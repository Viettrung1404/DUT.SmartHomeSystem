from fastapi import APIRouter, status
from uuid import UUID

from ...database.core import DbSession
from . import models
from . import service
from ..auth.service import CurrentUser
from ...dependencies.auth import AdminUser

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)
admin_router = APIRouter(prefix='/admin/users', tags=['admin-users'])


@router.get("/me", response_model=models.UserResponse)
def get_current_user(current_user: CurrentUser, db: DbSession):
    user = service.get_user_by_id(db, current_user.get_uuid())
    return models.UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        role=user.role,
        is_active=user.is_active,
    )


@admin_router.post("", status_code=status.HTTP_201_CREATED, response_model=models.UserResponse)
async def admin_create_user(_: AdminUser, db: DbSession, body: models.AdminCreateUserRequest):
    user = service.create_user_by_admin(db, body)
    return models.UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        role=user.role,
        is_active=user.is_active,
    )


@admin_router.get("", response_model=models.AdminUserListResponse)
async def admin_list_users(_: AdminUser, db: DbSession):
    users = service.list_users(db)
    return models.AdminUserListResponse(
        users=[
            models.UserResponse(
                id=str(user.id),
                email=user.email,
                full_name=user.full_name,
                avatar_url=user.avatar_url,
                role=user.role,
                is_active=user.is_active,
            )
            for user in users
        ]
    )


@admin_router.patch("/{user_id}", response_model=models.UserResponse)
async def admin_update_user(user_id: UUID, _: AdminUser, db: DbSession, body: models.AdminUpdateUserRequest):
    user = service.update_user_by_admin(db, user_id, body)
    return models.UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        role=user.role,
        is_active=user.is_active,
    )


@admin_router.delete("/{user_id}", response_model=models.MessageResponse)
async def admin_delete_user(user_id: UUID, _: AdminUser, db: DbSession):
    service.delete_user_by_admin(db, user_id)
    return models.MessageResponse(message="Xóa tài khoản thành công")


@admin_router.post("/{user_id}/deactivate", response_model=models.UserResponse)
async def admin_deactivate_user(user_id: UUID, _: AdminUser, db: DbSession):
    user = service.deactivate_user_by_admin(db, user_id)
    return models.UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        role=user.role,
        is_active=user.is_active,
    )
