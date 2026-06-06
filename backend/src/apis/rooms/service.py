from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from src.entities.models import Device, EnergyLog, HomeUser, Room
from src.exceptions import ForbiddenError, RoomNotFoundError

from . import models


def _is_archived_device(device: Device) -> bool:
    return bool(isinstance(device.config, dict) and device.config.get("archived"))


def _is_active_room(room: Room) -> bool:
    return bool(getattr(room, "is_active", True))


def _archive_device(device: Device) -> None:
    config = dict(device.config or {})
    config["archived"] = True
    config["archived_at"] = datetime.now(timezone.utc).isoformat()
    device.config = config
    flag_modified(device, "config")

    if device.state:
        next_state = dict(device.state.state or {})
        next_state["power"] = "OFF"
        if config.get("kind") in {"door", "lock"}:
            next_state["door"] = "closed"
        if config.get("kind") == "curtain":
            next_state["position"] = "closed"
        device.state.is_online = False
        device.state.state = next_state
        device.state.last_updated = datetime.now(timezone.utc)
        flag_modified(device.state, "state")


def _check_home_access(db: Session, home_id: UUID, user_id: UUID):
    member = db.query(HomeUser).filter(
        HomeUser.home_id == home_id, HomeUser.user_id == user_id
    ).first()
    if not member:
        raise ForbiddenError("Ban khong co quyen truy cap nha nay")


def create_room(db: Session, user_id: UUID, data: models.RoomCreate) -> Room:
    home_id = UUID(data.home_id)
    _check_home_access(db, home_id, user_id)
    room = Room(id=uuid4(), home_id=home_id, name=data.name, icon=data.icon, is_active=True)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def get_rooms_by_home(db: Session, home_id: UUID, user_id: UUID) -> list[Room]:
    _check_home_access(db, home_id, user_id)
    rooms = db.query(Room).filter(Room.home_id == home_id).all()
    return [room for room in rooms if _is_active_room(room)]


def get_room(db: Session, room_id: UUID, user_id: UUID) -> Room:
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room or not _is_active_room(room):
        raise RoomNotFoundError(room_id)
    _check_home_access(db, room.home_id, user_id)
    return room


def update_room(db: Session, room_id: UUID, user_id: UUID, data: models.RoomUpdate) -> Room:
    room = get_room(db, room_id, user_id)
    if data.name is not None:
        room.name = data.name
    if data.icon is not None:
        room.icon = data.icon
    db.commit()
    db.refresh(room)
    return room


def delete_room(db: Session, room_id: UUID, user_id: UUID) -> None:
    room = get_room(db, room_id, user_id)
    room.is_active = False
    room.archived_at = datetime.now(timezone.utc)

    devices = db.query(Device).filter(Device.room_id == room.id).all()
    for device in devices:
        if _is_archived_device(device):
            continue
        _archive_device(device)

    db.commit()


def get_room_response(db: Session, room: Room) -> models.RoomResponse:
    devices = [
        device
        for device in db.query(Device).filter(Device.room_id == room.id).all()
        if not _is_archived_device(device)
    ]
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    device_ids = [device.id for device in devices]
    energy_today = 0.0
    if device_ids:
        result = db.query(func.sum(EnergyLog.power_usage)).filter(
            EnergyLog.device_id.in_(device_ids),
            EnergyLog.timestamp >= today_start,
        ).scalar()
        energy_today = result or 0.0

    all_online = all(device.state.is_online for device in devices if device.state) if devices else True

    active_count = 0
    for device in devices:
        if device.state and device.state.state and device.state.state.get("power", "OFF") == "ON":
            active_count += 1

    return models.RoomResponse(
        id=str(room.id),
        home_id=str(room.home_id),
        name=room.name,
        icon=room.icon,
        created_at=room.created_at,
        device_count=len(devices),
        active_devices=active_count,
        energy_today=round(energy_today, 2),
        is_online=all_online,
    )
