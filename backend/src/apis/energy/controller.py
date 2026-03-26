from uuid import UUID
from fastapi import APIRouter
from . import models, service
from ...database.core import DbSession
from ...apis.auth.service import CurrentUser

router = APIRouter(prefix='/energy', tags=['energy'])


@router.get("/daily", response_model=models.EnergySummaryResponse)
async def daily_energy(home_id: UUID, current_user: CurrentUser, db: DbSession):
    return service.get_daily_energy(db, home_id, current_user.get_uuid())


@router.get("/weekly", response_model=models.EnergySummaryResponse)
async def weekly_energy(home_id: UUID, current_user: CurrentUser, db: DbSession):
    return service.get_weekly_energy(db, home_id, current_user.get_uuid())


@router.get("/monthly", response_model=models.EnergySummaryResponse)
async def monthly_energy(home_id: UUID, current_user: CurrentUser, db: DbSession):
    return service.get_monthly_energy(db, home_id, current_user.get_uuid())
