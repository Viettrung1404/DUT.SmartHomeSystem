from uuid import UUID
from fastapi import APIRouter
from starlette import status
from . import models, service
from ...database.core import DbSession
from ...apis.auth.service import CurrentUser

router = APIRouter(prefix='/devices', tags=['devices'])


@router.get("/", response_model=list[models.DeviceResponse])
async def list_devices(room_id: UUID, current_user: CurrentUser, db: DbSession):
    devices = service.get_devices_by_room(db, room_id, current_user.get_uuid())
    return [service.to_response(d) for d in devices]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=models.DeviceResponse)
async def create_device(current_user: CurrentUser, db: DbSession, body: models.DeviceCreate):
    device = service.create_device(db, current_user.get_uuid(), body)
    return service.to_response(device)


@router.get("/{device_id}", response_model=models.DeviceResponse)
async def get_device(device_id: UUID, current_user: CurrentUser, db: DbSession):
    device = service.get_device(db, device_id, current_user.get_uuid())
    return service.to_response(device)


@router.put("/{device_id}", response_model=models.DeviceResponse)
async def update_device(device_id: UUID, current_user: CurrentUser, db: DbSession, body: models.DeviceUpdate):
    device = service.update_device(db, device_id, current_user.get_uuid(), body)
    return service.to_response(device)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(device_id: UUID, current_user: CurrentUser, db: DbSession):
    service.delete_device(db, device_id, current_user.get_uuid())


@router.post("/{device_id}/toggle", response_model=models.DeviceResponse)
async def toggle_device(device_id: UUID, current_user: CurrentUser, db: DbSession, body: models.DeviceToggleRequest):
    device = service.toggle_device(db, device_id, current_user.get_uuid(), body)
    return service.to_response(device)


@router.post("/{device_id}/command", response_model=models.DeviceResponse)
async def send_command(device_id: UUID, current_user: CurrentUser, db: DbSession, body: models.DeviceCommandRequest):
    device = service.send_command(db, device_id, current_user.get_uuid(), body)
    return service.to_response(device)
