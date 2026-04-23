from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class RegisterUserRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    session_id: UUID


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    new_password_confirm: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    reset_token: Optional[str] = None
    otp_code: Optional[str] = None
    new_password: str
    new_password_confirm: str


class TokenData(BaseModel):
    user_id: str | None = None
    session_id: str | None = None
    token_type: str = "access"

    def get_uuid(self) -> UUID | None:
        if self.user_id:
            return UUID(self.user_id)
        return None

    def get_session_uuid(self) -> UUID | None:
        if self.session_id:
            return UUID(self.session_id)
        return None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    last_used_at: Optional[datetime] = None


class MessageResponse(BaseModel):
    message: str


