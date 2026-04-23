import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID, uuid4

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.config.env import (
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    PASSWORD_RESET_BASE_URL,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
)
from src.entities.auth_session import AuthSession
from src.entities.password_reset_token import PasswordResetToken
from src.entities.user import User
from src.services.mailer import MailerConfigurationError, send_email
from ...database.core import DbSession

from ...exceptions import AuthenticationError, UserNotFoundError
from . import models

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 30


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)


def authenticate_user(email: str, password: str, db: Session) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        logging.warning("Failed authentication attempt for email: %s", email)
        return None
    if not user.is_active:
        raise AuthenticationError("Tài khoản đã bị vô hiệu hóa")
    return user


def create_access_token(email: str, user_id: UUID, session_id: UUID, expires_delta: timedelta) -> str:
    payload = {
        "sub": email,
        "id": str(user_id),
        "sid": str(session_id),
        "type": "access",
        "exp": _now() + expires_delta,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(email: str, user_id: UUID, session_id: UUID) -> str:
    payload = {
        "sub": email,
        "id": str(user_id),
        "sid": str(session_id),
        "type": "refresh",
        "exp": _now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, expected_type: str = "access") -> models.TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        session_id: str = payload.get("sid")
        token_type: str = payload.get("type", "access")
        if token_type != expected_type:
            raise AuthenticationError("Invalid token type")
        if not user_id or not session_id:
            raise AuthenticationError("Invalid token payload")
        return models.TokenData(user_id=user_id, session_id=session_id, token_type=token_type)
    except PyJWTError as exc:
        logging.warning("Token verification failed: %s", str(exc))
        raise AuthenticationError()


def _get_active_session(db: Session, session_id: UUID) -> AuthSession | None:
    session = db.query(AuthSession).filter(AuthSession.id == session_id).first()
    if not session:
        return None
    if session.revoked_at is not None:
        return None
    if session.expires_at <= _now():
        return None
    return session


def register_user(db: Session, request: models.RegisterUserRequest) -> User:
    try:
        user = User(
            id=uuid4(),
            email=request.email,
            full_name=request.full_name,
            password_hash=get_password_hash(request.password),
            role="MEMBER",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as exc:
        db.rollback()
        logging.error("Failed to register user: %s. Error: %s", request.email, str(exc))
        raise


def login_user(email: str, password: str, db: Session, user_agent: str | None = None, ip_address: str | None = None) -> models.Token:
    user = authenticate_user(email, password, db)
    if not user:
        raise AuthenticationError("Email hoặc mật khẩu không đúng")

    auth_session = AuthSession(
        id=uuid4(),
        user_id=user.id,
        refresh_token_hash="",
        user_agent=user_agent,
        ip_address=ip_address,
        expires_at=_now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    refresh_token = create_refresh_token(user.email, user.id, auth_session.id)
    auth_session.refresh_token_hash = _hash_token(refresh_token)
    db.add(auth_session)
    db.commit()

    access_token = create_access_token(
        user.email,
        user.id,
        auth_session.id,
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return models.Token(
        access_token=access_token,
        refresh_token=refresh_token,
        session_id=auth_session.id,
    )


def refresh_access_token(refresh_token: str, db: Session) -> models.Token:
    token_data = verify_token(refresh_token, expected_type="refresh")
    session_id = token_data.get_session_uuid()
    user_id = token_data.get_uuid()
    if not session_id or not user_id:
        raise AuthenticationError("Invalid token")

    session = _get_active_session(db, session_id)
    if not session or session.user_id != user_id:
        raise AuthenticationError("Session is not active")

    if session.refresh_token_hash != _hash_token(refresh_token):
        session.revoked_at = _now()
        db.commit()
        raise AuthenticationError("Refresh token mismatch")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise AuthenticationError("User not found or inactive")

    new_refresh_token = create_refresh_token(user.email, user.id, session.id)
    session.refresh_token_hash = _hash_token(new_refresh_token)
    session.expires_at = _now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    session.last_used_at = _now()
    db.commit()

    access_token = create_access_token(
        user.email,
        user.id,
        session.id,
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return models.Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        session_id=session.id,
    )


def logout_session(session_id: UUID, db: Session) -> None:
    session = db.query(AuthSession).filter(AuthSession.id == session_id).first()
    if session and session.revoked_at is None:
        session.revoked_at = _now()
        db.commit()


def logout_user(current_token_data: models.TokenData | None, db: Session, refresh_token: str | None = None) -> None:
    if refresh_token:
        token_data = verify_token(refresh_token, expected_type="refresh")
    elif current_token_data:
        token_data = current_token_data
    else:
        raise AuthenticationError("Missing token")

    session_id = token_data.get_session_uuid()
    if not session_id:
        raise AuthenticationError("Invalid session")
    logout_session(session_id, db)


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: DbSession) -> models.TokenData:
    token_data = verify_token(token, expected_type="access")
    session_id = token_data.get_session_uuid()
    user_id = token_data.get_uuid()
    if not session_id or not user_id:
        raise AuthenticationError("Invalid token")

    session = _get_active_session(db, session_id)
    if not session or session.user_id != user_id:
        raise AuthenticationError("Session is not active")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise AuthenticationError("User not found or inactive")

    return token_data


CurrentUser = Annotated[models.TokenData, Depends(get_current_user)]
RawToken = Annotated[str, Depends(oauth2_bearer)]


def get_user_profile(user_id: UUID, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UserNotFoundError(user_id)
    return user


def change_password(db: Session, user_id: UUID, payload: models.ChangePasswordRequest) -> None:
    user = get_user_profile(user_id, db)
    if not verify_password(payload.current_password, user.password_hash):
        raise AuthenticationError("Mật khẩu hiện tại không đúng")
    if payload.new_password != payload.new_password_confirm:
        raise AuthenticationError("Xác nhận mật khẩu mới không khớp")
    user.password_hash = get_password_hash(payload.new_password)
    db.commit()


def list_active_sessions(db: Session, user_id: UUID) -> list[AuthSession]:
    return (
        db.query(AuthSession)
        .filter(
            AuthSession.user_id == user_id,
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > _now(),
        )
        .order_by(AuthSession.created_at.desc())
        .all()
    )


def revoke_one_session(db: Session, user_id: UUID, session_id: UUID) -> None:
    session = db.query(AuthSession).filter(AuthSession.id == session_id, AuthSession.user_id == user_id).first()
    if not session:
        raise AuthenticationError("Session không tồn tại")
    if session.revoked_at is None:
        session.revoked_at = _now()
        db.commit()


def revoke_all_sessions(db: Session, user_id: UUID) -> int:
    sessions = db.query(AuthSession).filter(AuthSession.user_id == user_id, AuthSession.revoked_at.is_(None)).all()
    for session in sessions:
        session.revoked_at = _now()
    db.commit()
    return len(sessions)


def create_password_reset_request(db: Session, payload: models.PasswordResetRequest) -> None:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        return

    reset_token = secrets.token_urlsafe(48)
    otp_code = f"{secrets.randbelow(900000) + 100000}"

    token_record = PasswordResetToken(
        id=uuid4(),
        user_id=user.id,
        token_hash=_hash_token(reset_token),
        expires_at=_now() + timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
    )

    otp_record = PasswordResetToken(
        id=uuid4(),
        user_id=user.id,
        token_hash=_hash_token(otp_code),
        expires_at=_now() + timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
    )

    db.add(token_record)
    db.add(otp_record)
    db.commit()

    reset_link = f"{PASSWORD_RESET_BASE_URL.rstrip('/')}/reset-password?token={reset_token}"
    subject = "Smart Home - Ma OTP dat lai mat khau"
    plain_text_body = (
        "Ban da yeu cau dat lai mat khau.\n\n"
        f"OTP: {otp_code}\n"
        f"Reset link: {reset_link}\n\n"
        "OTP va link se het han sau 30 phut."
    )
    html_body = (
        "<p>Ban da yeu cau dat lai mat khau.</p>"
        f"<p><b>OTP:</b> {otp_code}</p>"
        f"<p><b>Reset link:</b> <a href=\"{reset_link}\">{reset_link}</a></p>"
        "<p>OTP va link se het han sau 30 phut.</p>"
    )

    try:
        send_email(user.email, subject, plain_text_body, html_body)
    except MailerConfigurationError as exc:
        logging.error("Mailer configuration error: %s", str(exc))
        raise AuthenticationError("He thong email chua duoc cau hinh")
    except Exception as exc:
        logging.error("Failed to send reset password email: %s", str(exc))
        raise AuthenticationError("Khong the gui email reset password")


def confirm_password_reset(db: Session, payload: models.PasswordResetConfirmRequest) -> None:
    if payload.new_password != payload.new_password_confirm:
        raise AuthenticationError("Xác nhận mật khẩu mới không khớp")

    reset_secret = payload.reset_token or payload.otp_code
    if not reset_secret:
        raise AuthenticationError("Can cung cap reset_token hoac otp_code")

    token_hash = _hash_token(reset_secret)
    record = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token_hash == token_hash)
        .first()
    )
    if not record:
        raise AuthenticationError("Token reset không hợp lệ")
    if record.used_at is not None or record.expires_at <= _now():
        raise AuthenticationError("Token reset đã hết hạn hoặc đã sử dụng")

    user = db.query(User).filter(User.id == record.user_id).first()
    if not user:
        raise AuthenticationError("User not found")

    user.password_hash = get_password_hash(payload.new_password)
    record.used_at = _now()

    # Invalidate all remaining reset secrets for this user after successful reset.
    active_records = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.user_id == user.id, PasswordResetToken.used_at.is_(None))
        .all()
    )
    for active_record in active_records:
        active_record.used_at = _now()

    db.commit()
