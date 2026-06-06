#!/usr/bin/env python3
"""Import devices from Iot/device_map.json into the backend DB.

Creates a room per device `room` key under the first Home (if not exists)
and upserts devices using the UUIDs from the file. Safe to re-run.

Usage (run from repository root):
  python backend/scripts/db/import_device_map.py
  python backend/scripts/db/import_device_map.py --path Iot/device_map.json
"""
import json
import os
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

try:
    from src.config.env import DATABASE_URL
except Exception:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/smarthome")

# NOTE: Use raw SQL upserts for devices because DB schema may vary (home_id vs room_id).
from src.entities.home import Home
# Ensure related mapped classes are imported so SQLAlchemy mappers initialize
from src.entities.device_log import DeviceLog  # noqa: F401
from src.entities.energy_log import EnergyLog  # noqa: F401
from src.entities.security_event import SecurityEvent  # noqa: F401
from src.entities.suggestion_log import SuggestionLog  # noqa: F401
from src.entities.automation import Automation, AutomationCondition, AutomationAction  # noqa: F401
from src.entities.user import User  # noqa: F401
from src.entities.home_member import HomeMember  # noqa: F401


def now_utc():
    return datetime.now(timezone.utc)


def load_map(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def upsert_devices(db: Session, data, home: Home):
    """Insert or update devices attaching them to the provided `home`.

    Uses raw SQL ON CONFLICT upsert to avoid ORM/column mismatches across DB versions.
    """
    from sqlalchemy import Table, MetaData
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    engine = db.get_bind()
    meta = MetaData()
    devices_table = Table("devices", meta, autoload_with=engine)

    for entry in data:
        dev_id = entry.get("id")
        try:
            parsed_id = str(uuid.UUID(dev_id))
        except Exception:
            parsed_id = str(uuid.uuid4())

        kind = entry.get("kind") or "unknown"
        name = entry.get("name") or f"Device {parsed_id}"
        metadata_obj = entry.get("metadata") or {}

        insert_stmt = pg_insert(devices_table).values(
            id=parsed_id,
            home_id=str(home.id),
            name=name,
            type=kind,
            status=False,
            online_status=True,
            metadata=metadata_obj,
            last_seen=now_utc(),
            created_at=now_utc(),
            updated_at=now_utc(),
        )

        update_cols = {
            "name": insert_stmt.excluded.name,
            "type": insert_stmt.excluded.type,
            "home_id": insert_stmt.excluded.home_id,
            "online_status": insert_stmt.excluded.online_status,
            "last_seen": insert_stmt.excluded.last_seen,
            "metadata": insert_stmt.excluded.metadata,
            "updated_at": insert_stmt.excluded.updated_at,
        }

        stmt = insert_stmt.on_conflict_do_update(index_elements=["id"], set_=update_cols)
        db.execute(stmt)

    db.flush()


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default=os.path.join(os.path.dirname(__file__), "..", "..", "Iot", "device_map.json"),
                        help="Path to device_map.json")
    parser.add_argument("--home-name", default=None, help="Home name to attach devices to (defaults to first home)")
    args = parser.parse_args()

    path = os.path.abspath(args.path)
    if not os.path.exists(path):
        print(f"Device map file not found: {path}")
        sys.exit(1)

    data = load_map(path)
    if not isinstance(data, list):
        print("device_map.json must be a list of device entries")
        sys.exit(1)

    engine = create_engine(DATABASE_URL)
    with Session(engine) as db:
        # Resolve home using raw SQL to avoid ORM mapper initialization issues
        from sqlalchemy import text
        if args.home_name:
            row = db.execute(
                text("SELECT id, name FROM homes WHERE name = :name ORDER BY created_at LIMIT 1"),
                {"name": args.home_name},
            ).first()
            if not row:
                print(f"Home named '{args.home_name}' not found")
                sys.exit(1)
            home = type("H", (), {"id": row[0], "name": row[1]})
        else:
            row = db.execute(
                text("SELECT id, name FROM homes ORDER BY created_at LIMIT 1"),
            ).first()
            if not row:
                print("No Home found in DB. Please create a Home first or specify --home-name")
                sys.exit(1)
            home = type("H", (), {"id": row[0], "name": row[1]})

        upsert_devices(db, data, home)
        db.commit()
        print(f"Imported {len(data)} devices into home '{home.name}'")


if __name__ == "__main__":
    main()
