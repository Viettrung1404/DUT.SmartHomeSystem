from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from src.entities.models import (
    ActivityLog,
    Automation,
    AutomationAction,
    AutomationCondition,
    Device,
    DeviceLog,
    DeviceState,
    EnergyLog,
    Home,
    HomeUser,
    Room,
    Schedule,
    SecurityEvent,
    SuggestionDecisionLog,
    SuggestionFeedbackLog,
    SuggestionLog,
    User,
    UserPattern,
    UserPresence,
)
from src.exceptions import ForbiddenError, HomeNotFoundError, UserNotFoundError

from . import models

def _is_archived_device(device: Device) -> bool:
    return bool(isinstance(device.config, dict) and device.config.get("archived"))

def _is_active_room(room: Room) -> bool:
    return bool(getattr(room, "is_active", True))


def create_home(db: Session, user_id: UUID, data: models.HomeCreate) -> Home:
    home = Home(id=uuid4(), name=data.name, address=data.address)
    db.add(home)
    db.add(HomeUser(home_id=home.id, user_id=user_id, role="ADMIN"))
    db.commit()
    db.refresh(home)
    return home


def get_user_homes(db: Session, user_id: UUID) -> list[Home]:
    member_homes = db.query(HomeUser).filter(HomeUser.user_id == user_id).all()
    home_ids = [membership.home_id for membership in member_homes]
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
        HomeUser.role == "ADMIN",
    ).first()
    return member is not None


def update_home(db: Session, home_id: UUID, user_id: UUID, data: models.HomeUpdate) -> Home:
    home = get_home(db, home_id, user_id)
    if not _is_owner(db, home_id, user_id):
        raise ForbiddenError("Chi chu so huu moi co quyen sua")
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
        raise ForbiddenError("Chi chu so huu moi co quyen xoa")

    room_ids = [room_id for (room_id,) in db.query(Room.id).filter(Room.home_id == home_id).all()]
    device_ids = [device_id for (device_id,) in db.query(Device.id).filter(Device.room_id.in_(room_ids)).all()] if room_ids else []
    automation_ids = [automation_id for (automation_id,) in db.query(Automation.id).filter(Automation.home_id == home_id).all()]
    pattern_ids = [pattern_id for (pattern_id,) in db.query(UserPattern.id).filter(UserPattern.home_id == home_id).all()]
    suggestion_ids = [suggestion_id for (suggestion_id,) in db.query(SuggestionLog.id).filter(SuggestionLog.pattern_id.in_(pattern_ids)).all()] if pattern_ids else []

    db.query(ActivityLog).filter(ActivityLog.home_id == home_id).delete(synchronize_session=False)
    db.query(SecurityEvent).filter(SecurityEvent.home_id == home_id).delete(synchronize_session=False)
    db.query(UserPresence).filter(UserPresence.home_id == home_id).update(
        {UserPresence.home_id: None, UserPresence.room_id: None},
        synchronize_session=False,
    )
    db.query(SuggestionDecisionLog).filter(SuggestionDecisionLog.home_id == home_id).delete(synchronize_session=False)

    if suggestion_ids:
        db.query(SuggestionFeedbackLog).filter(SuggestionFeedbackLog.suggestion_id.in_(suggestion_ids)).delete(synchronize_session=False)
        db.query(SuggestionLog).filter(SuggestionLog.id.in_(suggestion_ids)).delete(synchronize_session=False)

    if pattern_ids:
        db.query(UserPattern).filter(UserPattern.id.in_(pattern_ids)).delete(synchronize_session=False)

    if automation_ids:
        db.query(AutomationAction).filter(AutomationAction.automation_id.in_(automation_ids)).delete(synchronize_session=False)
        db.query(AutomationCondition).filter(AutomationCondition.automation_id.in_(automation_ids)).delete(synchronize_session=False)
        db.query(Automation).filter(Automation.id.in_(automation_ids)).delete(synchronize_session=False)

    if device_ids:
        db.query(Schedule).filter(Schedule.device_id.in_(device_ids)).delete(synchronize_session=False)
        db.query(DeviceLog).filter(DeviceLog.device_id.in_(device_ids)).delete(synchronize_session=False)
        db.query(EnergyLog).filter(EnergyLog.device_id.in_(device_ids)).delete(synchronize_session=False)
        db.query(DeviceState).filter(DeviceState.device_id.in_(device_ids)).delete(synchronize_session=False)
        db.query(Device).filter(Device.id.in_(device_ids)).delete(synchronize_session=False)

    if room_ids:
        db.query(Room).filter(Room.id.in_(room_ids)).delete(synchronize_session=False)

    db.query(HomeUser).filter(HomeUser.home_id == home_id).delete(synchronize_session=False)
    db.delete(home)
    db.commit()


def get_home_stats(db: Session, home: Home) -> models.HomeResponse:
    rooms = [room for room in db.query(Room).filter(Room.home_id == home.id).all() if _is_active_room(room)]
    room_ids = [room.id for room in rooms]
    devices = [device for device in db.query(Device).filter(Device.room_id.in_(room_ids)).all() if not _is_archived_device(device)] if room_ids else []

    owner_user = db.query(HomeUser).filter(HomeUser.home_id == home.id, HomeUser.role == "ADMIN").first()
    owner_id = str(owner_user.user_id) if owner_user else ""

    active_devices = 0
    for device in devices:
        if device.state and device.state.state.get("power", "OFF") == "ON":
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
    for member in members:
        user = db.query(User).filter(User.id == member.user_id).first()
        if user:
            result.append(
                models.HomeUserResponse(
                    id=str(member.id),
                    user_id=str(member.user_id),
                    email=user.email,
                    full_name=user.full_name,
                    role=member.role,
                )
            )
    return result


def add_home_member(db: Session, home_id: UUID, owner_id: UUID, data: models.AddMemberRequest) -> HomeUser:
    get_home(db, home_id, owner_id)
    if not _is_owner(db, home_id, owner_id):
        raise ForbiddenError("Chi chu so huu moi co quyen them thanh vien")
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
        HomeUser.user_id == user_id,
    ).first()
    if not member:
        raise ForbiddenError("Ban khong co quyen truy cap nha nay")
