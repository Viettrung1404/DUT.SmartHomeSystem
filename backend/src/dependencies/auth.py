from src.entities.models import User

from typing import Annotated

from fastapi import Depends, HTTPException, status

from src.apis.auth import service as auth_service
from src.database.core import DbSession

async def get_current_user(token_data: auth_service.CurrentUser, db: DbSession) -> User:
    user = auth_service.get_user_profile(token_data.get_uuid(), db)
    return user

async def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user

async def require_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account deactivated",
        )
    return current_user

CurrentUserEntity = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]
ActiveUser = Annotated[User, Depends(require_active_user)]
