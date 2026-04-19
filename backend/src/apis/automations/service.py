from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from src.entities.automation import Automation, AutomationCondition, AutomationAction
from src.entities.home_member import HomeMember
from src.exceptions import AutomationNotFoundError, ForbiddenError
from . import models


def _check_home_access(db: Session, home_id: UUID, user_id: UUID):
    member = db.query(HomeMember).filter(
        HomeMember.home_id == home_id, HomeMember.user_id == user_id
    ).first()
    if not member:
        raise ForbiddenError("Bạn không có quyền truy cập")


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
        act = AutomationAction(
            id=uuid4(), automation_id=automation.id,
            device_id=UUID(a.device_id) if a.device_id else None,
            action=a.action, value=a.value
        )
        db.add(act)

    db.commit()
    db.refresh(automation)
    return automation


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
