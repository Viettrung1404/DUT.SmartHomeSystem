from uuid import UUID
from fastapi import APIRouter
from starlette import status
from . import models, service
from ...database.core import DbSession
from ...apis.auth.service import CurrentUser

router = APIRouter(prefix='/automations', tags=['automations'])


@router.get("/", response_model=list[models.AutomationResponse])
async def list_automations(home_id: UUID, current_user: CurrentUser, db: DbSession):
    automations = service.get_automations(db, home_id, current_user.get_uuid())
    return [service.to_response(a) for a in automations]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=models.AutomationResponse)
async def create_automation(current_user: CurrentUser, db: DbSession, body: models.AutomationCreate):
    automation = service.create_automation(db, current_user.get_uuid(), body)
    return service.to_response(automation)


@router.get("/{automation_id}", response_model=models.AutomationResponse)
async def get_automation(automation_id: UUID, current_user: CurrentUser, db: DbSession):
    automation = service.get_automation(db, automation_id, current_user.get_uuid())
    return service.to_response(automation)


@router.put("/{automation_id}", response_model=models.AutomationResponse)
async def update_automation(automation_id: UUID, current_user: CurrentUser, db: DbSession, body: models.AutomationUpdate):
    automation = service.update_automation(db, automation_id, current_user.get_uuid(), body)
    return service.to_response(automation)


@router.delete("/{automation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_automation(automation_id: UUID, current_user: CurrentUser, db: DbSession):
    service.delete_automation(db, automation_id, current_user.get_uuid())
