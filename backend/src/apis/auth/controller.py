from uuid import UUID

from fastapi import APIRouter, Request, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from . import models, service
from ...database.core import DbSession
from ...rate_limiter import limiter

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=models.UserResponse)
@limiter.limit("5/hour")
async def register_user(request: Request, db: DbSession,
                        body: models.RegisterUserRequest):
    user = service.register_user(db, body)
    return models.UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        role=user.role,
        is_active=user.is_active,
    )


@router.post("/login", response_model=models.Token)
async def login(
    request: Request,
    db: DbSession,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    return service.login_user(
        form_data.username,
        form_data.password,
        db,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )


@router.post("/login-json", response_model=models.Token)
async def login_json(request: Request, db: DbSession, body: models.LoginRequest):
    return service.login_user(
        body.email,
        body.password,
        db,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )


@router.post("/logout", response_model=models.MessageResponse)
async def logout(db: DbSession, current_user: service.CurrentUser, body: models.LogoutRequest | None = None):
    service.logout_user(current_user, db, body.refresh_token if body else None)
    return models.MessageResponse(message="Đăng xuất thành công")


@router.post("/refresh", response_model=models.Token)
async def refresh_token(db: DbSession, body: models.RefreshRequest):
    return service.refresh_access_token(body.refresh_token, db)


@router.post("/change-password", response_model=models.MessageResponse)
async def change_password(current_user: service.CurrentUser, db: DbSession, body: models.ChangePasswordRequest):
    service.change_password(db, current_user.get_uuid(), body)
    return models.MessageResponse(message="Đổi mật khẩu thành công")


@router.get("/sessions", response_model=list[models.SessionResponse])
async def get_sessions(current_user: service.CurrentUser, db: DbSession):
    sessions = service.list_active_sessions(db, current_user.get_uuid())
    return [
        models.SessionResponse(
            id=s.id,
            user_id=s.user_id,
            user_agent=s.user_agent,
            ip_address=s.ip_address,
            created_at=s.created_at,
            expires_at=s.expires_at,
            last_used_at=s.last_used_at,
        )
        for s in sessions
    ]


@router.delete("/sessions/{session_id}", response_model=models.MessageResponse)
async def delete_one_session(session_id: UUID, current_user: service.CurrentUser, db: DbSession):
    service.revoke_one_session(db, current_user.get_uuid(), session_id)
    return models.MessageResponse(message="Đã đăng xuất phiên được chọn")


@router.delete("/sessions/all", response_model=models.MessageResponse)
async def delete_all_sessions(current_user: service.CurrentUser, db: DbSession):
    count = service.revoke_all_sessions(db, current_user.get_uuid())
    return models.MessageResponse(message=f"Đã đăng xuất {count} phiên")


@router.post("/reset-password/request", response_model=models.MessageResponse)
async def request_password_reset(db: DbSession, body: models.PasswordResetRequest):
    service.create_password_reset_request(db, body)
    return models.MessageResponse(message="Nếu email tồn tại, hệ thống đã gửi hướng dẫn đặt lại mật khẩu")


@router.post("/reset-password/confirm", response_model=models.MessageResponse)
async def confirm_password_reset(db: DbSession, body: models.PasswordResetConfirmRequest):
    service.confirm_password_reset(db, body)
    return models.MessageResponse(message="Đặt lại mật khẩu thành công")


@router.get("/me", response_model=models.UserResponse)
async def get_me(current_user: service.CurrentUser, db: DbSession):
    user = service.get_user_profile(current_user.get_uuid(), db)
    return models.UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        role=user.role,
        is_active=user.is_active,
    )
