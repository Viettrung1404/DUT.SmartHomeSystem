from fastapi import APIRouter, Request
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
        avatar_url=user.avatar_url
    )


@router.post("/login", response_model=models.Token)
async def login(db: DbSession, body: models.LoginRequest):
    return service.login_user(body.email, body.password, db)


@router.post("/refresh", response_model=models.Token)
async def refresh_token(db: DbSession, body: models.RefreshRequest):
    return service.refresh_access_token(body.refresh_token, db)


@router.get("/me", response_model=models.UserResponse)
async def get_me(current_user: service.CurrentUser, db: DbSession):
    user = service.get_user_profile(current_user.get_uuid(), db)
    return models.UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url
    )
