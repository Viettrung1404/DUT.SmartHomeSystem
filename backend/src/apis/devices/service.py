from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from src.entities.device import Device
from src.entities.device_log import DeviceLog
from src.entities.room import Room
from src.entities.home_member import HomeMember
from src.exceptions import DeviceNotFoundError, DeviceOfflineError, ForbiddenError, RoomNotFoundError
from src.mqtt_client import publish_command
from . import models
import json
import logging


def _check_device_access(db: Session, device: Device, user_id: UUID):
    room = db.query(Room).filter(Room.id == device.room_id).first()
    if not room:
        raise RoomNotFoundError()
    member = db.query(HomeMember).filter(
        HomeMember.home_id == room.home_id, HomeMember.user_id == user_id
    ).first()
    if not member:
        raise ForbiddenError("Bạn không có quyền truy cập thiết bị này")


def create_device(db: Session, user_id: UUID, data: models.DeviceCreate) -> Device:
    room = db.query(Room).filter(Room.id == UUID(data.room_id)).first()
    if not room:
        raise RoomNotFoundError()
    member = db.query(HomeMember).filter(
        HomeMember.home_id == room.home_id, HomeMember.user_id == user_id
    ).first()
    if not member:
        raise ForbiddenError("Bạn không có quyền thêm thiết bị")

    device = Device(
        id=uuid4(), room_id=room.id, name=data.name, type=data.type,
        metadata_json=data.metadata or {}
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def get_devices_by_room(db: Session, room_id: UUID, user_id: UUID) -> list[Device]:
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise RoomNotFoundError(room_id)
    member = db.query(HomeMember).filter(
        HomeMember.home_id == room.home_id, HomeMember.user_id == user_id
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
    device = get_device(db, device_id, user_id)
    if not device.online_status:
        raise DeviceOfflineError(device_id)

    device.status = data.status
    device.last_seen = datetime.now(timezone.utc)

    # Log action
    log = DeviceLog(id=uuid4(), device_id=device.id, action='toggle', value=str(data.status))
    db.add(log)
    db.commit()
    db.refresh(device)

    # Publish MQTT command
    try:
        mqtt_payload = json.dumps({"device_id": str(device_id), "command": "toggle", "value": data.status})
        publish_command(mqtt_payload)
    except Exception as e:
        logging.warning(f"MQTT publish failed: {e}")

    return device


def send_command(db: Session, device_id: UUID, user_id: UUID, data: models.DeviceCommandRequest) -> Device:
    device = get_device(db, device_id, user_id)
    if not device.online_status:
        raise DeviceOfflineError(device_id)

    # Update metadata based on command
    metadata = device.metadata_json or {}
    if data.command == 'set_brightness':
        metadata['brightness'] = data.value
    elif data.command == 'set_temperature':
        metadata['targetTemp'] = data.value
    elif data.command == 'set_mode':
        metadata['mode'] = data.value
    elif data.command in ('lock', 'unlock'):
        metadata['isLocked'] = data.command == 'lock'

    device.metadata_json = metadata
    device.last_seen = datetime.now(timezone.utc)

    # Log
    log = DeviceLog(id=uuid4(), device_id=device.id, action=data.command, value=str(data.value))
    db.add(log)
    db.commit()
    db.refresh(device)

    # MQTT
    try:
        mqtt_payload = json.dumps({"device_id": str(device_id), "command": data.command, "value": data.value})
        publish_command(mqtt_payload)
    except Exception as e:
        logging.warning(f"MQTT publish failed: {e}")

    return device


def to_response(device: Device) -> models.DeviceResponse:
    return models.DeviceResponse(
        id=str(device.id),
        room_id=str(device.room_id),
        name=device.name,
        type=device.type,
        status=device.status,
        online_status=device.online_status,
        last_seen=device.last_seen,
        metadata=device.metadata_json,
        created_at=device.created_at,
    )
