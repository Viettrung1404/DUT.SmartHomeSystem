from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from src.entities.device import Device
from src.entities.device_log import DeviceLog
from src.entities.device_identity_map import DeviceIdentityMap
from src.entities.home_member import HomeMember
from src.exceptions import DeviceNotFoundError, DeviceOfflineError, ForbiddenError
from src.mqtt_client import publish_command
from . import models
import json
import logging


def _check_device_access(db: Session, device: Device, user_id: UUID):
    """Check if user has access to the device's home."""
    member = db.query(HomeMember).filter(
        HomeMember.home_id == device.home_id, HomeMember.user_id == user_id
    ).first()
    if not member:
        raise ForbiddenError("Bạn không có quyền truy cập thiết bị này")


def create_device(db: Session, user_id: UUID, data: models.DeviceCreate) -> Device:
    """Create a new device in a home."""
    home_id = UUID(data.home_id)
    member = db.query(HomeMember).filter(
        HomeMember.home_id == home_id, HomeMember.user_id == user_id
    ).first()
    if not member:
        raise ForbiddenError("Bạn không có quyền thêm thiết bị vào ngôi nhà này")

    device = Device(
        id=uuid4(), home_id=home_id, name=data.name, type=data.type,
        location=data.location, metadata_json=data.metadata or {}
    )
    db.add(device)
    db.flush()

    metadata = data.metadata or {}
    mqtt_home_key = str(metadata.get("mqtt_home_key", str(home_id))).strip()
    mqtt_device_key = str(metadata.get("mqtt_device_key", str(device.id))).strip()
    if mqtt_home_key and mqtt_device_key:
        topic_mapping = db.query(DeviceIdentityMap).filter(
            DeviceIdentityMap.home_key == mqtt_home_key,
            DeviceIdentityMap.device_key == mqtt_device_key,
        ).first()
        mapping = db.query(DeviceIdentityMap).filter(DeviceIdentityMap.device_id == device.id).first()
        if topic_mapping is not None and topic_mapping.device_id != device.id:
            raise ForbiddenError("mqtt_home_key + mqtt_device_key da duoc lien ket voi thiet bi khac")
        if mapping is None:
            db.add(
                DeviceIdentityMap(
                    id=uuid4(),
                    home_id=home_id,
                    device_id=device.id,
                    home_key=mqtt_home_key,
                    device_key=mqtt_device_key,
                )
            )
        else:
            mapping.home_id = home_id
            mapping.home_key = mqtt_home_key
            mapping.device_key = mqtt_device_key

    db.commit()
    db.refresh(device)
    return device


def get_devices_by_home(db: Session, home_id: UUID, user_id: UUID) -> list[Device]:
    """Get all devices in a home for the user."""
    member = db.query(HomeMember).filter(
        HomeMember.home_id == home_id, HomeMember.user_id == user_id
    ).first()
    if not member:
        raise ForbiddenError("Bạn không có quyền truy cập ngôi nhà này")
    return db.query(Device).filter(Device.home_id == home_id).all()


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
        publish_command("on" if data.status else "off", str(device.home_id), str(device.id))
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
        command = data.command if data.value is None else f"{data.command}:{data.value}"
        publish_command(command, str(device.home_id), str(device.id))
    except Exception as e:
        logging.warning(f"MQTT publish failed: {e}")

    return device


def to_response(device: Device) -> models.DeviceResponse:
    return models.DeviceResponse(
        id=str(device.id),
        home_id=str(device.home_id),
        name=device.name,
        type=device.type,
        location=device.location,
        status=device.status,
        online_status=device.online_status,
        last_seen=device.last_seen,
        metadata=device.metadata_json,
        created_at=device.created_at,
    )
