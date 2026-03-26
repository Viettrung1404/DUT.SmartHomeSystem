from datetime import timedelta, datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4
from fastapi import Depends
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError
from sqlalchemy.orm import Session
from src.entities.user import User
from . import models
from fastapi.security import OAuth2PasswordBearer
from ...exceptions import AuthenticationError, UserNotFoundError
from src.config.env import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
import logging

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/login')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)


def authenticate_user(email: str, password: str, db: Session) -> User | bool:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        logging.warning(f"Failed authentication attempt for email: {email}")
        return False
    return user


def create_access_token(email: str, user_id: UUID, expires_delta: timedelta) -> str:
    encode = {
        'sub': email,
        'id': str(user_id),
        'type': 'access',
        'exp': datetime.now(timezone.utc) + expires_delta
    }
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(email: str, user_id: UUID) -> str:
    encode = {
        'sub': email,
        'id': str(user_id),
        'type': 'refresh',
        'exp': datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    }
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, expected_type: str = 'access') -> models.TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get('id')
        token_type: str = payload.get('type', 'access')
        if token_type != expected_type:
            raise AuthenticationError("Invalid token type")
        return models.TokenData(user_id=user_id)
    except PyJWTError as e:
        logging.warning(f"Token verification failed: {str(e)}")
        raise AuthenticationError()


def register_user(db: Session, request: models.RegisterUserRequest) -> User:
    try:
        user = User(
            id=uuid4(),
            email=request.email,
            full_name=request.full_name,
            password_hash=get_password_hash(request.password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        logging.error(f"Failed to register user: {request.email}. Error: {str(e)}")
        raise


def login_user(email: str, password: str, db: Session) -> models.Token:
    user = authenticate_user(email, password, db)
    if not user:
        raise AuthenticationError("Email hoặc mật khẩu không đúng")
    access_token = create_access_token(user.email, user.id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_refresh_token(user.email, user.id)
    return models.Token(access_token=access_token, refresh_token=refresh_token)


def refresh_access_token(refresh_token: str, db: Session) -> models.Token:
    token_data = verify_token(refresh_token, expected_type='refresh')
    user_id = token_data.get_uuid()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AuthenticationError("User not found")
    access_token = create_access_token(user.email, user.id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    new_refresh = create_refresh_token(user.email, user.id)
    return models.Token(access_token=access_token, refresh_token=new_refresh)


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]) -> models.TokenData:
    return verify_token(token)


CurrentUser = Annotated[models.TokenData, Depends(get_current_user)]


def get_user_profile(user_id: UUID, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UserNotFoundError(user_id)
    return user
