from src.entities.models import SecurityEvent, HomeUser

from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from src.exceptions import ForbiddenError
from . import models

def _check_home_access(db: Session, home_id: UUID, user_id: UUID):
    member = db.query(HomeUser).filter(
        HomeUser.home_id == home_id, HomeUser.user_id == user_id
    ).first()
    if not member:
        raise ForbiddenError("Bạn không có quyền truy cập")

def create_event(db: Session, data: models.SecurityEventCreate) -> SecurityEvent:
    event = SecurityEvent(
        id=uuid4(), home_id=UUID(data.home_id),
        event_type=data.event_type, severity=data.severity,
        description=data.description
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

def get_events(db: Session, home_id: UUID, user_id: UUID, limit: int = 50) -> list[SecurityEvent]:
    _check_home_access(db, home_id, user_id)
    return db.query(SecurityEvent).filter(
        SecurityEvent.home_id == home_id
    ).order_by(SecurityEvent.timestamp.desc()).limit(limit).all()

def get_security_summary(db: Session, home_id: UUID, user_id: UUID) -> models.SecuritySummaryResponse:
    _check_home_access(db, home_id, user_id)
    # Last 24 hours
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    events = db.query(SecurityEvent).filter(
        SecurityEvent.home_id == home_id,
        SecurityEvent.timestamp >= since
    ).order_by(SecurityEvent.timestamp.desc()).all()

    high_count = sum(1 for e in events if e.severity == 'high')
    medium_count = sum(1 for e in events if e.severity == 'medium')
    low_count = sum(1 for e in events if e.severity == 'low')

    risk_level = 'low'
    if high_count >= 2:
        risk_level = 'high'
    elif high_count >= 1 or medium_count >= 3:
        risk_level = 'medium'

    recent = [models.SecurityEventResponse(
        id=str(e.id), home_id=str(e.home_id),
        event_type=e.event_type, severity=e.severity,
        description=e.description, timestamp=e.timestamp
    ) for e in events[:20]]

    return models.SecuritySummaryResponse(
        risk_level=risk_level, total_events=len(events),
        high_count=high_count, medium_count=medium_count, low_count=low_count,
        recent_events=recent
    )
