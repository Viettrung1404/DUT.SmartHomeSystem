from src.entities.models import Home, HomeUser, Room, Device, User

from uuid import UUID, uuid4
from sqlalchemy.orm import Session

from src.exceptions import HomeNotFoundError, ForbiddenError, UserNotFoundError
from . import models
import logging

def create_home(db: Session, user_id: UUID, data: models.HomeCreate) -> Home:
    home = Home(id=uuid4(), name=data.name, address=data.address)
    db.add(home)
    # Auto-add owner as member
    member = HomeUser(home_id=home.id, user_id=user_id, role='ADMIN')
    db.add(member)
    db.commit()
    db.refresh(home)
    return home

def get_user_homes(db: Session, user_id: UUID) -> list[Home]:
    member_homes = db.query(HomeUser).filter(HomeUser.user_id == user_id).all()
    home_ids = [m.home_id for m in member_homes]
    return db.query(Home).filter(Home.id.in_(home_ids)).all()

def get_home(db: Session, home_id: UUID, user_id: UUID) -> Home:
    home = db.query(Home).filter(Home.id == home_id).first()
    if not home:
        raise HomeNotFoundError(home_id)
    _check_home_access(db, home_id, user_id)
    return home

def _is_owner(db: Session, home_id: UUID, user_id: UUID) -> bool:
    member = db.query(HomeUser).filter(
        HomeUser.home_id == home_id,
        HomeUser.user_id == user_id,
        HomeUser.role == 'ADMIN'
    ).first()
    return member is not None

def update_home(db: Session, home_id: UUID, user_id: UUID, data: models.HomeUpdate) -> Home:
    home = get_home(db, home_id, user_id)
    if not _is_owner(db, home_id, user_id):
        raise ForbiddenError("Chỉ chủ sở hữu mới có quyền sửa")
    if data.name is not None:
        home.name = data.name
    if data.address is not None:
        home.address = data.address
    db.commit()
    db.refresh(home)
    return home

def delete_home(db: Session, home_id: UUID, user_id: UUID) -> None:
    home = get_home(db, home_id, user_id)
    if not _is_owner(db, home_id, user_id):
        raise ForbiddenError("Chỉ chủ sở hữu mới có quyền xóa")
    db.delete(home)
    db.commit()

def get_home_stats(db: Session, home: Home) -> models.HomeResponse:
    rooms = db.query(Room).filter(Room.home_id == home.id).all()
    room_ids = [r.id for r in rooms]
    devices = db.query(Device).filter(Device.room_id.in_(room_ids)).all() if room_ids else []
    
    owner_user = db.query(HomeUser).filter(HomeUser.home_id == home.id, HomeUser.role == 'ADMIN').first()
    owner_id = str(owner_user.user_id) if owner_user else ""
    
    # Calculate active devices from device states
    active_devices = 0
    for d in devices:
        if d.state and d.state.state.get("power", "OFF") == "ON":
            active_devices += 1
            
    return models.HomeResponse(
        id=str(home.id),
        owner_id=owner_id,
        name=home.name,
        address=home.address,
        created_at=home.created_at,
        room_count=len(rooms),
        device_count=len(devices),
        active_devices=active_devices,
    )

def get_home_members(db: Session, home_id: UUID, user_id: UUID) -> list:
    _check_home_access(db, home_id, user_id)
    members = db.query(HomeUser).filter(HomeUser.home_id == home_id).all()
    result = []
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()
        if user:
            result.append(models.HomeUserResponse(
                id=str(m.id), user_id=str(m.user_id),
                email=user.email, full_name=user.full_name, role=m.role
            ))
    return result

def add_home_member(db: Session, home_id: UUID, owner_id: UUID, data: models.AddMemberRequest) -> HomeUser:
    home = get_home(db, home_id, owner_id)
    if not _is_owner(db, home_id, owner_id):
        raise ForbiddenError("Chỉ chủ sở hữu mới có quyền thêm thành viên")
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise UserNotFoundError()
    member = HomeUser(home_id=home_id, user_id=user.id, role=data.role.upper())
    db.add(member)
    db.commit()
    return member

def _check_home_access(db: Session, home_id: UUID, user_id: UUID):
    member = db.query(HomeUser).filter(
        HomeUser.home_id == home_id,
        HomeUser.user_id == user_id
    ).first()
    if not member:
        raise ForbiddenError("Bạn không có quyền truy cập nhà này")
