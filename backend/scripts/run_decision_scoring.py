"""
Decision scoring layer (phase 1, non-breaking).

Purpose:
- Read active patterns from user_patterns.
- Compute decision score for SHOULD_SUGGEST.
- Print summary and optionally write JSON candidates.

Usage:
    python scripts/run_decision_scoring.py
    python scripts/run_decision_scoring.py --threshold 0.65 --write-json scripts/decision_candidates.json
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.apis.suggestions.service import SuggestionService

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/smarthome")
TZ = ZoneInfo("Asia/Ho_Chi_Minh")


@dataclass
class DecisionWeights:
    pattern_confidence: float = 0.30
    anomaly_severity: float = 0.25
    historical_acceptance: float = 0.15
    energy_saving_potential: float = 0.10
    user_preference: float = 0.10
    urgency: float = 0.10


PRIORITY_BASE_WEIGHT = {
    "ANOMALY": 3.0,
    "TIME_HABIT": 2.0,
    "CLUSTER": 1.0,
}


def priority_base_weight(pattern_type: str) -> float:
    return PRIORITY_BASE_WEIGHT.get(pattern_type, 0.5)


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def historical_acceptance_score(session: Session, user_id: str, lookback_days: int = 30) -> float:
    since = datetime.now(TZ) - timedelta(days=lookback_days)
    row = session.execute(
        text(
            """
            SELECT
                            COUNT(*) FILTER (WHERE fb.feedback_type IN ('ACCEPT', 'REJECT')) AS seen,
                            COUNT(*) FILTER (WHERE fb.feedback_type = 'ACCEPT') AS accepted
                        FROM suggestion_logs sl
                        LEFT JOIN suggestion_feedback_logs fb ON fb.suggestion_id = sl.id
                        WHERE sl.user_id = :uid
                            AND sl.created_at >= :since
            """
        ),
        {"uid": user_id, "since": since},
    ).fetchone()

    seen = int(row.seen or 0)
    accepted = int(row.accepted or 0)
    if seen == 0:
        return 0.5
    return clamp01(accepted / seen)


def anomaly_severity(pattern_type: str, pattern_data: dict) -> float:
    if pattern_type != "ANOMALY":
        return 0.2

    occ = float(pattern_data.get("occurrences", 1))
    threshold = float(pattern_data.get("threshold_min", pattern_data.get("threshold", 0)) or 0)
    avg = float(pattern_data.get("avg_dur_min", pattern_data.get("avg_dur", 0)) or 0)

    occ_score = clamp01(occ / 5.0)
    ratio_score = clamp01((threshold / max(avg, 1.0)) / 3.0) if avg > 0 else 0.6
    return clamp01(0.6 * occ_score + 0.4 * ratio_score)


def energy_saving_potential(device_id: str | None, pattern_type: str) -> float:
    if not device_id:
        return 0.3
    d = device_id.lower()

    if "ac" in d:
        base = 0.9
    elif "fan" in d:
        base = 0.6
    elif "light" in d:
        base = 0.4
    else:
        base = 0.3

    if pattern_type == "ANOMALY":
        base += 0.1

    return clamp01(base)


def urgency_score(pattern_type: str, pattern_data: dict) -> float:
    if pattern_type == "ANOMALY":
        occ = float(pattern_data.get("occurrences", 1))
        return clamp01(0.5 + occ / 10.0)
    if pattern_type == "TIME_HABIT":
        return 0.4
    if pattern_type == "CLUSTER":
        return 0.3
    return 0.2


def user_preference_proxy(pattern_type: str, hist_accept: float) -> float:
    # Simple proxy in phase 1: anomaly may be less preferred if acceptance is low.
    if pattern_type == "ANOMALY":
        return clamp01(0.4 + 0.6 * hist_accept)
    return clamp01(0.5 + 0.5 * hist_accept)


def device_duration_baseline(session: Session, home_id: str, device_id: str, lookback_days: int = 60) -> float:
    """Return average duration_seconds baseline for a device in a home."""
    since = datetime.now(TZ) - timedelta(days=lookback_days)
    row = session.execute(
        text(
            """
            SELECT AVG(duration_seconds) AS avg_dur
            FROM activity_logs
            WHERE home_id = :hid
              AND device_id = :did
              AND event_type = 'DEVICE_ON'
              AND duration_seconds IS NOT NULL
              AND duration_seconds > 0
              AND timestamp >= :since
            """
        ),
        {"hid": home_id, "did": device_id, "since": since},
    ).fetchone()
    return float(row.avg_dur or 0.0)


def is_energy_heavy_device(device_id: str | None) -> bool:
    if not device_id:
        return False
    d = device_id.lower()
    heavy_markers = ("ac", "heater", "water_heater", "boiler", "oven", "dryer")
    return any(m in d for m in heavy_markers)


def normalize_reason_keys(reason_keys: list[str] | tuple[str, ...] | None) -> list[str]:
    if not reason_keys:
        return []
    return sorted({str(reason).strip() for reason in reason_keys if str(reason).strip()})


def build_cooldown_signature(pattern_type: str, device_id: str | None, reason_keys: list[str]) -> str:
    normalized_device = (device_id or "unknown_device").lower()
    normalized_reasons = ",".join(normalize_reason_keys(reason_keys)) or "no_reason"
    return f"{pattern_type}:{normalized_device}:{normalized_reasons}"


def derive_cooldown_reason_keys(pattern_type: str, usefulness_reasons: list[str]) -> list[str]:
    if pattern_type == "ANOMALY":
        if "repeated_anomaly" in usefulness_reasons:
            return ["repeated_anomaly"]
        return ["single_anomaly"]

    keys = [
        reason
        for reason in (
            "duration_above_baseline",
            "energy_heavy_device",
            "unusual_hour",
            "high_weekly_repetition",
        )
        if reason in usefulness_reasons
    ]

    if pattern_type == "CLUSTER":
        return ["cluster"]

    return keys or ["unknown_reason"]


def is_critical_anomaly(pattern_type: str, device_id: str | None, usefulness_reasons: list[str], score_breakdown: dict) -> bool:
    if pattern_type != "ANOMALY":
        return False
    if not is_energy_heavy_device(device_id):
        return False
    if "repeated_anomaly" not in usefulness_reasons:
        return False
    severity = float(score_breakdown.get("anomaly_severity", 0.0))
    urgency = float(score_breakdown.get("urgency", 0.0))
    return severity >= 0.4 or urgency >= 0.7


def get_user_cooldown_history(session: Session, user_id: str, lookback_days: int = 7) -> list[dict]:
    since = datetime.now(TZ) - timedelta(days=lookback_days)
    rows = session.execute(
        text(
            """
            SELECT
                            sl.id,
                            sl.pattern_id,
                            fb.feedback_type::text AS feedback_type,
                            fb.feedback_reason,
                            fb.feedback_time,
                            sl.created_at AS suggestion_created_at,
                            sl.suggestion_json,
              up.pattern_type::text AS pattern_type,
              up.device_id
                        FROM suggestion_feedback_logs fb
                        JOIN suggestion_logs sl ON sl.id = fb.suggestion_id
                        LEFT JOIN user_patterns up ON up.id = sl.pattern_id
                        WHERE sl.user_id = CAST(:uid AS uuid)
                            AND fb.feedback_time >= :since
                        ORDER BY fb.feedback_time DESC, fb.id DESC
            """
        ),
        {"uid": user_id, "since": since},
    ).mappings().all()
    return [dict(row) for row in rows]


def cooldown_check(
    session: Session,
    user_id: str,
    pattern_type: str,
    device_id: str | None,
    usefulness_reasons: list[str],
    score_breakdown: dict,
    pattern_data: dict,
    history_cache: dict[str, list[dict]],
) -> tuple[bool, list[str], str]:
    """
    Cooldown policy:
      - same pattern signature: block for 48h
      - daily cap: max 2 suggestions/user/day
      - rejection-aware: rejected suggestion extends cooldown to 7 days
      - critical anomaly can bypass cooldown
    """
    reasons: list[str] = []
    now = datetime.now(TZ)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    today_count_row = session.execute(
        text(
            """
            SELECT COUNT(*) AS cnt
            FROM suggestion_logs
            WHERE user_id = CAST(:uid AS uuid)
              AND created_at >= :today_start
            """
        ),
        {"uid": user_id, "today_start": today_start},
    ).fetchone()
    today_count = int(today_count_row.cnt or 0)

    recent_history = history_cache.get(user_id)
    if recent_history is None:
        recent_history = get_user_cooldown_history(session, user_id)
        history_cache[user_id] = recent_history
    if today_count >= 2:
        reasons.append("daily_suggestion_cap")

    reason_keys = derive_cooldown_reason_keys(pattern_type, usefulness_reasons)
    cooldown_signature = build_cooldown_signature(pattern_type, device_id, reason_keys)

    if is_critical_anomaly(pattern_type, device_id, usefulness_reasons, score_breakdown):
        reasons.append("critical_anomaly_bypass")
        return True, reasons, cooldown_signature

    cooldown_hours = 48
    latest_same_signature_at = None

    for row in recent_history:
        row_pattern_type = row.get("pattern_type")
        row_device_id = row.get("device_id")
        row_payload = row.get("suggestion_json") or {}
        row_explanation = row_payload.get("explanation") or {}
        row_signature = row_explanation.get("cooldown_signature")

        if not row_signature:
            row_reason_keys = row_explanation.get("usefulness_reasons") or row_payload.get("usefulness_reasons") or []
            if not row_reason_keys:
                if row_pattern_type == "ANOMALY":
                    row_reason_keys = ["repeated_anomaly"]
                elif row_pattern_type == "TIME_HABIT":
                    row_reason_keys = [
                        reason
                        for reason in (
                            "duration_above_baseline",
                            "energy_heavy_device",
                            "unusual_hour",
                            "high_weekly_repetition",
                        )
                        if reason in row_explanation.get("priority_reason", [])
                    ]
            row_signature = build_cooldown_signature(str(row_pattern_type or pattern_type), row_device_id, list(row_reason_keys or []))

        if row_signature != cooldown_signature:
            continue

        latest_same_signature_at = row.get("feedback_time") or row.get("suggestion_created_at")
        if row.get("feedback_type") == "REJECT":
            cooldown_hours = 168
            reasons.append("rejected_previous_suggestion")
            break

    if latest_same_signature_at is not None:
        elapsed_hours = (now - latest_same_signature_at).total_seconds() / 3600.0
        if elapsed_hours < cooldown_hours:
            reasons.append("same_pattern_cooldown")
            return False, reasons, cooldown_signature

    if today_count >= 2:
        return False, reasons, cooldown_signature

    return True, reasons, cooldown_signature


def evaluate_usefulness(
    session: Session,
    pattern_type: str,
    pattern_data: dict,
    device_id: str | None,
    device_slug: str | None,
    home_id: str,
) -> tuple[bool, list[str]]:
    """
    Usefulness gate:
      - TIME_HABIT needs at least one A/B/C/D condition.
      - ANOMALY uses severity-friendly pass.
      - CLUSTER is informative only in phase-1, do not auto-suggest.
    """
    reasons: list[str] = []

    if pattern_type == "TIME_HABIT":
        avg_dur_min = float(pattern_data.get("avg_dur_min", 0) or 0)
        avg_dur_sec = avg_dur_min * 60.0
        occurrences = int(pattern_data.get("occurrences", 0) or 0)
        hour = int(pattern_data.get("hour", -1) or -1)

        # Rule A: duration much higher than device baseline.
        baseline_sec = device_duration_baseline(session, home_id, device_id or "") if device_id else 0.0
        if baseline_sec > 0 and avg_dur_sec > baseline_sec * 1.5:
            reasons.append("duration_above_baseline")

        # Rule B: energy-heavy device.
        if is_energy_heavy_device(device_slug):
            reasons.append("energy_heavy_device")

        # Rule C: unusual hour window.
        if hour in (23, 0, 1, 2, 3, 4, 5):
            reasons.append("unusual_hour")

        # Rule D: strong repeat frequency.
        if occurrences >= 4:
            reasons.append("high_weekly_repetition")

        return (len(reasons) > 0), reasons

    if pattern_type == "ANOMALY":
        occ = float(pattern_data.get("occurrences", 1) or 1)
        if occ >= 2:
            reasons.append("repeated_anomaly")
            return True, reasons
        reasons.append("single_anomaly")
        return True, reasons

    if pattern_type == "CLUSTER":
        reasons.append("cluster_is_informative_not_actionable")
        return False, reasons

    reasons.append("unknown_pattern_type")
    return False, reasons


def compute_priority_components(
    pattern_type: str,
    pattern_data: dict,
    device_id: str | None,
    score_breakdown: dict,
    usefulness_reasons: list[str],
) -> tuple[float, list[str], bool]:
    """
    Priority layer is separate from decision score.
    Output:
      - priority_score: for ranking only
      - priority_reason: explain why it ranks higher
      - hard_override: if True, force rank top.
    """
    reasons: list[str] = []
    boost = 0.0
    hard_override = False

    base = priority_base_weight(pattern_type)
    reasons.append(f"base_type_weight:{pattern_type}")

    # Score remains intact; priority only uses a ranking view.
    boost += float(score_breakdown.get("pattern_confidence", 0.0))
    reasons.append("pattern_confidence")

    if pattern_type == "ANOMALY":
        sev = float(score_breakdown.get("anomaly_severity", 0.0))
        urg = float(score_breakdown.get("urgency", 0.0))
        en = float(score_breakdown.get("energy_saving_potential", 0.0))
        boost += 1.2 * sev + 0.6 * urg + 0.6 * en

        if "repeated_anomaly" in usefulness_reasons:
            reasons.append("repeated_occurrence")
            boost += 0.8
        if en >= 0.8:
            reasons.append("high_energy_device")
            boost += 0.5
        if urg >= 0.7:
            reasons.append("high_urgency")
            boost += 0.3

        if en >= 0.8 and "repeated_anomaly" in usefulness_reasons:
            hard_override = True
            reasons.append("hard_override_anomaly_high_energy_repeated")

    elif pattern_type == "TIME_HABIT":
        # Still relevant, but only when usefulness says it matters.
        if "duration_above_baseline" in usefulness_reasons:
            boost += 0.6
            reasons.append("duration_above_baseline")
        if "energy_heavy_device" in usefulness_reasons:
            boost += 0.5
            reasons.append("high_energy_device")
        if "unusual_hour" in usefulness_reasons:
            boost += 0.4
            reasons.append("unusual_hour")
        if "high_weekly_repetition" in usefulness_reasons:
            boost += 0.3
            reasons.append("repeated_occurrence")

    elif pattern_type == "CLUSTER":
        boost += 0.1
        reasons.append("informative_cluster")

    priority_score = base + float(score_breakdown.get("pattern_confidence", 0.0)) + boost

    # Hard override lifts only the priority ordering, not the decision score.
    if hard_override:
        priority_score += 100.0

    return round(priority_score, 4), reasons, hard_override


def compute_score(weights: DecisionWeights, components: dict) -> float:
    score = (
        weights.pattern_confidence * components["pattern_confidence"]
        + weights.anomaly_severity * components["anomaly_severity"]
        + weights.historical_acceptance * components["historical_acceptance"]
        + weights.energy_saving_potential * components["energy_saving_potential"]
        + weights.user_preference * components["user_preference"]
        + weights.urgency * components["urgency"]
    )
    return clamp01(score)


def load_active_patterns(session: Session, home_id: str | None):
    sql = """
        SELECT
            up.id,
            up.user_id,
            up.home_id,
            up.device_id,
            d.slug AS device_slug,
            up.pattern_type,
            up.pattern_data,
            up.confidence,
            u.full_name,
            u.email
        FROM user_patterns up
        JOIN users u ON u.id = up.user_id
        LEFT JOIN devices d ON d.id = up.device_id
        WHERE up.is_active = true
    """
    params = {}
    if home_id:
        sql += " AND up.home_id = :home_id"
        params["home_id"] = home_id
    sql += " ORDER BY up.home_id, up.user_id, up.id"

    return session.execute(text(sql), params).fetchall()


def run_decision_scoring(home_id: str | None, threshold: float, write_json: str | None):
    engine = create_engine(DB_URL, echo=False)
    weights = DecisionWeights()

    with Session(engine) as session:
        rows = load_active_patterns(session, home_id)

        if not rows:
            print("No active patterns found.")
            return []

        results = []
        suggest_count = 0
        cooldown_history_cache: dict[str, list[dict]] = {}

        for r in rows:
            pdata = r.pattern_data or {}
            hist = historical_acceptance_score(session, str(r.user_id))

            comps = {
                "pattern_confidence": clamp01(float(r.confidence or 0.5)),
                "anomaly_severity": anomaly_severity(r.pattern_type, pdata),
                "historical_acceptance": hist,
                "energy_saving_potential": energy_saving_potential(r.device_slug, r.pattern_type),
                "user_preference": user_preference_proxy(r.pattern_type, hist),
                "urgency": urgency_score(r.pattern_type, pdata),
            }

            score = compute_score(weights, comps)
            usefulness, usefulness_reasons = evaluate_usefulness(
                session=session,
                pattern_type=r.pattern_type,
                pattern_data=pdata,
                device_id=r.device_id,
                device_slug=r.device_slug,
                home_id=str(r.home_id),
            )

            # Production rule: suggest only if both score and usefulness pass.
            should_suggest = (score >= threshold) and usefulness
            cooldown_pass = False
            cooldown_reasons: list[str] = []
            cooldown_signature = None
            if should_suggest:
                cooldown_pass, cooldown_reasons, cooldown_signature = cooldown_check(
                    session=session,
                    user_id=str(r.user_id),
                    pattern_type=r.pattern_type,
                    device_id=r.device_slug,
                    usefulness_reasons=usefulness_reasons,
                    score_breakdown=comps,
                    pattern_data=pdata,
                    history_cache=cooldown_history_cache,
                )
            
            # Determine blocked_by reason for audit log
            blocked_by = None
            if not usefulness:
                blocked_by = "USELESS"
            elif score < threshold:
                blocked_by = "LOW_SCORE"
            elif not cooldown_pass:
                blocked_by = cooldown_reasons[0] if cooldown_reasons else "COOLDOWN"

            should_suggest = should_suggest and cooldown_pass
            suggest_count += 1 if should_suggest else 0

            priority_score = None
            priority_reason = []
            hard_override = False
            if should_suggest:
                priority_score, priority_reason, hard_override = compute_priority_components(
                    pattern_type=r.pattern_type,
                    pattern_data=pdata,
                    device_id=r.device_slug,
                    score_breakdown=comps,
                    usefulness_reasons=usefulness_reasons,
                )

            # Log to audit table for Guardrail metrics
            SuggestionService.log_decision(
                session=session,
                pattern_id=int(r.id),
                home_id=str(r.home_id),
                user_id=str(r.user_id),
                decision_score=round(score, 4),
                should_suggest=should_suggest,
                blocked_by=blocked_by,
                cooldown_signature=cooldown_signature,
                metadata_json={
                    "usefulness_reasons": usefulness_reasons,
                    "cooldown_reasons": cooldown_reasons,
                    "score_breakdown": {k: round(v, 4) for k, v in comps.items()},
                    "priority_reason": priority_reason if should_suggest else []
                }
            )

            result = {
                "pattern_id": int(r.id),
                "home_id": str(r.home_id),
                "user_id": str(r.user_id),
                "user_email": r.email,
                "user_name": r.full_name,
                "device_id": r.device_id,
                "pattern_type": r.pattern_type,
                "threshold": threshold,
                "score": round(score, 4),
                "usefulness": usefulness,
                "usefulness_reasons": usefulness_reasons,
                "cooldown_pass": cooldown_pass,
                "cooldown_reasons": cooldown_reasons,
                "cooldown_signature": cooldown_signature,
                "should_suggest": should_suggest,
                "priority_score": priority_score,
                "priority_reason": priority_reason,
                "priority_hard_override": hard_override,
                "score_breakdown": {k: round(v, 4) for k, v in comps.items()},
            }
            results.append(result)

        # Final suggestion order should follow priority, not score.
        suggested = [r for r in results if r["should_suggest"]]
        suggested.sort(
            key=lambda x: (
                x["priority_score"] if x["priority_score"] is not None else -1,
                x["score"],
            ),
            reverse=True,
        )
        for idx, item in enumerate(suggested, start=1):
            item["priority_rank"] = idx

        for item in results:
            if not item["should_suggest"]:
                item["priority_rank"] = None

        # Keep output deterministic and easy to inspect.
        results.sort(
            key=lambda x: (
                1 if x["should_suggest"] else 0,
                x["priority_rank"] if x["priority_rank"] is not None else 9999,
                x["score"],
            ),
            reverse=True,
        )

        print("Decision scoring done")
        print(f"  Active patterns: {len(results)}")
        print(f"  Should suggest : {suggest_count}")
        print(f"  Skip           : {len(results) - suggest_count}")

        if write_json:
            out_path = Path(write_json)
            if not out_path.is_absolute():
                out_path = (Path(__file__).resolve().parents[1] / write_json).resolve()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"  Output JSON    : {out_path}")

        return results


def main():
    parser = argparse.ArgumentParser(description="Decision scoring layer (phase 1)")
    parser.add_argument("--home-id", default="", help="Optional home UUID to filter")
    parser.add_argument("--threshold", type=float, default=0.65, help="Suggest threshold [0,1]")
    parser.add_argument("--write-json", default="", help="Optional output JSON path")
    args = parser.parse_args()

    threshold = clamp01(args.threshold)
    home_id = args.home_id.strip() or None
    write_json = args.write_json.strip() or None

    run_decision_scoring(home_id=home_id, threshold=threshold, write_json=write_json)


if __name__ == "__main__":
    main()
