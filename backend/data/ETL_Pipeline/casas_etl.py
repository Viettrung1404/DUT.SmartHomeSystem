"""
ETL CASAS CSV -> SmartHome PostgreSQL
=====================================
Supports both formats:
- raw data:    date,time,sensor,state
- labeled data:date,time,sensor,state,label

Example:
  python data/ETL_Pipeline/casas_etl.py \
    --input data/dataset/data/data/aruba.csv \
    --home-name "CASAS Aruba Home" \
        --user-emails "hung@import.local,mai@import.local" \
    --reset-home-data \
    --limit 200000
"""

import argparse
import csv
import os
import re
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Add backend root to path so we can import src.entities.models
BACKEND_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(BACKEND_ROOT))

from src.entities.models import (
    ActivityLog,
    Device,
    DeviceState,
    DeviceType,
    EventType,
    Home,
    HomeUser,
    MetricType,
    Room,
    TriggerSource,
    User,
    UserRole,
)

load_dotenv(BACKEND_ROOT / ".env")

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/smarthome")
DEFAULT_TZ = "Asia/Ho_Chi_Minh"


@dataclass
class RowEvent:
    timestamp: datetime
    sensor: str
    state: str
    label: str | None


def slugify_sensor(sensor_name: str) -> str:
    value = sensor_name.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return f"casas_{value}"


def infer_room_name(sensor_name: str) -> str:
    s = sensor_name.lower()
    if "bed" in s:
        return "Phòng ngủ"
    if "kitchen" in s:
        return "Bếp"
    if "living" in s:
        return "Phòng khách"
    if "bath" in s or "toilet" in s:
        return "Phòng tắm"
    if "door" in s or "entry" in s:
        return "Lối ra vào"
    return "Khu vực chung"


def infer_device_type(sensor_name: str) -> DeviceType:
    s = sensor_name.lower()
    if "door" in s or "lock" in s:
        return DeviceType.LOCK
    if "light" in s or "lamp" in s:
        return DeviceType.LIGHT
    if "fan" in s:
        return DeviceType.FAN
    if "ac" in s or "hvac" in s:
        return DeviceType.AC
    return DeviceType.SENSOR


def parse_row(raw: list[str], tz: ZoneInfo) -> RowEvent | None:
    if len(raw) < 4:
        return None

    date_s = raw[0].strip()
    time_s = raw[1].strip()
    sensor = raw[2].strip()
    state = raw[3].strip().upper()
    label = raw[4].strip() if len(raw) >= 5 and raw[4].strip() else None

    try:
        ts = datetime.fromisoformat(f"{date_s} {time_s}").replace(tzinfo=tz)
    except ValueError:
        return None

    if state not in {"ON", "OFF", "OPEN", "CLOSE", "PRESENT", "ABSENT"}:
        return None

    return RowEvent(timestamp=ts, sensor=sensor, state=state, label=label)


def map_event_type(state: str) -> EventType:
    if state in {"ON", "OPEN", "PRESENT"}:
        return EventType.DEVICE_ON
    return EventType.DEVICE_OFF


def ensure_home_users(session: Session, home_name: str, user_emails: list[str], tz_name: str) -> tuple[Home, list[User]]:
    home = session.execute(
        text("SELECT id, name, timezone FROM homes WHERE name = :name LIMIT 1"),
        {"name": home_name},
    ).fetchone()

    if home:
        home_obj = session.get(Home, home.id)
    else:
        home_obj = Home(name=home_name, timezone=tz_name, is_active=True)
        session.add(home_obj)
        session.flush()

    users: list[User] = []
    for idx, user_email in enumerate(user_emails):
        user = session.execute(
            text("SELECT id FROM users WHERE email = :email LIMIT 1"),
            {"email": user_email},
        ).fetchone()

        if user:
            user_obj = session.get(User, user.id)
        else:
            full_name = f"CASAS Resident {idx + 1}"
            user_obj = User(
                id=uuid.uuid4(),
                full_name=full_name,
                email=user_email,
                password_hash="$2b$12$CASAS_IMPORT_PLACEHOLDER",
                role=UserRole.MEMBER,
                is_active=True,
            )
            session.add(user_obj)
            session.flush()

        link = session.execute(
            text("SELECT id FROM home_users WHERE home_id = :hid AND user_id = :uid LIMIT 1"),
            {"hid": str(home_obj.id), "uid": str(user_obj.id)},
        ).fetchone()
        if not link:
            session.add(HomeUser(home_id=home_obj.id, user_id=user_obj.id, role=UserRole.MEMBER))
            session.flush()

        users.append(user_obj)

    return home_obj, users


def ensure_device(session: Session, home_id, sensor_name: str) -> str:
    device_id = slugify_sensor(sensor_name)

    room_name = infer_room_name(sensor_name)
    room = session.execute(
        text("SELECT id FROM rooms WHERE home_id = :hid AND name = :name LIMIT 1"),
        {"hid": str(home_id), "name": room_name},
    ).fetchone()

    if room:
        room_id = room.id
    else:
        room_obj = Room(home_id=home_id, name=room_name, icon="sensor")
        session.add(room_obj)
        session.flush()
        room_id = room_obj.id

    existing = session.get(Device, device_id)
    if not existing:
        dev = Device(
            id=device_id,
            name=sensor_name,
            type=infer_device_type(sensor_name),
            mqtt_topic=f"casas/{device_id}",
            room_id=room_id,
            config={"source": "CASAS"},
        )
        session.add(dev)
        session.flush()

        state = DeviceState(device_id=device_id, is_online=True, state={"source": "CASAS"})
        session.add(state)
        session.flush()

    return device_id


def reset_home_data(session: Session, home_id):
    session.execute(
        text(
            """
            DELETE FROM suggestion_logs
            WHERE user_id IN (
                SELECT user_id FROM home_users WHERE home_id = :hid
            )
            """
        ),
        {"hid": str(home_id)},
    )
    session.execute(text("DELETE FROM user_patterns WHERE home_id = :hid"), {"hid": str(home_id)})
    session.execute(text("DELETE FROM activity_logs WHERE home_id = :hid"), {"hid": str(home_id)})
    session.flush()


def pick_user_for_event(users: list[User], evt: RowEvent) -> User:
    """
    Deterministic user assignment for single-resident CASAS stream.
    - 1 user: all records map to that user.
    - 2+ users: split by day parity to keep stable and reproducible.
    """
    if len(users) == 1:
        return users[0]

    # Deterministic hash split by (day + hour + sensor) for better balance.
    sensor_hash = sum(ord(c) for c in evt.sensor)
    idx = (evt.timestamp.toordinal() + evt.timestamp.hour + sensor_hash) % len(users)
    return users[idx]


def run_etl(input_path: Path, home_name: str, user_emails: list[str], tz_name: str, limit: int, do_reset: bool):
    tz = ZoneInfo(tz_name)
    engine = create_engine(DB_URL, echo=False)

    parsed = 0
    skipped = 0
    imported = 0
    matched_pairs = 0
    inferred_forgot = 0

    with Session(engine) as session:
        with session.begin():
            home, users = ensure_home_users(session, home_name, user_emails, tz_name)
            if do_reset:
                print(f"Reset existing logs/patterns for home {home.id} ...")
                reset_home_data(session, home.id)

            pending_on: dict[str, ActivityLog] = {}

            with input_path.open("r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                for raw in reader:
                    if limit and parsed >= limit:
                        break

                    evt = parse_row(raw, tz)
                    parsed += 1
                    if evt is None:
                        skipped += 1
                        continue

                    user = pick_user_for_event(users, evt)

                    device_id = ensure_device(session, home.id, evt.sensor)
                    evt_type = map_event_type(evt.state)

                    if evt_type == EventType.DEVICE_ON:
                        prev = pending_on.get(device_id)
                        if prev is not None and prev.session_end is None:
                            prev.event_type = EventType.FORGOT_OFF
                            prev.metadata_json = {
                                **(prev.metadata_json or {}),
                                "inferred": "FORGOT_OFF",
                            }
                            inferred_forgot += 1

                        on_log = ActivityLog(
                            timestamp=evt.timestamp,
                            session_end=None,
                            duration_seconds=None,
                            event_type=EventType.DEVICE_ON,
                            trigger_source=TriggerSource.SENSOR,
                            device_id=device_id,
                            user_id=user.id,
                            home_id=home.id,
                            description=f"CASAS sensor {evt.sensor} {evt.state}",
                            metadata_json={
                                "source": "CASAS",
                                "sensor": evt.sensor,
                                "sensor_state": evt.state,
                                "activity_label": evt.label,
                            },
                        )
                        session.add(on_log)
                        pending_on[device_id] = on_log
                        imported += 1

                    else:
                        off_log = ActivityLog(
                            timestamp=evt.timestamp,
                            session_end=None,
                            duration_seconds=0,
                            event_type=EventType.DEVICE_OFF,
                            trigger_source=TriggerSource.SENSOR,
                            device_id=device_id,
                            user_id=user.id,
                            home_id=home.id,
                            description=f"CASAS sensor {evt.sensor} {evt.state}",
                            metadata_json={
                                "source": "CASAS",
                                "sensor": evt.sensor,
                                "sensor_state": evt.state,
                                "activity_label": evt.label,
                            },
                        )
                        session.add(off_log)
                        imported += 1

                        on_log = pending_on.get(device_id)
                        if on_log is not None and on_log.timestamp <= evt.timestamp:
                            duration = int((evt.timestamp - on_log.timestamp).total_seconds())
                            on_log.session_end = evt.timestamp
                            on_log.duration_seconds = max(0, duration)
                            matched_pairs += 1
                            pending_on.pop(device_id, None)

            # Convert remaining open sessions to FORGOT_OFF for richer anomaly signals.
            for device_id, on_log in pending_on.items():
                if on_log.session_end is None and on_log.event_type == EventType.DEVICE_ON:
                    on_log.event_type = EventType.FORGOT_OFF
                    on_log.metadata_json = {
                        **(on_log.metadata_json or {}),
                        "inferred": "FORGOT_OFF",
                        "reason": "No OFF event found in source stream",
                    }
                    inferred_forgot += 1

    print("\nETL completed")
    print(f"Input file        : {input_path}")
    print(f"Rows read         : {parsed}")
    print(f"Rows skipped      : {skipped}")
    print(f"Logs inserted     : {imported}")
    print(f"ON/OFF matched    : {matched_pairs}")
    print(f"FORGOT_OFF inferred: {inferred_forgot}")
    print("Users mapped      :", ", ".join(user_emails))


def main():
    parser = argparse.ArgumentParser(description="ETL CASAS CSV into SmartHome activity_logs")
    parser.add_argument(
        "--input",
        default="data/dataset/data/data/aruba.csv",
        help="Path to CASAS csv file (raw or labeled)",
    )
    parser.add_argument("--home-name", default="CASAS Aruba Home")
    parser.add_argument(
        "--user-email",
        default="aruba@import.local",
        help="Single user email (backward compatible)",
    )
    parser.add_argument(
        "--user-emails",
        default="",
        help="Comma-separated list of user emails (e.g. hung@x.local,mai@x.local)",
    )
    parser.add_argument("--timezone", default=DEFAULT_TZ)
    parser.add_argument("--limit", type=int, default=0, help="Max rows to import (0 = all)")
    parser.add_argument("--reset-home-data", action="store_true", help="Delete prior logs/patterns for this home")

    args = parser.parse_args()
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = (BACKEND_ROOT / input_path).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    user_emails = [x.strip() for x in args.user_emails.split(",") if x.strip()]
    if not user_emails:
        user_emails = [args.user_email]

    run_etl(
        input_path=input_path,
        home_name=args.home_name,
        user_emails=user_emails,
        tz_name=args.timezone,
        limit=args.limit,
        do_reset=args.reset_home_data,
    )


if __name__ == "__main__":
    main()
