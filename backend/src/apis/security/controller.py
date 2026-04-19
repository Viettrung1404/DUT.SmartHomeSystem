from uuid import UUID
from fastapi import APIRouter
from starlette import status
from . import models, service
from ...database.core import DbSession
from ...apis.auth.service import CurrentUser

router = APIRouter(prefix='/security', tags=['security'])


@router.get("/summary")
async def security_summary(home_id: UUID, current_user: CurrentUser, db: DbSession):
    return service.get_security_summary(db, home_id, current_user.get_uuid())


@router.get("/events", response_model=list[models.SecurityEventResponse])
async def list_events(home_id: UUID, current_user: CurrentUser, db: DbSession, limit: int = 50):
    events = service.get_events(db, home_id, current_user.get_uuid(), limit)
    return [models.SecurityEventResponse(
        id=str(e.id), home_id=str(e.home_id),
        event_type=e.event_type, severity=e.severity,
        description=e.description, timestamp=e.timestamp
    ) for e in events]


@router.post("/events", status_code=status.HTTP_201_CREATED, response_model=models.SecurityEventResponse)
async def create_event(current_user: CurrentUser, db: DbSession, body: models.SecurityEventCreate):
    event = service.create_event(db, body)
    return models.SecurityEventResponse(
        id=str(event.id), home_id=str(event.home_id),
        event_type=event.event_type, severity=event.severity,
        description=event.description, timestamp=event.timestamp
    )
