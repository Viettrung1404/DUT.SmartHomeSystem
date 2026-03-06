from uuid import UUID
from fastapi import APIRouter
from starlette import status
from . import models, service
from ...database.core import DbSession
from ...apis.auth.service import CurrentUser

router = APIRouter(prefix='/rooms', tags=['rooms'])


@router.get("/", response_model=list[models.RoomResponse])
async def list_rooms(home_id: UUID, current_user: CurrentUser, db: DbSession):
    rooms = service.get_rooms_by_home(db, home_id, current_user.get_uuid())
    return [service.get_room_response(db, r) for r in rooms]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=models.RoomResponse)
async def create_room(current_user: CurrentUser, db: DbSession, body: models.RoomCreate):
    room = service.create_room(db, current_user.get_uuid(), body)
    return service.get_room_response(db, room)


@router.get("/{room_id}", response_model=models.RoomResponse)
async def get_room(room_id: UUID, current_user: CurrentUser, db: DbSession):
    room = service.get_room(db, room_id, current_user.get_uuid())
    return service.get_room_response(db, room)


@router.put("/{room_id}", response_model=models.RoomResponse)
async def update_room(room_id: UUID, current_user: CurrentUser, db: DbSession, body: models.RoomUpdate):
    room = service.update_room(db, room_id, current_user.get_uuid(), body)
    return service.get_room_response(db, room)


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(room_id: UUID, current_user: CurrentUser, db: DbSession):
    service.delete_room(db, room_id, current_user.get_uuid())
