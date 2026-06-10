import json
from uuid import UUID, uuid4

from src.entities.models import (
    Automation,
    AutomationAction,
    AutomationCondition,
    Device,
    HomeUser,
    Room,
)
from sqlalchemy.orm import Session

from src.exceptions import AutomationNotFoundError, DeviceNotFoundError, ForbiddenError
from . import models

def _check_home_access(db: Session, home_id: UUID, user_id: UUID):
    member = db.query(HomeUser).filter(
        HomeUser.home_id == home_id, HomeUser.user_id == user_id
    ).first()
    if not member:
        raise ForbiddenError("Bạn không có quyền truy cập")

def _check_action_device_access(db: Session, home_id: UUID, device_id: UUID) -> None:
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise DeviceNotFoundError(device_id)

    room = db.query(Room).filter(Room.id == device.room_id).first()
    if not room or room.home_id != home_id or not getattr(room, "is_active", True):
        raise ForbiddenError("Thiet bi khong thuoc nha dang tao tu dong hoa")


def create_automation(db: Session, user_id: UUID, data: models.AutomationCreate) -> Automation:
    home_id = UUID(data.home_id)
    _check_home_access(db, home_id, user_id)

    automation = Automation(id=uuid4(), home_id=home_id, name=data.name)
    db.add(automation)
    db.flush()

    for c in data.conditions:
        cond = AutomationCondition(
            id=uuid4(), automation_id=automation.id,
            condition_type=c.condition_type, value=c.value
        )
        db.add(cond)

    for a in data.actions:
        action_device_id = UUID(a.device_id) if a.device_id else None
        if action_device_id:
            _check_action_device_access(db, home_id, action_device_id)

        act = AutomationAction(
            id=uuid4(), automation_id=automation.id,
            device_id=action_device_id,
            action=a.action, value=a.value
        )
        db.add(act)

    db.commit()
    db.refresh(automation)
    return automation


def create_schedule_automation_from_suggestion(
    db: Session,
    user_id: UUID,
    *,
    device_id: str,
    automation_name: str,
    time_value: str,
    days_of_week: list[int] | None = None,
    power_state: str | None = None,
) -> Automation:
    device_uuid = UUID(device_id)
    device = db.query(Device).filter(Device.id == device_uuid).first()
    if not device or not device.room or not device.room.home_id:
        raise ValueError("Device referenced by suggestion is invalid")

    normalized_days = sorted({int(day) for day in (days_of_week or []) if 0 <= int(day) <= 6})
    condition_type = "weekday_time" if normalized_days else "time"
    condition_value = (
        json.dumps({"time": time_value, "days_of_week": normalized_days})
        if normalized_days
        else time_value
    )

    normalized_power = (power_state or "ON").strip().upper()
    action_value = "true" if normalized_power in {"ON", "TRUE", "1"} else "false"

    payload = models.AutomationCreate(
        home_id=str(device.room.home_id),
        name=automation_name,
        conditions=[
            models.ConditionCreate(
                condition_type=condition_type,
                value=condition_value,
            )
        ],
        actions=[
            models.ActionCreate(
                device_id=str(device_uuid),
                action="toggle",
                value=action_value,
            )
        ],
    )
    return create_automation(db, user_id, payload)

def get_automations(db: Session, home_id: UUID, user_id: UUID) -> list[Automation]:
    _check_home_access(db, home_id, user_id)
    return db.query(Automation).filter(Automation.home_id == home_id).all()

def get_automation(db: Session, automation_id: UUID, user_id: UUID) -> Automation:
    automation = db.query(Automation).filter(Automation.id == automation_id).first()
    if not automation:
        raise AutomationNotFoundError(automation_id)
    _check_home_access(db, automation.home_id, user_id)
    return automation

def update_automation(db: Session, automation_id: UUID, user_id: UUID, data: models.AutomationUpdate) -> Automation:
    automation = get_automation(db, automation_id, user_id)
    if data.name is not None:
        automation.name = data.name
    if data.enabled is not None:
        automation.enabled = data.enabled
    db.commit()
    db.refresh(automation)
    return automation

def delete_automation(db: Session, automation_id: UUID, user_id: UUID):
    automation = get_automation(db, automation_id, user_id)
    db.delete(automation)
    db.commit()

def to_response(automation: Automation) -> models.AutomationResponse:
    return models.AutomationResponse(
        id=str(automation.id),
        home_id=str(automation.home_id),
        name=automation.name,
        enabled=automation.enabled,
        created_at=automation.created_at,
        conditions=[
            models.ConditionResponse(id=str(c.id), condition_type=c.condition_type, value=c.value)
            for c in automation.conditions
        ],
        actions=[
            models.ActionResponse(
                id=str(a.id), device_id=str(a.device_id) if a.device_id else None,
                action=a.action, value=a.value
            )
            for a in automation.actions
        ],
    )
