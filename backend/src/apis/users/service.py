from src.entities.models import User

from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from src.apis.auth.service import get_password_hash

from src.exceptions import UserNotFoundError

from . import models

def get_user_by_id(db: Session, user_id: UUID) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UserNotFoundError(user_id)
    return user

def create_user_by_admin(db: Session, payload: models.AdminCreateUserRequest) -> User:
    user = User(
        id=uuid4(),
        email=payload.email,
        full_name=payload.full_name,
        password_hash=get_password_hash(payload.password),
        role=payload.role,
        is_active=payload.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def list_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.created_at.desc()).all()

def update_user_by_admin(db: Session, user_id: UUID, payload: models.AdminUpdateUserRequest) -> User:
    user = get_user_by_id(db, user_id)
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

def delete_user_by_admin(db: Session, user_id: UUID) -> None:
    user = get_user_by_id(db, user_id)
    db.delete(user)
    db.commit()

def deactivate_user_by_admin(db: Session, user_id: UUID) -> User:
    user = get_user_by_id(db, user_id)
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user
