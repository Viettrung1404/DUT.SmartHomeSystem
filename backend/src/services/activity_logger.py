from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from src.entities.models import (
    ActivityLog,
    Device,
    EventType,
    HomeUser,
    Room,
    TriggerSource,
)


def is_power_on(state: dict | None) -> bool:
    if not isinstance(state, dict):
        return False

    power = state.get("power")
    if isinstance(power, str):
        return power.strip().upper() == "ON"
    if isinstance(power, bool):
        return power

    status = state.get("status")
    if isinstance(status, bool):
        return status
    return False


def _device_type_value(device: Device) -> str:
    return str(getattr(getattr(device, "type", ""), "value", getattr(device, "type", ""))).lower()


def _device_kind(device: Device) -> str:
    config = getattr(device, "config", None)
    if isinstance(config, dict):
        value = str(config.get("kind") or "").strip().lower()
        if value:
            return value
    return _device_type_value(device)


def should_log_activity(device: Device) -> bool:
    kind = _device_kind(device)
    if kind in {
        "sensor",
        "camera",
        "rain_sensor",
        "gas_sensor",
        "distance_sensor",
        "temperature_humidity",
        "rain_servo",
        "distance_light",
        "buzzer",
    }:
        return False
    return _device_type_value(device) in {"light", "fan", "ac", "lock"} or kind in {
        "light",
        "fan",
        "ac",
        "door",
        "lock",
    }


def get_device_home_id(db: Session, device: Device) -> UUID | None:
    if not device.room_id:
        return None
    room = db.query(Room).filter(Room.id == device.room_id).first()
    return room.home_id if room else None


def get_attributed_home_user_id(db: Session, home_id: UUID) -> UUID | None:
    membership = (
        db.query(HomeUser)
        .filter(HomeUser.home_id == home_id)
        .order_by(HomeUser.id.asc())
        .first()
    )
    return membership.user_id if membership else None


def record_device_power_transition(
    db: Session,
    *,
    device: Device,
    old_state: dict | None,
    new_state: dict | None,
    trigger_source: TriggerSource,
    user_id: UUID | None = None,
    home_id: UUID | None = None,
) -> None:
    if not should_log_activity(device):
        return

    old_is_on = is_power_on(old_state)
    new_is_on = is_power_on(new_state)
    if old_is_on == new_is_on:
        return

    resolved_home_id = home_id or get_device_home_id(db, device)
    if not resolved_home_id:
        return

    resolved_user_id = user_id
    resolved_trigger = trigger_source
    if resolved_user_id is None and trigger_source == TriggerSource.PHYSICAL_ATTRIBUTED:
        resolved_user_id = get_attributed_home_user_id(db, resolved_home_id)
        if resolved_user_id is None:
            resolved_trigger = TriggerSource.PHYSICAL_UNKNOWN

    now = datetime.now(timezone.utc)
    if new_is_on:
        db.add(
            ActivityLog(
                timestamp=now,
                event_type=EventType.DEVICE_ON,
                trigger_source=resolved_trigger,
                device_id=device.id,
                user_id=resolved_user_id,
                home_id=resolved_home_id,
                metadata_json={"source": "device_state_transition"},
            )
        )
        return

    open_log = (
        db.query(ActivityLog)
        .filter(
            ActivityLog.device_id == device.id,
            ActivityLog.home_id == resolved_home_id,
            ActivityLog.event_type == EventType.DEVICE_ON,
            ActivityLog.session_end.is_(None),
        )
        .order_by(ActivityLog.timestamp.desc())
        .first()
    )
    duration_seconds = 0
    if open_log:
        open_log.session_end = now
        started_at = open_log.timestamp
        comparable_now = now.replace(tzinfo=None) if started_at.tzinfo is None else now
        elapsed = comparable_now - started_at
        duration_seconds = max(0, int(elapsed.total_seconds()))
        open_log.duration_seconds = duration_seconds

    db.add(
        ActivityLog(
            timestamp=now,
            session_end=now,
            event_type=EventType.DEVICE_OFF,
            trigger_source=resolved_trigger,
            device_id=device.id,
            user_id=resolved_user_id,
            home_id=resolved_home_id,
            duration_seconds=duration_seconds,
            metadata_json={"source": "device_state_transition"},
        )
    )
