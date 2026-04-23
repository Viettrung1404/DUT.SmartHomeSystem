"""
scripts/db/seed.py  —  Seed dữ liệu cơ bản để test API
=========================================================
Tạo đủ dữ liệu cho tất cả API hiện có:
  - Auth   : 3 users (admin, member, guest) với password thực
  - Homes  : 2 homes, mỗi home có nhiều rooms và members
  - Rooms  : phòng ngủ, phòng khách, bếp, nhà vệ sinh
  - Devices: đủ loại (light, ac, fan, sensor, camera, lock, curtain)
  - Automations + Conditions + Actions
  - DeviceLogs, EnergyLogs
  - SecurityEvents
  - SuggestionLogs

Chạy từ thư mục backend/:
    python scripts/db/seed.py           # seed bình thường
    python scripts/db/seed.py --drop    # xóa data cũ rồi seed lại
    python scripts/db/seed.py --wipe    # xóa TOÀN BỘ rồi seed lại

Accounts tạo ra:
    admin@demo.local    / Admin@123456  (role=ADMIN, owner của Home 1)
    member@demo.local   / Member@123   (role=MEMBER, member của Home 1 & Home 2)
    guest@demo.local    / Guest@123    (role=MEMBER, member của Home 2)
    owner2@demo.local   / Owner2@123   (role=ADMIN, owner của Home 2)
"""

import sys
import io
import argparse
import os

# Force UTF-8 stdout on Windows (cp1252 can't render Vietnamese)
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import uuid
from datetime import datetime, timedelta, timezone

# ── Cho phép import từ backend/src ────────────────────────────────────────────
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from src.database.core import Base
from src.entities.user import User
from src.entities.home import Home
from src.entities.home_member import HomeMember
from src.entities.room import Room
from src.entities.device import Device
from src.entities.automation import Automation, AutomationCondition, AutomationAction
from src.entities.device_log import DeviceLog
from src.entities.energy_log import EnergyLog
from src.entities.security_event import SecurityEvent
from src.entities.suggestion_log import SuggestionLog

# ── Đọc DATABASE_URL từ .env nếu có ───────────────────────────────────────────
try:
    from src.config.env import DATABASE_URL
except Exception:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/smarthome")

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def h(plain: str) -> str:
    return pwd_ctx.hash(plain)

def now_utc(offset_hours: float = 0) -> datetime:
    return datetime.now(timezone.utc) - timedelta(hours=offset_hours)


# ═══════════════════════════════════════════════════════════════════════════════
# WIPE / DROP helpers
# ═══════════════════════════════════════════════════════════════════════════════

TABLES_NEW = [
    "suggestion_logs", "security_events", "energy_logs", "device_logs",
    "automation_actions", "automation_conditions", "automations",
    "devices", "rooms", "home_members", "homes",
    "password_reset_tokens", "auth_sessions", "users",
]

def wipe_new_tables(engine):
    """Xóa toàn bộ data trong các bảng mới (theo thứ tự FK)."""
    with engine.begin() as conn:
        conn.execute(text("SET session_replication_role = replica"))  # tắt FK trigger
        for tbl in TABLES_NEW:
            try:
                conn.execute(text(f"TRUNCATE TABLE {tbl} CASCADE"))
                print(f"  ✓ truncated {tbl}")
            except Exception as e:
                print(f"  ⚠ {tbl}: {e}")
        conn.execute(text("SET session_replication_role = DEFAULT"))


# ═══════════════════════════════════════════════════════════════════════════════
# SEED FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def seed_users(db: Session) -> dict:
    """Tạo 4 users với password thực (bcrypt)."""
    users_data = [
        dict(
            email="admin@demo.local",
            full_name="Nguyễn Văn Admin",
            password_hash=h("Admin@123456"),
            role="ADMIN",
            avatar_url="https://ui-avatars.com/api/?name=Admin&background=6366f1&color=fff",
        ),
        dict(
            email="member@demo.local",
            full_name="Trần Thị Member",
            password_hash=h("Member@123"),
            role="MEMBER",
            avatar_url="https://ui-avatars.com/api/?name=Member&background=10b981&color=fff",
        ),
        dict(
            email="guest@demo.local",
            full_name="Lê Văn Guest",
            password_hash=h("Guest@123"),
            role="MEMBER",
            avatar_url="https://ui-avatars.com/api/?name=Guest&background=f59e0b&color=fff",
        ),
        dict(
            email="owner2@demo.local",
            full_name="Phạm Thị Owner",
            password_hash=h("Owner2@123"),
            role="ADMIN",
            avatar_url="https://ui-avatars.com/api/?name=Owner&background=ef4444&color=fff",
        ),
    ]

    users = {}
    for data in users_data:
        # Skip nếu đã tồn tại
        existing = db.query(User).filter_by(email=data["email"]).first()
        if existing:
            users[data["email"]] = existing
            print(f"  - (existing) {data['email']}")
            continue

        user = User(id=uuid.uuid4(), **data, is_active=True,
                    created_at=now_utc(offset_hours=72))
        db.add(user)
        db.flush()
        users[data["email"]] = user
        print(f"  + created user: {data['email']}")

    return users


def seed_homes(db: Session, users: dict) -> dict:
    """Tạo 2 homes."""
    admin = users["admin@demo.local"]
    owner2 = users["owner2@demo.local"]

    homes_data = [
        dict(
            owner_id=admin.id,
            name="Nhà Nguyễn Văn Admin",
            address="123 Đường Lê Lợi, Quận 1, TP. Hồ Chí Minh",
        ),
        dict(
            owner_id=owner2.id,
            name="Biệt thự Phạm Gia",
            address="456 Đường Nguyễn Huệ, Quận 3, TP. Hồ Chí Minh",
        ),
    ]

    homes = {}
    for data in homes_data:
        home = Home(id=uuid.uuid4(), **data,
                    created_at=now_utc(offset_hours=48))
        db.add(home)
        db.flush()
        homes[data["name"]] = home
        print(f"  + created home: {data['name']}")

    return homes


def seed_home_members(db: Session, users: dict, homes: dict):
    """Gán thành viên vào homes."""
    home1 = homes["Nhà Nguyễn Văn Admin"]
    home2 = homes["Biệt thự Phạm Gia"]
    admin = users["admin@demo.local"]
    member = users["member@demo.local"]
    guest = users["guest@demo.local"]
    owner2 = users["owner2@demo.local"]

    memberships = [
        # Home 1: admin là owner, member là member
        dict(home_id=home1.id, user_id=admin.id,  role="owner"),
        dict(home_id=home1.id, user_id=member.id, role="member"),
        # Home 2: owner2 là owner, member và guest là member
        dict(home_id=home2.id, user_id=owner2.id, role="owner"),
        dict(home_id=home2.id, user_id=member.id, role="member"),
        dict(home_id=home2.id, user_id=guest.id,  role="member"),
    ]

    for data in memberships:
        # Skip nếu đã tồn tại
        exists = db.query(HomeMember).filter_by(
            home_id=data["home_id"], user_id=data["user_id"]
        ).first()
        if exists:
            continue
        hm = HomeMember(id=uuid.uuid4(), **data,
                        joined_at=now_utc(offset_hours=47))
        db.add(hm)

    db.flush()
    print(f"  + seeded {len(memberships)} home memberships")


def seed_rooms(db: Session, homes: dict) -> dict:
    """Tạo các phòng cho 2 homes."""
    home1 = homes["Nhà Nguyễn Văn Admin"]
    home2 = homes["Biệt thự Phạm Gia"]

    rooms_def = [
        # Home 1
        (home1.id, "Phòng ngủ chính",  "bed"),
        (home1.id, "Phòng khách",       "sofa"),
        (home1.id, "Bếp",               "kitchen"),
        (home1.id, "Nhà vệ sinh",       "bath"),
        (home1.id, "Phòng ngủ con",     "bed"),
        # Home 2
        (home2.id, "Master Bedroom",    "bed"),
        (home2.id, "Living Room",       "sofa"),
        (home2.id, "Kitchen",           "kitchen"),
        (home2.id, "Garage",            "garage"),
    ]

    rooms = {}
    for home_id, name, icon in rooms_def:
        room = Room(id=uuid.uuid4(), home_id=home_id, name=name, icon=icon,
                    created_at=now_utc(offset_hours=46))
        db.add(room)
        db.flush()
        rooms[f"{home_id}_{name}"] = room

    print(f"  + created {len(rooms_def)} rooms")
    return rooms


def seed_devices(db: Session, rooms: dict, homes: dict) -> dict:
    """Tạo các thiết bị đủ loại."""
    home1 = homes["Nhà Nguyễn Văn Admin"]
    home2 = homes["Biệt thự Phạm Gia"]

    def room(home, name):
        return rooms[f"{home.id}_{name}"]

    now = now_utc(offset_hours=24)

    devices_def = [
        # ── Home 1 ──────────────────────────────────────────────────
        # Phòng ngủ chính
        dict(room_id=room(home1, "Phòng ngủ chính").id,
             name="Đèn LED phòng ngủ", type="light",
             status=False, online_status=True,
             metadata_json={"brightness": 75, "color_temp": 4000},
             last_seen=now),
        dict(room_id=room(home1, "Phòng ngủ chính").id,
             name="Điều hòa Panasonic", type="ac",
             status=True, online_status=True,
             metadata_json={"temperature": 26, "targetTemp": 25, "mode": "cool", "fanSpeed": "auto"},
             last_seen=now),
        dict(room_id=room(home1, "Phòng ngủ chính").id,
             name="Quạt trần ASSA", type="fan",
             status=False, online_status=True,
             metadata_json={"speed": 3},
             last_seen=now),
        dict(room_id=room(home1, "Phòng ngủ chính").id,
             name="Khóa cửa Smart Lock", type="lock",
             status=False, online_status=True,
             metadata_json={"isLocked": True, "battery": 87},
             last_seen=now),
        dict(room_id=room(home1, "Phòng ngủ chính").id,
             name="Rèm thông minh", type="curtain",
             status=False, online_status=True,
             metadata_json={"position": 100},
             last_seen=now),

        # Phòng khách
        dict(room_id=room(home1, "Phòng khách").id,
             name="Đèn trần phòng khách", type="light",
             status=True, online_status=True,
             metadata_json={"brightness": 100},
             last_seen=now),
        dict(room_id=room(home1, "Phòng khách").id,
             name="Điều hòa LG Dual Cool", type="ac",
             status=False, online_status=True,
             metadata_json={"temperature": 28, "targetTemp": 26, "mode": "cool", "fanSpeed": "high"},
             last_seen=now),
        dict(room_id=room(home1, "Phòng khách").id,
             name="Cảm biến chuyển động PIR", type="sensor",
             status=True, online_status=True,
             metadata_json={"motion": False, "battery": 92},
             last_seen=now),
        dict(room_id=room(home1, "Phòng khách").id,
             name="Camera an ninh 4K", type="camera",
             status=True, online_status=True,
             metadata_json={"recording": True, "resolution": "4K"},
             last_seen=now),

        # Bếp
        dict(room_id=room(home1, "Bếp").id,
             name="Đèn bếp", type="light",
             status=False, online_status=True,
             metadata_json={"brightness": 90},
             last_seen=now),
        dict(room_id=room(home1, "Bếp").id,
             name="Cảm biến khí gas", type="sensor",
             status=True, online_status=True,
             metadata_json={"gasLevel": 0, "battery": 78},
             last_seen=now),

        # Nhà vệ sinh
        dict(room_id=room(home1, "Nhà vệ sinh").id,
             name="Đèn nhà tắm", type="light",
             status=False, online_status=False,
             metadata_json={"brightness": 100},
             last_seen=now_utc(offset_hours=2)),
        dict(room_id=room(home1, "Nhà vệ sinh").id,
             name="Quạt thông gió", type="fan",
             status=False, online_status=True,
             metadata_json={"speed": 1},
             last_seen=now),

        # Phòng ngủ con
        dict(room_id=room(home1, "Phòng ngủ con").id,
             name="Đèn ngủ Night Light", type="light",
             status=True, online_status=True,
             metadata_json={"brightness": 20, "color": "#ff9500"},
             last_seen=now),
        dict(room_id=room(home1, "Phòng ngủ con").id,
             name="Quạt đứng Xiaomi", type="fan",
             status=False, online_status=True,
             metadata_json={"speed": 2},
             last_seen=now),

        # ── Home 2 ──────────────────────────────────────────────────
        dict(room_id=room(home2, "Master Bedroom").id,
             name="Smart Light Philips", type="light",
             status=False, online_status=True,
             metadata_json={"brightness": 60, "color_temp": 3000},
             last_seen=now),
        dict(room_id=room(home2, "Master Bedroom").id,
             name="Smart AC Daikin", type="ac",
             status=True, online_status=True,
             metadata_json={"temperature": 27, "targetTemp": 24, "mode": "cool", "fanSpeed": "low"},
             last_seen=now),
        dict(room_id=room(home2, "Living Room").id,
             name="Smart TV Backlight", type="light",
             status=True, online_status=True,
             metadata_json={"brightness": 50},
             last_seen=now),
        dict(room_id=room(home2, "Garage").id,
             name="Garage Door Lock", type="lock",
             status=False, online_status=True,
             metadata_json={"isLocked": False, "battery": 65},
             last_seen=now),
        dict(room_id=room(home2, "Garage").id,
             name="Garage Camera", type="camera",
             status=True, online_status=True,
             metadata_json={"recording": True, "resolution": "1080p"},
             last_seen=now),
    ]

    devices = {}
    for data in devices_def:
        device = Device(id=uuid.uuid4(),
                        created_at=now_utc(offset_hours=40),
                        **data)
        db.add(device)
        db.flush()
        devices[data["name"]] = device

    print(f"  + created {len(devices_def)} devices")
    return devices


def seed_device_logs(db: Session, devices: dict):
    """Tạo lịch sử thao tác cho các thiết bị (30 ngày gần nhất)."""
    target_devices = [
        "Đèn LED phòng ngủ",
        "Điều hòa Panasonic",
        "Quạt trần ASSA",
        "Đèn trần phòng khách",
        "Điều hòa LG Dual Cool",
        "Đèn bếp",
        "Smart Light Philips",
    ]

    log_templates = [
        ("toggle", "on"),
        ("toggle", "off"),
        ("brightness", "75"),
        ("brightness", "100"),
        ("brightness", "50"),
        ("temperature", "25"),
        ("temperature", "26"),
        ("mode", "cool"),
        ("mode", "fan"),
        ("fanSpeed", "auto"),
    ]

    count = 0
    for dev_name in target_devices:
        device = devices.get(dev_name)
        if not device:
            continue
        # Tạo 20 log entry trong 30 ngày
        for i in range(20):
            action, value = log_templates[i % len(log_templates)]
            if device.type not in ("ac",) and action in ("temperature", "mode", "fanSpeed"):
                action, value = log_templates[i % 3]  # chỉ toggle/brightness cho non-AC
            ts = now_utc(offset_hours=i * 36)  # mỗi 36h 1 log = ~30 ngày
            log = DeviceLog(
                id=uuid.uuid4(),
                device_id=device.id,
                action=action,
                value=value,
                timestamp=ts,
            )
            db.add(log)
            count += 1

    db.flush()
    print(f"  + created {count} device logs")


def seed_energy_logs(db: Session, devices: dict):
    """Tạo dữ liệu điện năng tiêu thụ 30 ngày."""
    # Chỉ các thiết bị tiêu thụ điện có ý nghĩa
    energy_devices = {
        "Điều hòa Panasonic":    (0.8, 1.5),   # (kWh min, max) mỗi record
        "Điều hòa LG Dual Cool": (0.6, 1.2),
        "Đèn LED phòng ngủ":     (0.01, 0.05),
        "Đèn trần phòng khách":  (0.02, 0.06),
        "Đèn bếp":               (0.01, 0.04),
        "Quạt trần ASSA":        (0.04, 0.08),
        "Smart AC Daikin":       (0.7, 1.4),
    }

    import random
    random.seed(42)

    count = 0
    for dev_name, (lo, hi) in energy_devices.items():
        device = devices.get(dev_name)
        if not device:
            continue
        # Log mỗi 6 tiếng trong 30 ngày = 120 records
        for i in range(120):
            ts = now_utc(offset_hours=i * 6)
            # Giả lập điện năng thực tế theo giờ trong ngày
            hour_in_day = (i * 6) % 24
            multiplier = 1.3 if 12 <= hour_in_day <= 22 else 0.7  # ban ngày tiêu nhiều hơn
            usage = round(random.uniform(lo, hi) * multiplier, 3)
            energy = EnergyLog(
                id=uuid.uuid4(),
                device_id=device.id,
                power_usage=usage,
                timestamp=ts,
            )
            db.add(energy)
            count += 1

    db.flush()
    print(f"  + created {count} energy logs")


def seed_automations(db: Session, homes: dict, devices: dict):
    """Tạo các automation rules cho Home 1."""
    home1 = homes["Nhà Nguyễn Văn Admin"]

    ac_bedroom = devices.get("Điều hòa Panasonic")
    light_main = devices.get("Đèn LED phòng ngủ")
    light_living = devices.get("Đèn trần phòng khách")
    curtain = devices.get("Rèm thông minh")
    fan = devices.get("Quạt trần ASSA")

    automations_def = [
        {
            "name": "Tắt đèn lúc 23:00",
            "enabled": True,
            "conditions": [
                {"condition_type": "time", "value": "23:00"},
            ],
            "actions": [
                {"device": light_main,  "action": "toggle", "value": "off"},
                {"device": light_living, "action": "toggle", "value": "off"},
            ],
        },
        {
            "name": "Bật điều hòa khi nhiệt độ > 32°C",
            "enabled": True,
            "conditions": [
                {"condition_type": "temperature", "value": "> 32"},
            ],
            "actions": [
                {"device": ac_bedroom, "action": "set_temperature", "value": "25"},
                {"device": fan, "action": "toggle", "value": "on"},
            ],
        },
        {
            "name": "Mở rèm lúc 7:00 sáng",
            "enabled": True,
            "conditions": [
                {"condition_type": "time", "value": "07:00"},
            ],
            "actions": [
                {"device": curtain, "action": "toggle", "value": "open"},
            ],
        },
        {
            "name": "Tắt tất cả khi ra khỏi nhà",
            "enabled": False,  # disabled để test
            "conditions": [
                {"condition_type": "device_status", "value": "lock_activated"},
            ],
            "actions": [
                {"device": light_main,   "action": "toggle", "value": "off"},
                {"device": light_living, "action": "toggle", "value": "off"},
                {"device": ac_bedroom,   "action": "toggle", "value": "off"},
                {"device": fan,          "action": "toggle", "value": "off"},
            ],
        },
        {
            "name": "Chế độ ngủ lúc 22:30",
            "enabled": True,
            "conditions": [
                {"condition_type": "time", "value": "22:30"},
            ],
            "actions": [
                {"device": ac_bedroom, "action": "set_temperature", "value": "26"},
                {"device": light_main, "action": "set_brightness",  "value": "20"},
                {"device": curtain,    "action": "toggle",           "value": "close"},
            ],
        },
    ]

    automation_count = 0
    condition_count = 0
    action_count = 0

    for a_def in automations_def:
        auto = Automation(
            id=uuid.uuid4(),
            home_id=home1.id,
            name=a_def["name"],
            enabled=a_def["enabled"],
            created_at=now_utc(offset_hours=72),
        )
        db.add(auto)
        db.flush()
        automation_count += 1

        for c in a_def["conditions"]:
            cond = AutomationCondition(
                id=uuid.uuid4(),
                automation_id=auto.id,
                condition_type=c["condition_type"],
                value=c["value"],
            )
            db.add(cond)
            condition_count += 1

        for act in a_def["actions"]:
            device_obj = act["device"]
            if device_obj is None:
                continue
            action_obj = AutomationAction(
                id=uuid.uuid4(),
                automation_id=auto.id,
                device_id=device_obj.id,
                action=act["action"],
                value=act["value"],
            )
            db.add(action_obj)
            action_count += 1

    db.flush()
    print(f"  + created {automation_count} automations, "
          f"{condition_count} conditions, {action_count} actions")


def seed_security_events(db: Session, homes: dict):
    """Tạo các sự kiện bảo mật mẫu."""
    home1 = homes["Nhà Nguyễn Văn Admin"]
    home2 = homes["Biệt thự Phạm Gia"]

    events = [
        # Home 1
        (home1.id, "motion_detected",    "medium", "Phát hiện chuyển động tại phòng khách lúc 2:30 AM",        now_utc(offset_hours=5)),
        (home1.id, "door_opened",        "low",    "Cửa chính mở lúc 7:15 AM",                                 now_utc(offset_hours=14)),
        (home1.id, "device_offline",     "low",    "Đèn nhà tắm mất kết nối",                                  now_utc(offset_hours=2)),
        (home1.id, "unusual_activity",   "high",   "Phát hiện hoạt động bất thường: đèn bật nhiều lần ban đêm", now_utc(offset_hours=30)),
        (home1.id, "motion_detected",    "high",   "Phát hiện chuyển động khi không có ai ở nhà (3:00 AM)",     now_utc(offset_hours=48)),
        (home1.id, "smoke_detected",     "high",   "Cảm biến khói phát hiện khói ở bếp",                       now_utc(offset_hours=72)),
        (home1.id, "door_opened",        "medium", "Cửa garage mở khi chủ nhà đang ra ngoài",                  now_utc(offset_hours=96)),
        (home1.id, "motion_detected",    "low",    "Chuyển động phòng khách lúc 8:00 AM (bình thường)",         now_utc(offset_hours=120)),
        # Home 2
        (home2.id, "motion_detected",    "low",    "Motion detected in Living Room",                            now_utc(offset_hours=6)),
        (home2.id, "door_opened",        "medium", "Garage door opened at 11 PM",                              now_utc(offset_hours=8)),
        (home2.id, "unusual_activity",   "medium", "Unusual energy consumption detected",                      now_utc(offset_hours=24)),
    ]

    for home_id, event_type, severity, description, ts in events:
        ev = SecurityEvent(
            id=uuid.uuid4(),
            home_id=home_id,
            event_type=event_type,
            severity=severity,
            description=description,
            timestamp=ts,
        )
        db.add(ev)

    db.flush()
    print(f"  + created {len(events)} security events")


def seed_suggestion_logs(db: Session, users: dict):
    """Tạo AI suggestion logs mẫu."""
    admin = users["admin@demo.local"]
    member = users["member@demo.local"]

    suggestions = [
        dict(
            user_id=admin.id,
            action_type="SCHEDULE",
            suggestion_text="Bật điều hòa tự động lúc 21:30 thay vì 22:00 vì bạn thường lên phòng lúc 21:45",
            suggestion_json={"device": "Điều hòa Panasonic", "time": "21:30", "action": "on"},
            was_accepted=True,
        ),
        dict(
            user_id=admin.id,
            action_type="AUTOMATION",
            suggestion_text="Tạo automation tắt đèn sau 30 phút nếu không có chuyển động",
            suggestion_json={"trigger": "no_motion", "duration": 1800, "action": "toggle_off"},
            was_accepted=False,
        ),
        dict(
            user_id=admin.id,
            action_type="ALERT",
            suggestion_text="Cảnh báo: Điều hòa đã hoạt động liên tục 8 tiếng, có thể do cửa sổ mở",
            suggestion_json={"device": "Điều hòa Panasonic", "duration": 28800},
            was_accepted=None,  # chưa xử lý
        ),
        dict(
            user_id=member.id,
            action_type="SCHEDULE",
            suggestion_text="Bật đèn phòng khách lúc 18:00 vào các ngày trong tuần",
            suggestion_json={"device": "Đèn trần phòng khách", "time": "18:00", "days": [0,1,2,3,4]},
            was_accepted=True,
        ),
        dict(
            user_id=member.id,
            action_type="ALERT",
            suggestion_text="Phát hiện thiết bị bật khi không ai ở nhà (11:00 - 15:00)",
            suggestion_json={"devices": ["Đèn bếp"], "time_range": ["11:00", "15:00"]},
            was_accepted=None,
        ),
    ]

    for data in suggestions:
        sl = SuggestionLog(
            user_id=data["user_id"],
            action_type=data["action_type"],
            suggestion_text=data["suggestion_text"],
            suggestion_json=data["suggestion_json"],
            was_accepted=data["was_accepted"],
        )
        db.add(sl)

    db.flush()
    print(f"  + created {len(suggestions)} suggestion logs")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Seed database for Smart Home API testing")
    parser.add_argument("--drop",  action="store_true",
                        help="Clear existing data in new tables then re-seed")
    parser.add_argument("--wipe",  action="store_true",
                        help="TRUNCATE CASCADE all new tables then re-seed")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  Smart Home API — Seed Script")
    print(f"  Database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
    print(f"{'='*60}\n")

    engine = create_engine(DATABASE_URL)

    # Tạo bảng nếu chưa có (import đủ các module để đăng ký metadata)
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Tables ensured\n")
    except Exception as e:
        print(f"⚠ create_all warning: {e}\n")

    if args.wipe or args.drop:
        print("⚠  Wiping existing data...")
        wipe_new_tables(engine)
        print()

    with Session(engine) as db:
        try:
            print("► Seeding Users...")
            users = seed_users(db)

            print("\n► Seeding Homes...")
            homes = seed_homes(db, users)

            print("\n► Seeding Home Members...")
            seed_home_members(db, users, homes)

            print("\n► Seeding Rooms...")
            rooms = seed_rooms(db, homes)

            print("\n► Seeding Devices...")
            devices = seed_devices(db, rooms, homes)

            print("\n► Seeding Device Logs (30 days)...")
            seed_device_logs(db, devices)

            print("\n► Seeding Energy Logs (30 days)...")
            seed_energy_logs(db, devices)

            print("\n► Seeding Automations...")
            seed_automations(db, homes, devices)

            print("\n► Seeding Security Events...")
            seed_security_events(db, homes)

            print("\n► Seeding Suggestion Logs...")
            seed_suggestion_logs(db, users)

            db.commit()
            print(f"\n{'='*60}")
            print("  ✅ Seed hoàn thành!")
            print(f"{'='*60}")
            print("\nAccounts để test:")
            print("  📧 admin@demo.local   / Admin@123456  (ADMIN - owner Home 1)")
            print("  📧 member@demo.local  / Member@123    (MEMBER - Home 1 & Home 2)")
            print("  📧 guest@demo.local   / Guest@123     (MEMBER - Home 2)")
            print("  📧 owner2@demo.local  / Owner2@123    (ADMIN - owner Home 2)")
            print()

        except Exception as e:
            db.rollback()
            print(f"\n❌ Seed thất bại: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()
