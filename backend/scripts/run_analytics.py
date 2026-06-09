"""
scripts/run_analytics.py  (hoặc src/tasks/analytics_tasks.py nếu dùng Celery)
=============================================================================
Chạy thủ công để dev/test:
    python scripts/run_analytics.py

Trong production, Celery beat gọi hàm run_full_pipeline() lúc 2h sáng.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.entities.models import (
    ActivityLog, UserPattern, User,
    EventType, TriggerSource, PatternType,
)

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/smarthome")
TZ     = ZoneInfo("Asia/Ho_Chi_Minh")

# ─── Ngưỡng tối thiểu để chạy analytics ─────────────────────────────────────
MIN_DAYS_RULE_BASED = 1    # Rule-based cần ít nhất 1 ngày
MAX_SESSION_DURATION_SECONDS = 24 * 60 * 60


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 0 - PREPROCESSING / DATA QUALITY GATE
#
# Production analytics does not rewrite raw activity_logs. Instead, this phase
# defines the data-quality contract used by all downstream mining queries:
#   - keep only attributed user/physical activity
#   - require user_id, device_id, timestamp
#   - keep supported event types
#   - reject negative or unrealistic session durations
# The ETL layer still owns CSV parsing, timestamp normalization and ON/OFF
# session pairing.
# ═══════════════════════════════════════════════════════════════════════════════

def duration_quality_predicate(alias: str = "") -> str:
    prefix = f"{alias}." if alias else ""
    return (
        f"({prefix}duration_seconds IS NULL OR "
        f"({prefix}duration_seconds >= 0 AND "
        f"{prefix}duration_seconds <= {MAX_SESSION_DURATION_SECONDS}))"
    )


def preprocess_activity_window(session: Session, home_id, lookback_days=60) -> dict:
    since = datetime.now(TZ) - timedelta(days=lookback_days)

    row = session.execute(text(f"""
        SELECT
            COUNT(*) AS total_rows,
            COUNT(*) FILTER (
                WHERE timestamp IS NULL
                   OR user_id IS NULL
                   OR device_id IS NULL
                   OR event_type NOT IN ('DEVICE_ON', 'DEVICE_OFF', 'FORGOT_OFF')
            ) AS missing_or_unsupported_rows,
            COUNT(*) FILTER (
                WHERE NOT {duration_quality_predicate()}
            ) AS invalid_duration_rows,
            COUNT(*) FILTER (
                WHERE trigger_source NOT IN ('USER', 'PHYSICAL_ATTRIBUTED')
            ) AS ignored_trigger_rows,
            COUNT(*) FILTER (
                WHERE timestamp IS NOT NULL
                  AND user_id IS NOT NULL
                  AND device_id IS NOT NULL
                  AND event_type IN ('DEVICE_ON', 'DEVICE_OFF', 'FORGOT_OFF')
                  AND trigger_source IN ('USER', 'PHYSICAL_ATTRIBUTED')
                  AND {duration_quality_predicate()}
            ) AS valid_rows
        FROM activity_logs
        WHERE home_id = :hid
          AND timestamp >= :since
    """), {"hid": str(home_id), "since": since}).mappings().one()

    return dict(row)


def print_preprocessing_summary(summary: dict):
    print(
        "  [Preprocessing] "
        f"valid={summary['valid_rows']}/{summary['total_rows']}, "
        f"missing_or_unsupported={summary['missing_or_unsupported_rows']}, "
        f"invalid_duration={summary['invalid_duration_rows']}, "
        f"ignored_trigger={summary['ignored_trigger_rows']}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — RULE-BASED HABIT MINER
#
# Ý tưởng: GROUP BY user_id, device_id, hour, weekday
# Nếu user bật thiết bị X lúc giờ H trong ít nhất N ngày → đó là thói quen.
#
# Output → user_patterns với pattern_type=TIME_HABIT
# ═══════════════════════════════════════════════════════════════════════════════

HABIT_MIN_OCCURRENCES = 3   # Mềm hơn để bắt thói quen khi dữ liệu có jitter giờ giấc

def mine_time_habits(session: Session, home_id, user_id, lookback_days=30) -> list[dict]:
    """
    Trả về list các time habit tìm được cho user này.
    Mỗi habit: {device_id, hour, days_of_week, avg_duration_min, occurrences, confidence}
    """
    since = datetime.now(TZ) - timedelta(days=lookback_days)

    rows = session.execute(text(f"""
        WITH base AS (
            SELECT
                device_id,
                EXTRACT(HOUR FROM timestamp AT TIME ZONE 'Asia/Ho_Chi_Minh')::int AS hour,
                EXTRACT(DOW  FROM timestamp AT TIME ZONE 'Asia/Ho_Chi_Minh')::int AS dow,
                duration_seconds
            FROM activity_logs
            WHERE home_id = :home_id
              AND user_id = :user_id
              AND event_type = 'DEVICE_ON'
              AND trigger_source IN ('USER', 'PHYSICAL_ATTRIBUTED')
              AND timestamp >= :since
              AND user_id IS NOT NULL
              AND device_id IS NOT NULL
              AND {duration_quality_predicate()}
        )
        SELECT
            device_id,
            hour,
            ARRAY_AGG(DISTINCT dow ORDER BY dow) AS dows,
            COUNT(*)                             AS cnt,
            AVG(duration_seconds) / 60.0         AS avg_dur_min
        FROM base
        GROUP BY device_id, hour
        HAVING COUNT(*) >= :min_occ
        ORDER BY cnt DESC, device_id, hour
    """), {
        "home_id":  str(home_id),
        "user_id":  str(user_id),
        "since":    since,
        "min_occ":  HABIT_MIN_OCCURRENCES,
    }).fetchall()

    habits = []
    for row in rows:
        device_id    = row.device_id
        hour         = int(row.hour)
        total_cnt    = int(row.cnt)
        avg_dur      = float(row.avg_dur_min or 0)
        days_of_week = [int(d) for d in (row.dows or [])]

        # confidence đơn giản theo tần suất thói quen trong cửa sổ lookback
        confidence = min(1.0, total_cnt / max(lookback_days * 0.35, 1))

        habits.append({
            "device_id":    device_id,
            "hour":         hour,
            "days_of_week": days_of_week,
            "avg_dur_min":  round(float(avg_dur), 1),
            "occurrences":  total_cnt,
            "confidence":   round(confidence, 2),
        })

    return habits


def save_time_habits(session: Session, home_id, user_id, habits: list[dict]):
    # Deactivate các pattern cũ của user này
    session.execute(text("""
        UPDATE user_patterns
        SET is_active = false
        WHERE user_id = :uid AND home_id = :hid AND pattern_type = 'TIME_HABIT'
    """), {"uid": str(user_id), "hid": str(home_id)})

    for h in habits:
        session.add(UserPattern(
            user_id=user_id,
            home_id=home_id,
            device_id=h["device_id"],
            pattern_type=PatternType.TIME_HABIT,
            pattern_data={
                "hour":         h["hour"],
                "days_of_week": h["days_of_week"],
                "avg_dur_min":  h["avg_dur_min"],
                "occurrences":  h["occurrences"],
                "label_vn":     f"Thường bật lúc {h['hour']}h",
            },
            confidence=h["confidence"],
        ))
    session.flush()
    print(f"    → {len(habits)} TIME_HABIT patterns cho user {user_id}")


# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY CLUSTER HELPERS (unused in runtime)
#
# Feature vector mỗi user (27 chiều):
#   h0..h23   (24): tần suất bật thiết bị theo giờ (normalized 0-1)
#   unique_devices (1): số thiết bị khác nhau đã dùng / tổng thiết bị
#   weekend_ratio  (1): tỷ lệ hoạt động cuối tuần
#   avg_duration   (1): avg duration_seconds / 3600 (quy về giờ)
#
# Lưu ý: train riêng cho từng home_id
#        chỉ dùng trigger_source IN ('USER', 'PHYSICAL_ATTRIBUTED')
# ═══════════════════════════════════════════════════════════════════════════════

CLUSTER_LABELS = {
    # (peak_hour < 9, weekend_ratio, night_ratio > 0.3)
    "morning_person":  "Dậy sớm — hoạt động nhiều buổi sáng",
    "night_owl":       "Cú đêm — hoạt động nhiều sau 21h",
    "home_daytime":    "Ở nhà ban ngày — hoạt động rải đều 9h-17h",
    "weekend_heavy":   "Chủ yếu cuối tuần",
    "irregular":       "Thất thường — không rõ pattern",
}

def extract_feature_vector(session: Session, home_id, user_id, lookback_days=60) -> np.ndarray | None:
    """Trả về vector 27 chiều cho user. None nếu không đủ data."""
    since = datetime.now(TZ) - timedelta(days=lookback_days)

    rows = session.execute(text(f"""
        SELECT
            EXTRACT(HOUR FROM al.timestamp AT TIME ZONE 'Asia/Ho_Chi_Minh')::int AS hour,
            EXTRACT(DOW  FROM al.timestamp AT TIME ZONE 'Asia/Ho_Chi_Minh')::int AS dow,
            d.slug AS device_slug,
            al.duration_seconds
        FROM activity_logs al
        JOIN devices d ON al.device_id = d.id
        WHERE al.home_id     = :hid
          AND al.user_id     = :uid
          AND al.event_type  = 'DEVICE_ON'
          AND al.trigger_source IN ('USER', 'PHYSICAL_ATTRIBUTED')
          AND al.timestamp  >= :since
          AND al.user_id IS NOT NULL
          AND al.device_id IS NOT NULL
          AND {duration_quality_predicate("al")}
    """), {"hid": str(home_id), "uid": str(user_id), "since": since}).fetchall()

    if len(rows) < 20:
        return None  # không đủ data

    # h0..h23: tần suất theo giờ
    hour_counts = np.zeros(24)
    weekend_count = 0
    total_count   = len(rows)
    devices_used  = set()
    durations     = []

    for r in rows:
        hour_counts[int(r.hour)] += 1
        if int(r.dow) in (0, 6):  # CN=0, T7=6 trong PostgreSQL DOW
            weekend_count += 1
        devices_used.add(r.device_slug)
        if r.duration_seconds:
            durations.append(r.duration_seconds)

    # Normalize
    hour_freq      = hour_counts / max(total_count, 1)
    unique_ratio   = len(devices_used) / len(DEVICES_DEF_IDS)
    weekend_ratio  = weekend_count / max(total_count, 1)
    avg_dur_hours  = (np.mean(durations) / 3600) if durations else 0

    vec = np.concatenate([
        hour_freq,
        [unique_ratio, weekend_ratio, avg_dur_hours],
    ])
    return vec

# Danh sách device id để tính unique_ratio
DEVICES_DEF_IDS = [
    "light_bedroom","fan_bedroom","ac_bedroom",
    "light_living","fan_living","ac_living","light_kitchen",
]

def label_cluster(centroid: np.ndarray) -> str:
    """Gán nhãn tiếng Việt cho cluster dựa theo centroid."""
    hour_freq     = centroid[:24]
    weekend_ratio = centroid[25]

    peak_hour  = int(np.argmax(hour_freq))
    night_sum  = hour_freq[21:24].sum() + hour_freq[0:3].sum()
    day_sum    = hour_freq[9:17].sum()

    if peak_hour < 9:
        return "morning_person"
    if night_sum > 0.30:
        return "night_owl"
    if day_sum > 0.50:
        return "home_daytime"
    if weekend_ratio > 0.55:
        return "weekend_heavy"
    return "irregular"


def run_kmeans(session: Session, home_id, user_ids: list, lookback_days=60, params: dict | None = None):
    """Train KMeans và lưu kết quả vào user_patterns."""
    try:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        print("  [SKIP KMeans] scikit-learn chưa cài: pip install scikit-learn")
        return

    vectors, valid_user_ids = [], []
    for uid in user_ids:
        vec = extract_feature_vector(session, home_id, uid, lookback_days)
        if vec is not None:
            vectors.append(vec)
            valid_user_ids.append(uid)

    if len(valid_user_ids) < MIN_USERS_KMEANS:
        print(f"  [SKIP KMeans] Chỉ có {len(valid_user_ids)} user đủ data (cần {MIN_USERS_KMEANS})")
        return

    X = np.array(vectors)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    params = params or {}
    requested_k = int(params.get("n_clusters", 3))
    n_clusters = max(2, min(len(valid_user_ids), requested_k))
    n_init = int(params.get("n_init", 10))
    max_iter = int(params.get("max_iter", 300))
    random_state = int(params.get("random_state", 42))

    km = KMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        n_init=n_init,
        max_iter=max_iter,
    )
    labels = km.fit_predict(X_scaled)

    # Deactivate CLUSTER patterns cũ
    for uid in valid_user_ids:
        session.execute(text("""
            UPDATE user_patterns
            SET is_active = false
            WHERE user_id = :uid AND home_id = :hid AND pattern_type = 'CLUSTER'
        """), {"uid": str(uid), "hid": str(home_id)})

    for uid, label_idx, vec in zip(valid_user_ids, labels, vectors):
        centroid    = km.cluster_centers_[label_idx]
        # Inverse transform để đọc được ý nghĩa
        centroid_orig = scaler.inverse_transform([centroid])[0]
        cluster_name  = label_cluster(centroid_orig)
        peak_hour     = int(np.argmax(vec[:24]))

        session.add(UserPattern(
            user_id=uid,
            home_id=home_id,
            device_id=None,  # cluster pattern không gắn với device cụ thể
            pattern_type=PatternType.CLUSTER,
            pattern_data={
                "cluster_id":   int(label_idx),
                "cluster_name": cluster_name,
                "label_vn":     CLUSTER_LABELS.get(cluster_name, cluster_name),
                "peak_hour":    peak_hour,
                "weekend_ratio":round(float(vec[25]), 2),
                "avg_dur_hours":round(float(vec[26]), 2),
            },
            confidence=0.85,
        ))

    session.flush()
    print(f"    → KMeans k={n_clusters}, n_init={n_init}, users={len(valid_user_ids)}")


def run_dbscan(session: Session, home_id, user_ids: list, lookback_days=60, params: dict | None = None):
    """Train DBSCAN và lưu kết quả vào user_patterns (pattern_type=CLUSTER)."""
    try:
        from sklearn.cluster import DBSCAN
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        print("  [SKIP DBSCAN] scikit-learn chưa cài: pip install scikit-learn")
        return

    vectors, valid_user_ids = [], []
    for uid in user_ids:
        vec = extract_feature_vector(session, home_id, uid, lookback_days)
        if vec is not None:
            vectors.append(vec)
            valid_user_ids.append(uid)

    if len(valid_user_ids) < MIN_USERS_KMEANS:
        print(f"  [SKIP DBSCAN] Chỉ có {len(valid_user_ids)} user đủ data (cần {MIN_USERS_KMEANS})")
        return

    params = params or {}
    eps = float(params.get("eps", 0.5))
    min_samples = int(params.get("min_samples", 5))

    X = np.array(vectors)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    db = DBSCAN(eps=eps, min_samples=min_samples)
    labels = db.fit_predict(X_scaled)

    unique_clusters = sorted([int(x) for x in set(labels) if int(x) != -1])
    noise_ratio = float(np.mean(labels == -1)) if len(labels) > 0 else 1.0

    cluster_centroids_scaled = {}
    for cid in unique_clusters:
        member_idx = np.where(labels == cid)[0]
        if len(member_idx) > 0:
            cluster_centroids_scaled[cid] = np.mean(X_scaled[member_idx], axis=0)

    for uid in valid_user_ids:
        session.execute(text("""
            UPDATE user_patterns
            SET is_active = false
            WHERE user_id = :uid AND home_id = :hid AND pattern_type = 'CLUSTER'
        """), {"uid": str(uid), "hid": str(home_id)})

    for uid, label_idx, vec in zip(valid_user_ids, labels, vectors):
        cluster_id = int(label_idx)

        if cluster_id == -1:
            cluster_name = "irregular"
            label_vn = "Ngoai le cum (noise)"
            confidence = max(0.5, 0.8 - noise_ratio)
        else:
            centroid_scaled = cluster_centroids_scaled.get(cluster_id)
            if centroid_scaled is None:
                cluster_name = "irregular"
            else:
                centroid_orig = scaler.inverse_transform([centroid_scaled])[0]
                cluster_name = label_cluster(centroid_orig)
            label_vn = CLUSTER_LABELS.get(cluster_name, cluster_name)
            confidence = max(0.7, 1.0 - noise_ratio)

        peak_hour = int(np.argmax(vec[:24]))

        session.add(UserPattern(
            user_id=uid,
            home_id=home_id,
            device_id=None,
            pattern_type=PatternType.CLUSTER,
            pattern_data={
                "cluster_id": cluster_id,
                "cluster_name": cluster_name,
                "label_vn": label_vn,
                "peak_hour": peak_hour,
                "weekend_ratio": round(float(vec[25]), 2),
                "avg_dur_hours": round(float(vec[26]), 2),
                "noise_ratio": round(noise_ratio, 3),
                "model": "DBSCAN",
            },
            confidence=round(float(confidence), 2),
        ))

    session.flush()
    print(
        f"    → DBSCAN eps={eps}, min_samples={min_samples}, "
        f"clusters={len(unique_clusters)}, noise_ratio={noise_ratio:.2f}, users={len(valid_user_ids)}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — ANOMALY DETECTOR
#
# Phát hiện: thiết bị bật lâu hơn avg ×2 → FORGOT_OFF
# Ghi vào user_patterns với pattern_type=ANOMALY
# ═══════════════════════════════════════════════════════════════════════════════

def detect_anomalies(session: Session, home_id, user_id, lookback_days=30) -> list[dict]:
    since = datetime.now(TZ) - timedelta(days=lookback_days)

    rows = session.execute(text(f"""
        SELECT
            device_id,
            AVG(duration_seconds)    AS avg_dur,
            STDDEV(duration_seconds) AS std_dur,
            COUNT(*)                 AS cnt
        FROM activity_logs
        WHERE home_id     = :hid
          AND user_id     = :uid
          AND event_type  = 'DEVICE_ON'
          AND duration_seconds IS NOT NULL
          AND {duration_quality_predicate()}
          AND timestamp  >= :since
        GROUP BY device_id
        HAVING COUNT(*) >= 5
    """), {"hid": str(home_id), "uid": str(user_id), "since": since}).fetchall()

    anomalies = []
    for r in rows:
        avg_dur_float = float(r.avg_dur or 0)
        std_dur_float = float(r.std_dur or 0)
        threshold = avg_dur_float + 2 * std_dur_float

        # Lấy các lần bật thực sự lâu hơn ngưỡng
        outliers = session.execute(text(f"""
            SELECT timestamp, duration_seconds
            FROM activity_logs
            WHERE home_id     = :hid
              AND user_id     = :uid
              AND device_id   = :did
              AND event_type  = 'DEVICE_ON'
              AND {duration_quality_predicate()}
              AND duration_seconds > :thresh
              AND timestamp  >= :since
            ORDER BY timestamp DESC
            LIMIT 5
        """), {
            "hid":   str(home_id),
            "uid":   str(user_id),
            "did":   r.device_id,
            "thresh": threshold,
            "since": since,
        }).fetchall()

        if outliers:
            anomalies.append({
                "device_id":    r.device_id,
                "avg_dur_min":  round(avg_dur_float / 60, 1),
                "threshold_min":round(threshold / 60, 1),
                "occurrences":  len(outliers),
            })

    return anomalies


def save_anomalies(session: Session, home_id, user_id, anomalies: list[dict]):
    session.execute(text("""
        UPDATE user_patterns SET is_active = false
        WHERE user_id = :uid AND home_id = :hid AND pattern_type = 'ANOMALY'
    """), {"uid": str(user_id), "hid": str(home_id)})

    for a in anomalies:
        session.add(UserPattern(
            user_id=user_id,
            home_id=home_id,
            device_id=a["device_id"],
            pattern_type=PatternType.ANOMALY,
            pattern_data={
                "avg_dur_min":   a["avg_dur_min"],
                "threshold_min": a["threshold_min"],
                "occurrences":   a["occurrences"],
                "label_vn":      f"Có thể quên tắt (avg {a['avg_dur_min']} phút, vượt ngưỡng {a['occurrences']} lần)",
            },
            confidence=min(1.0, a["occurrences"] / 5),
        ))
    session.flush()
    print(f"    → {len(anomalies)} ANOMALY patterns")


# ═══════════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════════

def run_full_pipeline(session: Session = None):
    """Entry point cho cả Celery task lẫn chạy thủ công."""
    should_close = session is None
    if session is None:
        engine  = create_engine(DB_URL, echo=False)
        session = Session(engine)

    try:
        with session.begin():
            # Lấy tất cả home đang active
            homes = session.execute(text(
                "SELECT id FROM homes WHERE is_active = true"
            )).fetchall()

            for home_row in homes:
                home_id = home_row[0]
                print(f"\n── Home {home_id} ──")

                users = session.execute(text("""
                    SELECT u.id, u.email
                    FROM users u
                    JOIN home_users hu ON hu.user_id = u.id
                    WHERE hu.home_id = :hid AND u.is_active = true
                """), {"hid": str(home_id)}).fetchall()

                user_ids = [u[0] for u in users]

                # Kiểm tra đủ data chưa
                oldest = session.execute(text("""
                    SELECT MIN(timestamp) FROM activity_logs WHERE home_id = :hid
                """), {"hid": str(home_id)}).scalar()

                if not oldest:
                    print("  [SKIP] Không có data")
                    continue

                days_available = (datetime.now(TZ) - oldest.replace(tzinfo=TZ)).days
                print(f"  Data: {days_available} ngày / {len(users)} users")
                preprocessing_summary = preprocess_activity_window(session, home_id, lookback_days=60)
                print_preprocessing_summary(preprocessing_summary)

                if preprocessing_summary["valid_rows"] == 0:
                    print("  [SKIP] Không có dữ liệu hợp lệ sau preprocessing")
                    continue

                for user_row in users:
                    uid, email = user_row[0], user_row[1]
                    print(f"\n  User: {email}")

                    if days_available >= MIN_DAYS_RULE_BASED:
                        print("  [Rule-based]")
                        habits = mine_time_habits(session, home_id, uid, lookback_days=30)
                        save_time_habits(session, home_id, uid, habits)

                        print("  [Anomaly]")
                        anomalies = detect_anomalies(session, home_id, uid, lookback_days=30)
                        save_anomalies(session, home_id, uid, anomalies)

    finally:
        if should_close:
            session.close()


if __name__ == "__main__":
    print("Chạy analytics pipeline...")
    run_full_pipeline()
    print("\n✓ Xong! Kiểm tra bảng user_patterns trong DB.")
    print("Bước tiếp theo:")
    print("  python scripts/run_llm_formatter.py")
