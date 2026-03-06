from uuid import UUID
from fastapi import APIRouter
from starlette import status
from . import models, service
from ...database.core import DbSession
from ...apis.auth.service import CurrentUser

router = APIRouter(prefix='/homes', tags=['homes'])


@router.get("/", response_model=list[models.HomeResponse])
async def list_homes(current_user: CurrentUser, db: DbSession):
    homes = service.get_user_homes(db, current_user.get_uuid())
    return [service.get_home_stats(db, h) for h in homes]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=models.HomeResponse)
async def create_home(current_user: CurrentUser, db: DbSession, body: models.HomeCreate):
    home = service.create_home(db, current_user.get_uuid(), body)
    return service.get_home_stats(db, home)


@router.get("/{home_id}", response_model=models.HomeResponse)
async def get_home(home_id: UUID, current_user: CurrentUser, db: DbSession):
    home = service.get_home(db, home_id, current_user.get_uuid())
    return service.get_home_stats(db, home)


@router.put("/{home_id}", response_model=models.HomeResponse)
async def update_home(home_id: UUID, current_user: CurrentUser, db: DbSession, body: models.HomeUpdate):
    home = service.update_home(db, home_id, current_user.get_uuid(), body)
    return service.get_home_stats(db, home)


@router.delete("/{home_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_home(home_id: UUID, current_user: CurrentUser, db: DbSession):
    service.delete_home(db, home_id, current_user.get_uuid())


@router.get("/{home_id}/members", response_model=list[models.HomeMemberResponse])
async def list_members(home_id: UUID, current_user: CurrentUser, db: DbSession):
    return service.get_home_members(db, home_id, current_user.get_uuid())


@router.post("/{home_id}/members", status_code=status.HTTP_201_CREATED)
async def add_member(home_id: UUID, current_user: CurrentUser, db: DbSession, body: models.AddMemberRequest):
    service.add_home_member(db, home_id, current_user.get_uuid(), body)
    return {"message": "Đã thêm thành viên"}
