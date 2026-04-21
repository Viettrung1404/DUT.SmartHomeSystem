"""
scripts/seed_data.py  —  v3  (full noise model)
================================================
Noise taxonomy được implement:

  TEMPORAL NOISE
    - Hùng về muộn 21-22h (~20% ngày T2-T6)
    - Hùng WFH bất ngờ: thói quen sáng thay đổi hoàn toàn (~10% T2-T6)
    - Thức khuya xem phim: cả 2 bật TV/AC đến 1-2h sáng (~8%/tuần)
    - Ốm: nằm cả ngày, chỉ bật 1-2 thiết bị yếu (~3%/tháng)
    - Mất ngủ: bật đèn 2-4h sáng (~5%)

  MISSING DATA
    - Cúp điện: gap 2-6h không có log (~4%/tháng)
    - MQTT timeout: ON log có nhưng mất OFF log → duration NULL (~8%)
    - Đi vắng dài: 2-4 ngày liên tiếp không có gì (~1 lần/tháng)

  BEHAVIORAL NOISE (Mai-specific)
    - Deadline: thức đến 1-3h sáng làm việc (~15% T2-T5)
    - Đổi "văn phòng": hôm phòng ngủ, hôm phòng khách (~30%)
    - Thứ 6 đi cà phê sáng: không có log buổi sáng (~40% T6)
    - Ngủ trưa skip hoàn toàn (~30% ngày T2-T6)
    - Ngủ trưa đúng giờ nhưng rất dài (~15%: 2-3h thay vì 70 phút)

  DEVICE INTERACTION NOISE
    - Bật-tắt ngay < 2 phút (nhấn nhầm) (~5% habit)
    - Nhấn 2 lần liên tiếp cùng device (double-trigger) (~3%)
    - Ghost event từ MQTT: bật lúc không ai ở nhà (~2%/ngày)
    - Tắt rồi bật lại sau 5 phút (forgot something) (~4%)

Chạy:
    python scripts/seed_data.py [--days 60] [--drop]
"""

import argparse
import random
import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.entities.models import (
    Home, HomeUser, Room, Device, User, DeviceState,
    ActivityLog, SensorData, UserPresence,
    DeviceType, UserRole, EventType, TriggerSource, MetricType,
)

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/smarthome")
try:
    TZ = ZoneInfo("Asia/Ho_Chi_Minh")
except ZoneInfoNotFoundError:
    # Fallback when tzdata is missing on Windows environments.
    TZ = ZoneInfo("UTC")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def maybe(prob: float) -> bool:
    return random.random() < prob

def local_dt(base_date, hour: int, minute: int = 0) -> datetime:
    return datetime(
        base_date.year, base_date.month, base_date.day,
        max(0, min(23, int(hour) % 24)),
        max(0, min(59, int(minute) % 60)),
        tzinfo=TZ,
    )

def gauss_min(center_h: int, center_m: int, sigma: int = 10):
    """(hour, minute) với Gaussian noise."""
    total = center_h * 60 + center_m + int(random.gauss(0, sigma))
    total = max(0, min(23 * 60 + 59, total))
    return total // 60, total % 60

def rand_duration(base_min: int, sigma_ratio: float = 0.15) -> int:
    """Duration có nhiễu Gaussian, tối thiểu 5 phút."""
    return max(5, int(random.gauss(base_min, base_min * sigma_ratio)))


# ═══════════════════════════════════════════════════════════════════════════════
# HABIT DEFINITIONS
#
# (device_id, hour, minute, duration_min, days_of_week, base_prob, sigma_min)
#  base_prob: xác suất ngày "normal" — ngày disrupted/anomaly sẽ nhân thêm hệ số
#  sigma_min: độ lệch chuẩn jitter giờ giấc (phút)
# ═══════════════════════════════════════════════════════════════════════════════

HUNG_HABITS = [
    # ── Sáng T2-T6 ────────────────────────────────────────────────────────────
    ("light_bedroom",  6,  0,  45, [0,1,2,3,4], 0.72, 12),
    ("fan_bedroom",    6,  5,  40, [0,1,2,3,4], 0.68, 10),
    ("light_kitchen",  6, 30,  25, [0,1,2,3,4], 0.70, 15),
    ("light_bedroom",  7, 15,   0, [0,1,2,3,4], 0.75, 10),  # tắt đèn đi làm
    ("light_kitchen",  7, 20,   0, [0,1,2,3,4], 0.73, 10),

    # ── Sáng cuối tuần ────────────────────────────────────────────────────────
    ("light_bedroom",  7, 45,  60, [5,6], 0.70, 20),
    ("fan_bedroom",    8,  0,  50, [5,6], 0.65, 18),
    ("light_kitchen",  8, 30,  40, [5,6], 0.72, 15),
    ("fan_living",     9,  0, 120, [5,6], 0.60, 20),

    # ── Tối T2-T6 ─────────────────────────────────────────────────────────────
    ("light_living",  18,  0, 180, [0,1,2,3,4], 0.75, 20),
    ("fan_living",    18, 10, 170, [0,1,2,3,4], 0.70, 15),
    ("light_kitchen", 19,  0,  50, [0,1,2,3,4], 0.72, 15),
    ("ac_living",     20,  0, 120, [2,3,4,5,6], 0.65, 20),
    ("light_bedroom", 22, 30,  50, [0,1,2,3,4], 0.70, 15),
    ("ac_bedroom",    22, 35,  85, [0,1,2,3,4], 0.68, 12),
    ("light_living",  22, 55,   0, [0,1,2,3,4], 0.72, 10),
    ("light_bedroom", 23,  5,   0, [0,1,2,3,4], 0.75, 10),

    # ── Tối cuối tuần ─────────────────────────────────────────────────────────
    ("light_living",  18, 30, 240, [5,6], 0.72, 20),
    ("ac_living",     19,  0, 180, [5,6], 0.68, 20),
    ("light_bedroom", 23, 30,  60, [5,6], 0.70, 15),
    ("ac_bedroom",    23, 40,  90, [5,6], 0.65, 15),
]

MAI_HABITS = [
    # ── Sáng ──────────────────────────────────────────────────────────────────
    # Thấp hơn Hùng vì hay đi cà phê T6, deadline thức khuya nên dậy muộn
    ("light_bedroom",  6, 30,  30, None,        0.62, 15),
    ("light_kitchen",  7,  0,  40, [0,1,2,3,4], 0.60, 18),
    ("light_kitchen",  8, 30,  60, [5,6],       0.68, 18),

    # ── Ban ngày T2-T6 (freelance ở nhà) ──────────────────────────────────────
    # prob thấp vì hay đổi phòng làm việc + T6 đi cà phê
    ("light_living",   9,  0, 240, [0,1,2,3,4], 0.55, 25),
    ("fan_living",     9, 10, 230, [0,1,2,3,4], 0.52, 22),
    ("light_kitchen", 10, 30,  15, [0,1,2,3,4], 0.45, 25),   # cà phê: rất hay bỏ qua
    ("light_kitchen", 11, 30,  45, [0,1,2,3,4], 0.65, 18),

    # Ngủ trưa: prob thấp (hay skip), jitter cao (giờ không cố định)
    ("fan_bedroom",   13,  0,  70, [0,1,2,3,4], 0.52, 35),
    ("ac_bedroom",    13,  5,  65, [0,1,2,3,4], 0.35, 35),   # điều hoà trưa: rất thất thường

    # Chiều làm việc: hay dùng phòng ngủ thay phòng khách (đổi chỗ)
    ("light_living",  14, 30, 150, [0,1,2,3,4], 0.50, 28),
    ("fan_living",    14, 35, 140, [0,1,2,3,4], 0.48, 25),
    ("light_bedroom", 14, 30, 150, [0,1,2,3,4], 0.45, 30),   # làm ở phòng ngủ thay thế
    ("fan_bedroom",   14, 35, 140, [0,1,2,3,4], 0.42, 28),

    # Nấu ăn tối ~17h
    ("light_kitchen", 17,  0,  60, [0,1,2,3,4], 0.70, 15),

    # ── Tối T2-T6 ─────────────────────────────────────────────────────────────
    ("fan_living",    19, 30, 100, [0,1,2,3,4], 0.58, 22),
    ("light_bedroom", 21, 30,  30, [0,1,2,3,4], 0.65, 18),
    ("fan_bedroom",   21, 35,  25, [0,1,2,3,4], 0.60, 15),
    ("light_bedroom", 22,  0,   0, [0,1,2,3,4], 0.68, 12),   # tắt đèn ngủ

    # ── Cuối tuần (ở nhà nhiều hơn, prob tăng lên) ────────────────────────────
    ("light_living",   9, 30, 300, [5,6], 0.72, 20),
    ("fan_living",     9, 40, 290, [5,6], 0.70, 20),
    ("ac_living",     14,  0, 120, [5,6], 0.55, 28),
    ("light_bedroom", 22, 30,  30, [5,6], 0.65, 15),
    ("ac_bedroom",    22, 40,  80, [5,6], 0.58, 15),
]

PERSONAS = [
    {
        "name": "Nguyễn Văn Hùng", "email": "hung@demo.local",
        "password_hash": "$2b$12$FAKEHASH_HUNG", "role": UserRole.ADMIN,
        "habits": HUNG_HABITS,
        "forget_off": [
            ("fan_living",    0.08, 120, 240),
            ("light_kitchen", 0.06,  60, 180),
        ],
    },
    {
        "name": "Trần Thị Mai", "email": "mai@demo.local",
        "password_hash": "$2b$12$FAKEHASH_MAI", "role": UserRole.MEMBER,
        "habits": MAI_HABITS,
        "forget_off": [
            ("fan_bedroom",  0.12, 120, 360),  # hay quên quạt sau ngủ trưa
            ("light_living", 0.08,  60, 180),
            ("ac_bedroom",   0.10,  90, 240),  # hay quên tắt điều hoà phòng ngủ
        ],
    },
]

ROOMS_DEF = [
    {"name": "Phòng ngủ",   "icon": "bed"},
    {"name": "Phòng khách", "icon": "sofa"},
    {"name": "Bếp",         "icon": "kitchen"},
]

DEVICES_DEF = [
    ("light_bedroom", "Đèn phòng ngủ",        DeviceType.LIGHT, "Phòng ngủ"),
    ("fan_bedroom",   "Quạt phòng ngủ",        DeviceType.FAN,   "Phòng ngủ"),
    ("ac_bedroom",    "Điều hoà phòng ngủ",    DeviceType.AC,    "Phòng ngủ"),
    ("light_living",  "Đèn phòng khách",       DeviceType.LIGHT, "Phòng khách"),
    ("fan_living",    "Quạt phòng khách",      DeviceType.FAN,   "Phòng khách"),
    ("ac_living",     "Điều hoà phòng khách",  DeviceType.AC,    "Phòng khách"),
    ("light_kitchen", "Đèn bếp",               DeviceType.LIGHT, "Bếp"),
]
DEVICE_IDS = [d[0] for d in DEVICES_DEF]


# ═══════════════════════════════════════════════════════════════════════════════
# LOG BUILDER — hàm dùng chung
# ═══════════════════════════════════════════════════════════════════════════════

def on_off(date, uid, hid, dev_id, h, m, dur_min,
           trigger=TriggerSource.USER, is_forgot=False,
           drop_off_prob=0.0) -> list:
    """
    Tạo cặp ON + OFF.
    drop_off_prob: xác suất mất OFF log (simulate MQTT timeout).
    is_forgot    : đánh dấu FORGOT_OFF thay vì DEVICE_ON.
    dur_min == 0 : đây là lệnh TẮT thuần (chỉ tạo OFF).
    """
    logs = []
    if dur_min == 0:
        logs.append(ActivityLog(
            timestamp=local_dt(date, h, m),
            event_type=EventType.DEVICE_OFF,
            trigger_source=trigger,
            device_id=dev_id, user_id=uid, home_id=hid,
            duration_seconds=0,
        ))
        return logs

    actual = rand_duration(dur_min)
    start  = local_dt(date, h, m)
    end    = start + timedelta(minutes=actual)

    on_type = EventType.FORGOT_OFF if is_forgot else EventType.DEVICE_ON

    # Missing OFF log: duration_seconds = NULL để simulate mất session_end
    has_off = not maybe(drop_off_prob)

    logs.append(ActivityLog(
        timestamp=start,
        event_type=on_type,
        trigger_source=trigger,
        device_id=dev_id, user_id=uid, home_id=hid,
        session_end=end    if has_off else None,
        duration_seconds=actual * 60 if has_off else None,
    ))
    if has_off and not is_forgot:
        logs.append(ActivityLog(
            timestamp=end,
            event_type=EventType.DEVICE_OFF,
            trigger_source=trigger,
            device_id=dev_id, user_id=uid, home_id=hid,
            duration_seconds=0,
        ))
    return logs


# ═══════════════════════════════════════════════════════════════════════════════
# NOISE GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

# ── 1. Device interaction noise: nhấn nhầm, double-trigger, ghost event ───────

def device_interaction_noise(date, uid, hid) -> list:
    """Xác suất mỗi ngày: ~15% có ít nhất 1 loại interaction noise."""
    logs = []

    # Bật-tắt ngay < 2 phút (nhấn nhầm kiểm tra)
    if maybe(0.08):
        dev = random.choice(["light_living", "fan_living", "light_bedroom"])
        h   = random.randint(8, 22)
        m   = random.randint(0, 59)
        logs += on_off(date, uid, hid, dev, h, m, dur_min=random.randint(1, 3))

    # Double-trigger: bật 2 lần liên tiếp cùng device trong 3 phút
    if maybe(0.05):
        dev = random.choice(DEVICE_IDS)
        h   = random.randint(7, 21)
        m   = random.randint(0, 55)
        logs += on_off(date, uid, hid, dev, h, m, dur_min=random.randint(5, 15))
        logs += on_off(date, uid, hid, dev, h, m + random.randint(2, 5),
                       dur_min=random.randint(20, 60))

    # Tắt rồi bật lại sau 5 phút (forgot something → quay lại)
    if maybe(0.06):
        dev  = random.choice(["light_kitchen", "fan_living", "ac_bedroom"])
        h    = random.randint(18, 22)
        m    = random.randint(0, 50)
        dur1 = random.randint(30, 90)
        logs += on_off(date, uid, hid, dev, h, m, dur_min=dur1)
        gap  = dur1 + random.randint(5, 15)
        logs += on_off(date, uid, hid, dev, h, (m + gap) % 60,
                       dur_min=random.randint(20, 60))

    # Ghost event: bật khi không ai ở nhà (PHYSICAL_UNKNOWN)
    if maybe(0.04):
        dev = random.choice(["fan_living", "light_living", "ac_living"])
        h   = random.randint(9, 17)
        m   = random.randint(0, 59)
        logs += on_off(date, uid, hid, dev, h, m,
                       dur_min=random.randint(10, 40),
                       trigger=TriggerSource.PHYSICAL_UNKNOWN)

    return logs


# ── 2. Missing data: cúp điện, MQTT timeout ───────────────────────────────────

def apply_mqtt_dropout(logs: list, dropout_prob: float = 0.08) -> list:
    """
    Với mỗi ON log, có dropout_prob% mất OFF → set session_end=None.
    Simulate MQTT mất kết nối giữa chừng.
    """
    result = []
    skip_ids = set()

    for log in logs:
        if log.event_type == EventType.DEVICE_OFF:
            # Tìm ON log tương ứng để quyết định có skip OFF không
            result.append(log)
            continue

        if log.event_type == EventType.DEVICE_ON and maybe(dropout_prob):
            # Mất OFF: xoá session_end, duration
            log.session_end      = None
            log.duration_seconds = None
            skip_ids.add(id(log))

        result.append(log)

    # Xoá các OFF log của ON bị dropout (cần match bằng device + timestamp)
    # Đơn giản hoá: chỉ drop OFF log ngay sau ON bị dropout
    filtered, drop_next = [], False
    for log in result:
        if log.event_type == EventType.DEVICE_ON and id(log) in skip_ids:
            drop_next = True
            filtered.append(log)
        elif log.event_type == EventType.DEVICE_OFF and drop_next:
            drop_next = False  # skip OFF này
        else:
            drop_next = False
            filtered.append(log)

    return filtered


def power_outage_gap(date, home_id) -> tuple[datetime, datetime] | None:
    """
    Trả về (start, end) của khoảng cúp điện, hoặc None.
    Xác suất ~4%/ngày, kéo dài 2-6h.
    """
    if maybe(0.04):
        h_start = random.randint(10, 20)
        h_end   = h_start + random.randint(2, 6)
        return (local_dt(date, h_start), local_dt(date, min(h_end, 23)))
    return None


def filter_outage(logs: list, outage: tuple | None) -> list:
    """Xoá log trong khoảng cúp điện."""
    if not outage:
        return logs
    s, e = outage
    return [l for l in logs if not (s <= l.timestamp <= e)]


# ── 3. Temporal noise: WFH, thức khuya, ốm, mất ngủ ─────────────────────────

def wfh_day_logs(date, uid, hid, weekday) -> list:
    """
    Hùng WFH: không đi làm, ở nhà cả ngày.
    Thói quen sáng thay đổi hoàn toàn — không dậy 6h nữa.
    """
    if weekday not in [0,1,2,3,4]:
        return []
    logs = []
    # Dậy muộn ~8-9h
    h, m = gauss_min(8, 30, 30)
    logs += on_off(date, uid, hid, "light_bedroom", h, m, 40)
    logs += on_off(date, uid, hid, "light_kitchen", h + 1, m, 35)
    # Làm việc ở phòng khách cả ngày (giống Mai)
    logs += on_off(date, uid, hid, "light_living",  9, 30, 300)
    logs += on_off(date, uid, hid, "fan_living",    9, 40, 280)
    logs += on_off(date, uid, hid, "light_kitchen", 12, 0,  40)
    # Tối bình thường
    logs += on_off(date, uid, hid, "ac_living",    19, 0, 150)
    logs += on_off(date, uid, hid, "light_bedroom",22, 0,  50)
    logs += on_off(date, uid, hid, "ac_bedroom",   22,10,  80)
    return logs


def late_night_movie(date, uid, hid) -> list:
    """Thức khuya xem phim: cả 2 bật đèn/AC đến 1-2h sáng."""
    logs = []
    end_h = random.randint(1, 3)
    # Bật AC phòng khách từ 21h, kéo dài đến 1-2h
    dur = (end_h + 24 - 21) * 60 + random.randint(-20, 20)
    logs += on_off(date, uid, hid, "ac_living",   21, 0, max(60, dur))
    logs += on_off(date, uid, hid, "light_living", 21, 0, max(60, dur - 10))
    return logs


def sick_day_logs(date, uid, hid) -> list:
    """Ốm: nằm phòng ngủ cả ngày, chỉ bật quạt + đèn yếu."""
    logs = []
    logs += on_off(date, uid, hid, "fan_bedroom",   8, 0, 600,
                   drop_off_prob=0.3)   # hay quên tắt vì ngủ liên tục
    logs += on_off(date, uid, hid, "light_bedroom", 8,30,  30)
    # Vào bếp lấy nước 1-2 lần
    for _ in range(random.randint(1, 2)):
        h = random.randint(10, 15)
        logs += on_off(date, uid, hid, "light_kitchen", h, random.randint(0,59), 5)
    return logs


def insomnia_logs(date, uid, hid) -> list:
    """Mất ngủ: bật đèn 2-4h sáng, loay hoay 30-60 phút."""
    h = random.randint(2, 4)
    logs = []
    logs += on_off(date, uid, hid, "light_bedroom", h, 0, random.randint(20, 60))
    if maybe(0.4):
        logs += on_off(date, uid, hid, "light_kitchen", h, 15, 15)  # lấy nước
    return logs


# ── 4. Mai-specific behavioral noise ─────────────────────────────────────────

def mai_deadline_night(date, uid, hid, weekday) -> list:
    """
    Mai deadline: thức đến 1-3h sáng làm việc.
    Bật đèn phòng ngủ (làm ở bàn trong phòng) từ 22h → 1-3h sáng.
    """
    if weekday not in [0,1,2,3]:   # T2-T5 hay có deadline
        return []
    logs = []
    end_h  = random.randint(1, 3)
    dur    = (end_h + 24 - 22) * 60
    logs += on_off(date, uid, hid, "light_bedroom", 22, 0, max(60, dur))
    logs += on_off(date, uid, hid, "fan_bedroom",   22, 5, max(55, dur - 5))
    # Không ngủ trưa hôm sau (handled by lowered prob in habits)
    return logs


def mai_cafe_morning(date, uid, hid) -> list:
    """
    Mai đi cà phê buổi sáng T6: không có log sáng sớm.
    Trả về empty (thói quen sáng T6 bị skip hoàn toàn).
    Chỉ có log từ chiều: về nhà ~14-15h.
    """
    logs = []
    h, m = gauss_min(14, 30, 20)
    logs += on_off(date, uid, hid, "light_living",  h, m,      120)
    logs += on_off(date, uid, hid, "fan_living",    h, m + 5,  115)
    logs += on_off(date, uid, hid, "light_kitchen", h + 2, 30,  40)
    return logs


def mai_bedroom_office(date, uid, hid) -> list:
    """
    Mai đổi 'văn phòng' sang phòng ngủ thay vì phòng khách.
    """
    logs = []
    h, m = gauss_min(9, 15, 25)
    logs += on_off(date, uid, hid, "light_bedroom", h, m,      240)
    logs += on_off(date, uid, hid, "fan_bedroom",   h, m + 5,  230)
    logs += on_off(date, uid, hid, "light_kitchen", 11, 30,     40)
    h2, m2 = gauss_min(14, 30, 25)
    logs += on_off(date, uid, hid, "light_bedroom", h2, m2,   150,
                   drop_off_prob=0.12)
    return logs


def mai_long_nap(date, uid, hid) -> list:
    """Ngủ trưa dài bất thường: 2-3h thay vì 70 phút."""
    h, m = gauss_min(13, 0, 30)
    dur  = random.randint(120, 180)
    logs = []
    logs += on_off(date, uid, hid, "fan_bedroom", h, m, dur,
                   is_forgot=True,   # đánh dấu anomaly
                   drop_off_prob=0.2)
    if maybe(0.5):
        logs += on_off(date, uid, hid, "ac_bedroom", h, m + 5, dur - 5,
                       is_forgot=True, drop_off_prob=0.25)
    return logs


# ═══════════════════════════════════════════════════════════════════════════════
# DAY CLASSIFIER
# ═══════════════════════════════════════════════════════════════════════════════

def classify_day(date, day_offset: int) -> str:
    """70/15/10/5 — deterministic dựa trên hash(date)."""
    h = hash((date.isoformat(), day_offset, "v3")) % 100
    if h < 70:   return "normal"
    elif h < 85: return "disrupted"
    elif h < 95: return "anomaly"
    else:        return "away"


# ═══════════════════════════════════════════════════════════════════════════════
# CORE GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_hung_day(date, uid, hid, day_type: str, weekday: int) -> list:
    logs = []

    # WFH override (~10% T2-T6, chỉ xảy ra vào ngày normal/disrupted)
    if day_type != "away" and weekday in [0,1,2,3,4] and maybe(0.10):
        logs += wfh_day_logs(date, uid, hid, weekday)
        logs += device_interaction_noise(date, uid, hid)
        return logs

    # Thức khuya xem phim (~8%/tuần, bất kể loại ngày)
    if maybe(0.08):
        logs += late_night_movie(date, uid, hid)

    # Ốm (~3%/tháng ≈ 1%)
    if maybe(0.01):
        logs += sick_day_logs(date, uid, hid)
        return logs  # ốm thì không có thói quen thường

    # Mất ngủ (~5%)
    if maybe(0.05):
        logs += insomnia_logs(date, uid, hid)

    if day_type == "away":
        if maybe(0.25):
            logs += on_off(date, None, hid, "fan_living", 7, 0, 15,
                           trigger=TriggerSource.SCHEDULE)
        return logs

    # Forget off hôm nay
    forget_today = {
        dev for dev, prob, *_ in PERSONAS[0]["forget_off"] if maybe(prob)
    }

    if day_type == "normal":
        prob_mult, sigma_mult = 1.0, 1.0
    elif day_type == "disrupted":
        prob_mult, sigma_mult = 0.40, 2.5
    else:  # anomaly
        prob_mult, sigma_mult = 0.20, 3.0

    for dev, h, m, dur, days, prob, sigma in HUNG_HABITS:
        if days is not None and weekday not in days:
            continue
        if not maybe(prob * prob_mult):
            continue

        rh, rm = gauss_min(h, m, int(sigma * sigma_mult))
        is_forgot = dev in forget_today and dur > 0
        extra_dur = dur
        if is_forgot:
            for fdev, _, emin, emax in PERSONAS[0]["forget_off"]:
                if fdev == dev:
                    extra_dur += random.randint(emin, emax)
                    break

        # Hùng về muộn: lùi thói quen tối 2-3h (~20% ngày T2-T6)
        if day_type == "normal" and weekday in [0,1,2,3,4] and h >= 18 and maybe(0.20):
            rh = min(23, rh + random.randint(2, 3))

        logs += on_off(date, uid, hid, dev, rh, rm,
                       extra_dur if is_forgot else dur,
                       is_forgot=is_forgot,
                       drop_off_prob=0.06)

    if day_type == "anomaly":
        # 1-2 sự kiện giờ lạ
        for _ in range(random.randint(1, 2)):
            dev = random.choice(DEVICE_IDS)
            ah  = random.randint(0, 5)
            logs += on_off(date, uid, hid, dev, ah, random.randint(0,59),
                           random.randint(30, 150),
                           trigger=TriggerSource.PHYSICAL_UNKNOWN)

    logs += device_interaction_noise(date, uid, hid)
    return logs


def generate_mai_day(date, uid, hid, day_type: str, weekday: int) -> list:
    logs = []

    # Thức khuya deadline (~15% T2-T5)
    is_deadline = weekday in [0,1,2,3] and maybe(0.15)
    if is_deadline:
        logs += mai_deadline_night(date, uid, hid, weekday)

    # Ốm (~1.5% — hay ốm hơn Hùng vì ở nhà)
    if maybe(0.015):
        logs += sick_day_logs(date, uid, hid)
        return logs

    # Mất ngủ (~7%)
    if maybe(0.07):
        logs += insomnia_logs(date, uid, hid)

    if day_type == "away":
        return logs  # đi vắng, không có gì

    # T6: đi cà phê sáng (~40%)
    is_cafe_friday = (weekday == 4) and maybe(0.40)
    if is_cafe_friday:
        logs += mai_cafe_morning(date, uid, hid)
        logs += device_interaction_noise(date, uid, hid)
        return logs

    # Đổi "văn phòng" sang phòng ngủ (~30% T2-T6)
    is_bedroom_office = (weekday in [0,1,2,3,4]) and maybe(0.30)

    # Ngủ trưa dài (~15%)
    is_long_nap = maybe(0.15)

    if is_bedroom_office:
        logs += mai_bedroom_office(date, uid, hid)
    
    if is_long_nap:
        logs += mai_long_nap(date, uid, hid)

    # Forget off
    forget_today = {
        dev for dev, prob, *_ in PERSONAS[1]["forget_off"] if maybe(prob)
    }

    if day_type == "normal":
        prob_mult, sigma_mult = 1.0, 1.0
    elif day_type == "disrupted":
        prob_mult, sigma_mult = 0.35, 3.0   # Mai loạn hơn Hùng khi disrupted
    else:  # anomaly
        prob_mult, sigma_mult = 0.15, 4.0

    for dev, h, m, dur, days, prob, sigma in MAI_HABITS:
        if days is not None and weekday not in days:
            continue

        # Skip thói quen phòng khách buổi sáng nếu đang dùng phòng ngủ làm VP
        if is_bedroom_office and dev in ("light_living","fan_living") and h < 16:
            continue
        # Skip thói quen phòng ngủ buổi sáng nếu đi cà phê (đã handle ở trên)
        if is_cafe_friday:
            continue
        # Skip ngủ trưa ngắn nếu đã ngủ dài
        if is_long_nap and dev in ("fan_bedroom","ac_bedroom") and 12 <= h <= 14:
            continue
        # Deadline: ngủ muộn → skip thói quen dậy sớm hôm sau (~40%)
        if is_deadline and h < 8 and maybe(0.40):
            continue

        if not maybe(prob * prob_mult):
            continue

        rh, rm = gauss_min(h, m, int(sigma * sigma_mult))
        is_forgot = dev in forget_today and dur > 0
        extra_dur = dur
        if is_forgot:
            for fdev, _, emin, emax in PERSONAS[1]["forget_off"]:
                if fdev == dev:
                    extra_dur += random.randint(emin, emax)
                    break

        logs += on_off(date, uid, hid, dev, rh, rm,
                       extra_dur if is_forgot else dur,
                       is_forgot=is_forgot,
                       drop_off_prob=0.10)   # Mai hay bị mất OFF log hơn

    if day_type == "anomaly":
        for _ in range(random.randint(1, 3)):
            dev = random.choice(DEVICE_IDS)
            ah  = random.randint(0, 5)
            logs += on_off(date, uid, hid, dev, ah, random.randint(0,59),
                           random.randint(20, 120),
                           trigger=TriggerSource.PHYSICAL_UNKNOWN)

    logs += device_interaction_noise(date, uid, hid)
    return logs


# ═══════════════════════════════════════════════════════════════════════════════
# STATIC FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

def create_static_fixtures(session):
    home = Home(id=uuid.uuid4(), name="Nhà Hùng - Mai",
                address="123 Đường Lê Lợi, TP.HCM",
                timezone="Asia/Ho_Chi_Minh")
    session.add(home); session.flush()

    room_map = {}
    for r in ROOMS_DEF:
        room = Room(home_id=home.id, name=r["name"], icon=r["icon"])
        session.add(room); session.flush()
        room_map[r["name"]] = room

    for dev_id, dev_name, dev_type, room_name in DEVICES_DEF:
        session.add(Device(id=dev_id, room_id=room_map[room_name].id,
                           name=dev_name, type=dev_type,
                           mqtt_topic=f"home/{dev_id}", config={}))
        session.add(DeviceState(device_id=dev_id, is_online=True,
                                state={"power": "OFF"}))
    session.flush()
    return home


def create_users(session, home):
    users = []
    for p in PERSONAS:
        user = User(id=uuid.uuid4(), email=p["email"],
                    password_hash=p["password_hash"],
                    full_name=p["name"], role=p["role"], is_active=True)
        session.add(user); session.flush()
        session.add(HomeUser(home_id=home.id, user_id=user.id, role=p["role"]))
        session.add(UserPresence(user_id=user.id, home_id=home.id,
                                  is_home=False, detected_by="APP"))
        users.append(user)
    session.flush()
    return users


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

def generate_activity_logs(session, home, users, seed_days):
    today   = datetime.now(TZ).date()
    hung, mai = users[0], users[1]
    all_logs  = []
    stats     = {"normal":0,"disrupted":0,"anomaly":0,"away":0}

    # Đi vắng dài: chọn trước 1-2 đợt trong 60 ngày (2-4 ngày liên tiếp)
    away_ranges = set()
    n_trips = random.randint(1, 2)
    for _ in range(n_trips):
        start_off = random.randint(5, seed_days - 5)
        length    = random.randint(2, 4)
        for d in range(length):
            away_ranges.add(start_off - d)

    for day_offset in range(seed_days, 0, -1):
        current = today - timedelta(days=day_offset)
        weekday = current.weekday()

        if day_offset in away_ranges:
            day_type = "away"
        else:
            day_type = classify_day(current, day_offset)
        stats[day_type] += 1

        outage = power_outage_gap(current, home.id)

        hung_logs = generate_hung_day(current, hung.id, home.id, day_type, weekday)
        mai_logs  = generate_mai_day(current, mai.id,  home.id, day_type, weekday)

        hung_logs = apply_mqtt_dropout(hung_logs, 0.06)
        mai_logs  = apply_mqtt_dropout(mai_logs,  0.10)

        hung_logs = filter_outage(hung_logs, outage)
        mai_logs  = filter_outage(mai_logs,  outage)

        all_logs += hung_logs + mai_logs

    for i in range(0, len(all_logs), 500):
        session.add_all(all_logs[i:i+500])
        session.flush()

    print(f"  → {len(all_logs):,} activity_log records")
    print(f"     Phân bố: normal={stats['normal']} disrupted={stats['disrupted']} "
          f"anomaly={stats['anomaly']} away={stats['away']}")
    return all_logs


def generate_sensor_data(session, home, seed_days):
    today = datetime.now(TZ).date()
    HOURLY_TEMP = {
        0:27.5,1:27.0,2:26.8,3:26.5,4:26.5,5:26.8,
        6:27.5,7:28.5,8:29.5,9:30.5,10:31.8,11:33.0,
        12:34.0,13:34.5,14:34.2,15:33.5,16:32.0,17:31.0,
        18:30.0,19:29.5,20:29.0,21:28.5,22:28.0,23:27.8,
    }
    row = session.execute(text("SELECT id FROM rooms WHERE name='Phòng khách' LIMIT 1")).fetchone()
    rid = row[0] if row else None
    for sid, sname in [("sensor_temp","Cảm biến nhiệt độ"),("sensor_humid","Cảm biến độ ẩm")]:
        if not session.get(Device, sid):
            session.add(Device(id=sid, name=sname, type=DeviceType.SENSOR,
                               mqtt_topic=f"home/{sid}", room_id=rid, config={}))
            session.add(DeviceState(device_id=sid, is_online=True, state={}))
    session.flush()

    records = []
    for day_offset in range(seed_days, 0, -1):
        current = today - timedelta(days=day_offset)
        for h in range(24):
            ts   = local_dt(current, h, random.randint(0,59))
            temp = HOURLY_TEMP[h] + random.gauss(0, 0.8)
            hum  = max(55, min(92, 75 - (h-6)*0.3 + random.gauss(0,3)))
            records += [
                SensorData(time=ts, device_id="sensor_temp",
                           metric_type=MetricType.TEMP,     value=round(temp,1)),
                SensorData(time=ts, device_id="sensor_humid",
                           metric_type=MetricType.HUMIDITY, value=round(hum, 1)),
            ]
    for i in range(0, len(records), 500):
        session.add_all(records[i:i+500])
        session.flush()
    print(f"  → {len(records):,} sensor_data records")


def clear_existing_data(session):
    print("  Xoá data cũ...")
    # Truncate theo thứ tự phụ thuộc để xoá sạch data cũ và reset identity/sequence.
    tables = [
        "suggestion_logs",
        "user_patterns",
        "activity_logs",
        "sensor_data",
        "user_presence",
        "device_states",
        "home_users",
        "devices",
        "rooms",
        "users",
        "homes",
    ]
    session.execute(text(
        f"TRUNCATE TABLE {', '.join(tables)} RESTART IDENTITY CASCADE"
    ))
    session.flush()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=60)
    parser.add_argument("--drop", action="store_true")
    args = parser.parse_args()

    random.seed(42)

    engine = create_engine(DB_URL, echo=False)
    with Session(engine) as session:
        with session.begin():
            if args.drop:
                clear_existing_data(session)

            print("1. Tạo Home / Room / Device...")
            home = create_static_fixtures(session)

            print("2. Tạo User + HomeUser...")
            users = create_users(session, home)

            print(f"3. Sinh {args.days} ngày ActivityLog (full noise model)...")
            generate_activity_logs(session, home, users, args.days)

            print("4. Sinh SensorData...")
            generate_sensor_data(session, home, args.days)

    print("\n✓ Done!")
    print("Noise model:")
    print("  Temporal  : WFH ngẫu nhiên, về muộn, thức khuya, ốm, mất ngủ")
    print("  Missing   : MQTT dropout 6-10%, cúp điện 4%/ngày, đi vắng dài 1-2 đợt")
    print("  Mai chaos : deadline, đổi VP, T6 cà phê, ngủ trưa skip/dài bất thường")
    print("  Device    : nhấn nhầm, double-trigger, ghost event, tắt-bật lại")
    print("\nBước tiếp:")
    print("  python scripts/run_analytics.py")

if __name__ == "__main__":
    main()
