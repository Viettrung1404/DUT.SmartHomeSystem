"""
Error Handling Middleware for Vietnamese NLP Intent Classification API.

This module provides error handling middleware for FastAPI application.

**Validates: Requirements 10.1-10.3**
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Union
from datetime import datetime

logger = logging.getLogger(__name__)


class ErrorHandler:
    """
    Error Handler for API errors.
    
    This handler catches and formats errors:
    - Validation errors (400)
    - Authentication errors (401)
    - Authorization errors (403)
    - Rate limit errors (429)
    - Server errors (500)
    - Service unavailable (503)
    """
    
    @staticmethod
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """
        Handle validation errors (400).
        
        Args:
            request: FastAPI request
            exc: Validation error exception
            
        Returns:
            JSONResponse with 400 status code
        """
        logger.warning(f"Validation error: {exc.errors()}")
        
        # Extract error details
        errors = exc.errors()
        error_messages = []
        
        for error in errors:
            field = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_messages.append(f"{field}: {message}")
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status_code": 400,
                "message": "Validation error: " + "; ".join(error_messages),
                "error_type": "validation_error",
                "timestamp": datetime.utcnow().isoformat(),
                "details": errors
            }
        )
    
    @staticmethod
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """
        Handle HTTP exceptions (401, 403, 404, etc.).
        
        Args:
            request: FastAPI request
            exc: HTTP exception
            
        Returns:
            JSONResponse with appropriate status code
        """
        logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
        
        # Map status codes to error types
        error_type_map = {
            400: "validation_error",
            401: "authentication_error",
            403: "authorization_error",
            404: "not_found",
            429: "rate_limit_error",
            500: "server_error",
            503: "service_unavailable"
        }
        
        error_type = error_type_map.get(exc.status_code, "error")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status_code": exc.status_code,
                "message": exc.detail,
                "error_type": error_type,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Handle general exceptions (500).
        
        Args:
            request: FastAPI request
            exc: General exception
            
        Returns:
            JSONResponse with 500 status code
        """
        logger.error(f"Unhandled exception: {type(exc).__name__} - {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": 500,
                "message": "Internal server error",
                "error_type": "server_error",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    def create_error_response(
        status_code: int,
        message: str,
        error_type: str = "error"
    ) -> JSONResponse:
        """
        Create error response.
        
        Args:
            status_code: HTTP status code
            message: Error message
            error_type: Type of error
            
        Returns:
            JSONResponse with error details
        """
        return JSONResponse(
            status_code=status_code,
            content={
                "status_code": status_code,
                "message": message,
                "error_type": error_type,
                "timestamp": datetime.utcnow().isoformat()
            }
        )


# Custom exception classes

class AuthenticationError(Exception):
    """Authentication error (401)."""
    def __init__(self, message: str = "Authentication failed"):
        self.message = message
        super().__init__(self.message)


class AuthorizationError(Exception):
    """Authorization error (403)."""
    def __init__(self, message: str = "Access forbidden"):
        self.message = message
        super().__init__(self.message)


class RateLimitError(Exception):
    """Rate limit error (429)."""
    def __init__(self, message: str = "Rate limit exceeded"):
        self.message = message
        super().__init__(self.message)


class ServiceUnavailableError(Exception):
    """Service unavailable error (503)."""
    def __init__(self, message: str = "Service temporarily unavailable"):
        self.message = message
        super().__init__(self.message)


class TimeoutError(Exception):
    """Timeout error (504)."""
    def __init__(self, message: str = "Request timeout"):
        self.message = message
        super().__init__(self.message)


# Exception handlers for custom exceptions

async def authentication_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
    """Handle authentication errors."""
    logger.warning(f"Authentication error: {exc.message}")
    return ErrorHandler.create_error_response(401, exc.message, "authentication_error")


async def authorization_error_handler(request: Request, exc: AuthorizationError) -> JSONResponse:
    """Handle authorization errors."""
    logger.warning(f"Authorization error: {exc.message}")
    return ErrorHandler.create_error_response(403, exc.message, "authorization_error")


async def rate_limit_error_handler(request: Request, exc: RateLimitError) -> JSONResponse:
    """Handle rate limit errors."""
    logger.warning(f"Rate limit error: {exc.message}")
    return ErrorHandler.create_error_response(429, exc.message, "rate_limit_error")


async def service_unavailable_error_handler(request: Request, exc: ServiceUnavailableError) -> JSONResponse:
    """Handle service unavailable errors."""
    logger.error(f"Service unavailable: {exc.message}")
    return ErrorHandler.create_error_response(503, exc.message, "service_unavailable")


async def timeout_error_handler(request: Request, exc: TimeoutError) -> JSONResponse:
    """Handle timeout errors."""
    logger.warning(f"Timeout error: {exc.message}")
    return ErrorHandler.create_error_response(504, exc.message, "timeout_error")
