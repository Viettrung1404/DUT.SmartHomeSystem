from src.entities.models import Device, DeviceLog, Room, HomeUser

from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.exceptions import DeviceNotFoundError, DeviceOfflineError, ForbiddenError, RoomNotFoundError
from src.mqtt_client import publish_device_command
from . import models
import logging

def _check_device_access(db: Session, device: Device, user_id: UUID):
    room = db.query(Room).filter(Room.id == device.room_id).first()
    if not room:
        raise RoomNotFoundError()
    member = db.query(HomeUser).filter(
        HomeUser.home_id == room.home_id, HomeUser.user_id == user_id
    ).first()
    if not member:
        raise ForbiddenError("Bạn không có quyền truy cập thiết bị này")

def create_device(db: Session, user_id: UUID, data: models.DeviceCreate) -> Device:
    room = db.query(Room).filter(Room.id == UUID(data.room_id)).first()
    if not room:
        raise RoomNotFoundError()
    member = db.query(HomeUser).filter(
        HomeUser.home_id == room.home_id, HomeUser.user_id == user_id
    ).first()
    if not member:
        raise ForbiddenError("Bạn không có quyền thêm thiết bị")

    device = Device(
        room_id=room.id, name=data.name, type=data.type.upper(),
        config=data.metadata or {}
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    
    from src.entities.models import DeviceState
    d_state = DeviceState(device_id=device.id, is_online=False, state={})
    db.add(d_state)
    db.commit()
    db.refresh(device)
    return device

def get_devices_by_room(db: Session, room_id: UUID, user_id: UUID) -> list[Device]:
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise RoomNotFoundError(room_id)
    member = db.query(HomeUser).filter(
        HomeUser.home_id == room.home_id, HomeUser.user_id == user_id
    ).first()
    if not member:
        raise ForbiddenError("Bạn không có quyền truy cập phòng này")
    return db.query(Device).filter(Device.room_id == room_id).all()

def get_device(db: Session, device_id: UUID, user_id: UUID) -> Device:
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise DeviceNotFoundError(device_id)
    _check_device_access(db, device, user_id)
    return device

def toggle_device(db: Session, device_id: UUID, user_id: UUID, data: models.DeviceToggleRequest) -> Device:
    from sqlalchemy.orm.attributes import flag_modified
    device = get_device(db, device_id, user_id)
    if not device.state or not device.state.is_online:
        raise DeviceOfflineError(device_id)

    if device.state is None:
        device.state = DeviceState(device_id=device.id, is_online=True, state={})

    device.state.state["power"] = "ON" if data.status else "OFF"
    device.state.last_updated = datetime.now(timezone.utc)
    flag_modified(device.state, "state")

    # Log action
    log = DeviceLog(id=uuid4(), device_id=device.id, action='toggle', value=str(data.status))
    db.add(log)
    db.commit()
    db.refresh(device)

    # Publish MQTT command using explicit device-aware verbs
    try:
        device_type = str(device.type).lower()
        if device_type in {"lock", "door", "curtain"}:
            command = "open" if data.status else "close"
            publish_device_command(str(device_id), command)
        else:
            command = "turn_on" if data.status else "turn_off"
            publish_device_command(str(device_id), command)
    except Exception as e:
        logging.warning(f"MQTT publish failed: {e}")

    return device

def send_command(db: Session, device_id: UUID, user_id: UUID, data: models.DeviceCommandRequest) -> Device:
    from sqlalchemy.orm.attributes import flag_modified
    device = get_device(db, device_id, user_id)
    if not device.state or not device.state.is_online:
        raise DeviceOfflineError(device_id)

    # Update metadata based on command
    metadata = device.state.state or {}
    if data.command == 'set_brightness':
        metadata['brightness'] = data.value
    elif data.command == 'set_temperature':
        metadata['targetTemp'] = data.value
    elif data.command == 'set_mode':
        metadata['mode'] = data.value
    elif data.command in ('lock', 'unlock'):
        metadata['isLocked'] = data.command == 'lock'

    device.state.state = metadata
    device.state.last_updated = datetime.now(timezone.utc)
    flag_modified(device.state, "state")

    # Log
    log = DeviceLog(id=uuid4(), device_id=device.id, action=data.command, value=str(data.value))
    db.add(log)
    db.commit()
    db.refresh(device)

    # MQTT
    try:
        publish_device_command(str(device_id), data.command, data.value)
    except Exception as e:
        logging.warning(f"MQTT publish failed: {e}")

    return device

def update_device(db: Session, device_id: UUID, user_id: UUID, data: models.DeviceUpdate) -> Device:
    device = get_device(db, device_id, user_id)

    if data.room_id:
        target_room = db.query(Room).filter(Room.id == UUID(data.room_id)).first()
        if not target_room:
            raise RoomNotFoundError(data.room_id)
        member = db.query(HomeUser).filter(
            HomeUser.home_id == target_room.home_id, HomeUser.user_id == user_id
        ).first()
        if not member:
            raise ForbiddenError("Bạn không có quyền chuyển thiết bị sang phòng này")
        device.room_id = target_room.id

    if data.name is not None:
        device.name = data.name
    if data.type is not None:
        device.type = data.type.upper()
    if data.metadata is not None:
        device.config = data.metadata
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(device, "config")

    db.commit()
    db.refresh(device)
    return device

def delete_device(db: Session, device_id: UUID, user_id: UUID) -> None:
    device = get_device(db, device_id, user_id)
    db.delete(device)
    db.commit()

def to_response(device: Device) -> models.DeviceResponse:
    state = device.state
    status_bool = False
    is_online = False
    last_seen = None
    meta = device.config or {}
    
    if state:
        is_online = state.is_online
        status_bool = state.state.get("power", "OFF") == "ON"
        last_seen = state.last_updated
        meta.update(state.state)

    return models.DeviceResponse(
        id=str(device.id),
        room_id=str(device.room_id),
        name=device.name,
        type=device.type,
        status=status_bool,
        online_status=is_online,
        last_seen=last_seen,
        metadata=meta,
        created_at=device.created_at,
    )
