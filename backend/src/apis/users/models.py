from typing import Literal, Optional

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class AdminCreateUserRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: Literal["ADMIN", "MEMBER", "GUEST"] = "MEMBER"
    is_active: bool = True


class AdminUpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[Literal["ADMIN", "MEMBER", "GUEST"]] = None
    is_active: Optional[bool] = None


class AdminUserListResponse(BaseModel):
    users: list[UserResponse]


class MessageResponse(BaseModel):
    message: str
