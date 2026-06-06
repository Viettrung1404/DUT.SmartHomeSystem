import logging
import re
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from src.entities.models import Device, DeviceLog, DeviceState, DeviceType, HomeUser, Room, TriggerSource
from src.exceptions import DeviceNotFoundError, DeviceOfflineError, ForbiddenError, RoomNotFoundError
from src.mqtt_client import publish_device_command
from src.services.activity_logger import record_device_power_transition

from . import models

ENUM_DEVICE_TYPES = {member.value.lower(): member for member in DeviceType}
DEVICE_TYPE_ALIASES = {
    "door": "lock",
    "curtain": "lock",
    "buzzer": "sensor",
    "distance_light": "sensor",
    "temperature_humidity": "sensor",
    "distance_sensor": "sensor",
    "gas_sensor": "sensor",
    "rain_sensor": "sensor",
    "rain_servo": "sensor",
}
SPECIALIZED_KINDS = set(DEVICE_TYPE_ALIASES)


def _device_type_value(device: Device) -> str:
    return str(getattr(getattr(device, "type", None), "value", device.type)).strip().lower()


def _device_kind(device: Device) -> str:
    config = device.config if isinstance(device.config, dict) else {}
    kind = str(config.get("kind") or "").strip().lower()
    return kind or _device_type_value(device)


def _is_archived_config(config: dict | None) -> bool:
    return bool(isinstance(config, dict) and config.get("archived"))


def _is_archived_device(device: Device) -> bool:
    return _is_archived_config(device.config if isinstance(device.config, dict) else {})


def _slugify_device_name(name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return base or "device"


def _generate_unique_slug(db: Session, name: str) -> str:
    base_slug = _slugify_device_name(name)
    candidate = base_slug
    counter = 2
    while db.query(Device).filter(Device.slug == candidate).first():
        candidate = f"{base_slug}-{counter}"
        counter += 1
    return candidate


def _normalize_device_payload(device_type: str, metadata: dict | None) -> tuple[DeviceType, dict]:
    requested_type = str(device_type or "").strip().lower() or "sensor"
    normalized_config = dict(metadata or {})
    base_type = DEVICE_TYPE_ALIASES.get(requested_type, requested_type)
    enum_type = ENUM_DEVICE_TYPES.get(base_type)

    if enum_type is None:
        normalized_config.setdefault("kind", requested_type)
        enum_type = DeviceType.SENSOR
    elif requested_type in SPECIALIZED_KINDS:
        normalized_config.setdefault("kind", requested_type)

    return enum_type, normalized_config


def _apply_power_state(metadata: dict, *, is_on: bool) -> None:
    metadata["power"] = "ON" if is_on else "OFF"


def _apply_door_like_state(kind: str, metadata: dict, *, is_open: bool) -> None:
    if kind in {"door", "lock"}:
        metadata["door"] = "open" if is_open else "closed"
    if kind == "lock":
        metadata["isLocked"] = not is_open
    if kind == "curtain":
        metadata["position"] = "open" if is_open else "closed"


def _coerce_type_for_response(device: Device, metadata: dict) -> str:
    kind = str(metadata.get("kind") or "").strip().lower()
    if kind:
        return kind
    return _device_type_value(device)


def _check_device_access(db: Session, device: Device, user_id: UUID):
    room = db.query(Room).filter(Room.id == device.room_id).first()
    if not room or not getattr(room, "is_active", True):
        raise RoomNotFoundError()
    member = db.query(HomeUser).filter(
        HomeUser.home_id == room.home_id, HomeUser.user_id == user_id
    ).first()
    if not member:
        raise ForbiddenError("Ban khong co quyen truy cap thiet bi nay")


def create_device(db: Session, user_id: UUID, data: models.DeviceCreate) -> Device:
    room = db.query(Room).filter(Room.id == UUID(data.room_id)).first()
    if not room or not getattr(room, "is_active", True):
        raise RoomNotFoundError()
    member = db.query(HomeUser).filter(
        HomeUser.home_id == room.home_id, HomeUser.user_id == user_id
    ).first()
    if not member:
        raise ForbiddenError("Ban khong co quyen them thiet bi")

    normalized_type, normalized_config = _normalize_device_payload(data.type, data.metadata)
    slug = _generate_unique_slug(db, data.name)
    device = Device(
        room_id=room.id,
        name=data.name,
        type=normalized_type,
        slug=slug,
        mqtt_topic=f"device/{slug}",
        config=normalized_config,
    )

    initial_state: dict[str, object] = {}
    kind = str(normalized_config.get("kind") or "").strip().lower()
    if kind in {"door", "lock", "curtain"}:
        _apply_door_like_state(kind, initial_state, is_open=False)
    if kind == "buzzer":
        initial_state["buzzer"] = "off"
    if kind == "rain_servo":
        initial_state["angle"] = normalized_config.get("angle", 0)

    db.add(device)
    db.flush()
    db.add(DeviceState(device_id=device.id, is_online=False, state=initial_state))
    db.commit()
    db.refresh(device)
    return device


def get_devices_by_room(db: Session, room_id: UUID, user_id: UUID) -> list[Device]:
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room or not getattr(room, "is_active", True):
        raise RoomNotFoundError(room_id)
    member = db.query(HomeUser).filter(
        HomeUser.home_id == room.home_id, HomeUser.user_id == user_id
    ).first()
    if not member:
        raise ForbiddenError("Ban khong co quyen truy cap phong nay")
    devices = db.query(Device).filter(Device.room_id == room_id).all()
    return [device for device in devices if not _is_archived_device(device)]


def get_device(db: Session, device_id: UUID, user_id: UUID) -> Device:
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device or _is_archived_device(device):
        raise DeviceNotFoundError(device_id)
    _check_device_access(db, device, user_id)
    return device


def toggle_device(db: Session, device_id: UUID, user_id: UUID, data: models.DeviceToggleRequest) -> Device:
    device = get_device(db, device_id, user_id)
    if not device.state or not device.state.is_online:
        raise DeviceOfflineError(device_id)

    old_state = dict(device.state.state or {})
    next_state = dict(device.state.state or {})
    kind = _device_kind(device)
    _apply_power_state(next_state, is_on=data.status)
    if kind in {"door", "lock", "curtain"}:
        _apply_door_like_state(kind, next_state, is_open=data.status)

    device.state.state = next_state
    device.state.last_updated = datetime.now(timezone.utc)
    flag_modified(device.state, "state")
    room = db.query(Room).filter(Room.id == device.room_id).first()
    record_device_power_transition(
        db,
        device=device,
        old_state=old_state,
        new_state=next_state,
        trigger_source=TriggerSource.USER,
        user_id=user_id,
        home_id=room.home_id if room else None,
    )

    db.add(DeviceLog(id=uuid4(), device_id=device.id, action="toggle", value=str(data.status)))
    db.commit()
    db.refresh(device)

    try:
        if kind in {"lock", "door", "curtain"}:
            command = "open" if data.status else "close"
        else:
            command = "turn_on" if data.status else "turn_off"
        publish_device_command(str(device_id), command)
    except Exception as exc:
        logging.warning("MQTT publish failed: %s", exc)

    return device


def send_command(db: Session, device_id: UUID, user_id: UUID, data: models.DeviceCommandRequest) -> Device:
    device = get_device(db, device_id, user_id)
    if not device.state or not device.state.is_online:
        raise DeviceOfflineError(device_id)

    old_state = dict(device.state.state or {})
    metadata = dict(device.state.state or {})
    command = str(data.command or "").strip().lower()
    kind = _device_kind(device)

    if command == "set_brightness":
        metadata["brightness"] = data.value
    elif command == "set_temperature":
        metadata["targetTemp"] = data.value
    elif command == "set_mode":
        metadata["mode"] = data.value
    elif command == "set_speed":
        metadata["speed"] = str(data.value) if data.value is not None else "off"
        _apply_power_state(metadata, is_on=str(metadata["speed"]).lower() != "off")
    elif command in {"lock", "unlock"}:
        metadata["isLocked"] = command == "lock"
        metadata["door"] = "closed" if command == "lock" else "open"
        _apply_power_state(metadata, is_on=command == "unlock")
    elif command == "set_position":
        metadata["position"] = data.value
    elif command == "set_angle":
        metadata["angle"] = data.value
    elif command in {"turn_on", "on"}:
        _apply_power_state(metadata, is_on=True)
    elif command in {"turn_off", "off"}:
        _apply_power_state(metadata, is_on=False)
    elif command == "open":
        _apply_power_state(metadata, is_on=True)
        _apply_door_like_state(kind, metadata, is_open=True)
    elif command == "close":
        _apply_power_state(metadata, is_on=False)
        _apply_door_like_state(kind, metadata, is_open=False)

    device.state.state = metadata
    device.state.last_updated = datetime.now(timezone.utc)
    flag_modified(device.state, "state")
    room = db.query(Room).filter(Room.id == device.room_id).first()
    record_device_power_transition(
        db,
        device=device,
        old_state=old_state,
        new_state=metadata,
        trigger_source=TriggerSource.USER,
        user_id=user_id,
        home_id=room.home_id if room else None,
    )

    db.add(DeviceLog(id=uuid4(), device_id=device.id, action=command, value=str(data.value)))
    db.commit()
    db.refresh(device)

    try:
        publish_device_command(str(device_id), command, data.value)
    except Exception as exc:
        logging.warning("MQTT publish failed: %s", exc)

    return device


def update_device(db: Session, device_id: UUID, user_id: UUID, data: models.DeviceUpdate) -> Device:
    device = get_device(db, device_id, user_id)

    if data.room_id:
        target_room = db.query(Room).filter(Room.id == UUID(data.room_id)).first()
        if not target_room or not getattr(target_room, "is_active", True):
            raise RoomNotFoundError(data.room_id)
        member = db.query(HomeUser).filter(
            HomeUser.home_id == target_room.home_id, HomeUser.user_id == user_id
        ).first()
        if not member:
            raise ForbiddenError("Ban khong co quyen chuyen thiet bi sang phong nay")
        device.room_id = target_room.id

    if data.name is not None:
        device.name = data.name
    if data.type is not None or data.metadata is not None:
        requested_type = data.type or _coerce_type_for_response(device, dict(device.config or {}))
        normalized_type, normalized_config = _normalize_device_payload(
            requested_type,
            data.metadata if data.metadata is not None else dict(device.config or {}),
        )
        device.type = normalized_type
        device.config = normalized_config
        flag_modified(device, "config")

    db.commit()
    db.refresh(device)
    return device


def delete_device(db: Session, device_id: UUID, user_id: UUID) -> None:
    device = get_device(db, device_id, user_id)
    config = dict(device.config or {})
    config["archived"] = True
    config["archived_at"] = datetime.now(timezone.utc).isoformat()
    device.config = config
    flag_modified(device, "config")

    if device.state:
        next_state = dict(device.state.state or {})
        _apply_power_state(next_state, is_on=False)
        kind = _device_kind(device)
        if kind in {"door", "lock", "curtain"}:
            _apply_door_like_state(kind, next_state, is_open=False)
        device.state.is_online = False
        device.state.state = next_state
        device.state.last_updated = datetime.now(timezone.utc)
        flag_modified(device.state, "state")

    db.commit()


def to_response(device: Device) -> models.DeviceResponse:
    state = device.state
    status_bool = False
    is_online = False
    last_seen = None
    meta = dict(device.config or {})

    if state:
        is_online = state.is_online
        status_bool = state.state.get("power", "OFF") == "ON"
        last_seen = state.last_updated
        meta.update(state.state)

    if isinstance(meta, dict) and meta.get("kind") == "rain_servo":
        meta.pop("door", None)
        meta.pop("isLocked", None)

    return models.DeviceResponse(
        id=str(device.id),
        room_id=str(device.room_id),
        name=device.name,
        type=_coerce_type_for_response(device, meta),
        status=status_bool,
        online_status=is_online,
        last_seen=last_seen,
        metadata=meta,
        created_at=device.created_at,
    )
