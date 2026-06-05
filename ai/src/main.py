"""Main FastAPI application entry point for Vietnamese NLP Intent Classification Server."""

from __future__ import annotations

import logging
from datetime import datetime

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.error_handler import (
    AuthenticationError,
    AuthorizationError,
    ErrorHandler,
    RateLimitError,
    ServiceUnavailableError,
    TimeoutError as APITimeoutError,
    authentication_error_handler,
    authorization_error_handler,
    rate_limit_error_handler,
    service_unavailable_error_handler,
    timeout_error_handler,
)
from src.api.v1.router import api_router
from src.bootstrap import init_app_state
from src.config.settings import settings


logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Vietnamese NLP Intent Classification Server",
    description=(
        "AI-powered Natural Language Processing server for Vietnamese Smart Home "
        "intent classification and entity extraction"
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins() or ["*"],
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=[m.strip() for m in settings.cors_allow_methods.split(",") if m.strip()],
    allow_headers=[h.strip() for h in settings.cors_allow_headers.split(",") if h.strip()],
)


# Exception handlers
app.add_exception_handler(RequestValidationError, ErrorHandler.validation_error_handler)
app.add_exception_handler(StarletteHTTPException, ErrorHandler.http_exception_handler)
app.add_exception_handler(Exception, ErrorHandler.general_exception_handler)

app.add_exception_handler(AuthenticationError, authentication_error_handler)
app.add_exception_handler(AuthorizationError, authorization_error_handler)
app.add_exception_handler(RateLimitError, rate_limit_error_handler)
app.add_exception_handler(ServiceUnavailableError, service_unavailable_error_handler)
app.add_exception_handler(APITimeoutError, timeout_error_handler)


# Routes
app.include_router(api_router, prefix=f"/api/{settings.api_version}")


@app.get("/")
async def root() -> dict:
    return {
        "service": "Vietnamese NLP Intent Classification Server",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "api_base": f"/api/{settings.api_version}",
    }


@app.get("/health")
async def health_check() -> dict:
    return {
        "status": "healthy",
        "service": "nlp-server",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Starting Vietnamese NLP Intent Classification Server")
    init_app_state(app)
    logger.info("Server ready")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    logger.info("Shutting down Vietnamese NLP Intent Classification Server")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
