from src.entities.models import Room, Device, EnergyLog, HomeUser

from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.exceptions import RoomNotFoundError, ForbiddenError
from . import models

def _check_home_access(db: Session, home_id: UUID, user_id: UUID):
    member = db.query(HomeUser).filter(
        HomeUser.home_id == home_id, HomeUser.user_id == user_id
    ).first()
    if not member:
        raise ForbiddenError("Bạn không có quyền truy cập nhà này")

def create_room(db: Session, user_id: UUID, data: models.RoomCreate) -> Room:
    home_id = UUID(data.home_id)
    _check_home_access(db, home_id, user_id)
    room = Room(id=uuid4(), home_id=home_id, name=data.name, icon=data.icon)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

def get_rooms_by_home(db: Session, home_id: UUID, user_id: UUID) -> list[Room]:
    _check_home_access(db, home_id, user_id)
    return db.query(Room).filter(Room.home_id == home_id).all()

def get_room(db: Session, room_id: UUID, user_id: UUID) -> Room:
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
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
    db.delete(room)
    db.commit()

def get_room_response(db: Session, room: Room) -> models.RoomResponse:
    devices = db.query(Device).filter(Device.room_id == room.id).all()
    # Energy today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    device_ids = [d.id for d in devices]
    energy_today = 0.0
    if device_ids:
        result = db.query(func.sum(EnergyLog.power_usage)).filter(
            EnergyLog.device_id.in_(device_ids),
            EnergyLog.timestamp >= today_start
        ).scalar()
        energy_today = result or 0.0

    all_online = all(d.state.is_online for d in devices if d.state) if devices else True

    active_count = 0
    for d in devices:
        if d.state and d.state.state and d.state.state.get("power", "OFF") == "ON":
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
