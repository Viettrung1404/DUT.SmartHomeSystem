from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import register_routes
from app.core.model_registry import registry


@asynccontextmanager
async def lifespan(app: FastAPI):
    registry.warmup()
    yield


app = FastAPI(
    title="Smart Home AI Server",
    version="1.0.0",
    description="Standalone AI service for Vietnamese NLP assistant and environment prediction.",
    lifespan=lifespan,
)

register_routes(app)
