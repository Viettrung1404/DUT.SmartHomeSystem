"""
Authentication module for Vietnamese NLP Intent Classification API.

This module provides JWT authentication functionality.

**Validates: Requirements 11.1**
"""

import os

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.api.error_handler import AuthenticationError, AuthorizationError
from src.config.settings import settings

logger = logging.getLogger(__name__)


class JWTAuth:
    """JWT Authentication handler."""
    
    def __init__(self, secret_key: Optional[str] = None, algorithm: Optional[str] = None):
        """
        Initialize JWT authentication.
        
        Args:
            secret_key: JWT secret key (defaults to env variable)
        """
        self.secret_key = (
            secret_key
            or os.getenv("JWT_SECRET_KEY")
            or os.getenv("JWT_SECRET")
            or settings.jwt_secret_key
        )
        self.algorithm = algorithm or os.getenv("JWT_ALGORITHM") or settings.jwt_algorithm
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token and return payload.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload dictionary
            
        Raises:
            jwt.ExpiredSignatureError: If token is expired
            jwt.InvalidTokenError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            raise
        
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            raise
    
    def create_jwt_token(self,
                        user_id: str,
                        expires_in_minutes: int = 30,
                        **extra_claims) -> str:
        """
        Create JWT token.
        
        Args:
            user_id: User ID
            expires_in_minutes: Token expiration time in minutes
            **extra_claims: Additional claims to include
            
        Returns:
            JWT token string
        """
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(minutes=expires_in_minutes),
            "iat": datetime.utcnow(),
            **extra_claims
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token


_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> Dict[str, Any]:
    """FastAPI dependency: validate Bearer JWT and return decoded claims."""
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Missing Bearer token")

    if credentials.scheme.lower() != "bearer":
        raise AuthenticationError("Invalid authentication scheme")

    token = credentials.credentials
    auth = JWTAuth()
    try:
        return auth.verify_jwt_token(token)
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError("Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError("Invalid token") from exc


def require_admin(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """FastAPI dependency: require an `admin` role claim."""
    role = user.get("role") or user.get("roles")
    if role == "admin":
        return user
    if isinstance(role, list) and "admin" in role:
        return user
    raise AuthorizationError("Admin role required")


def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token (convenience function).
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload dictionary
    """
    auth = JWTAuth()
    return auth.verify_jwt_token(token)
