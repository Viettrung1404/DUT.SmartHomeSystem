"""API v1 router."""

from fastapi import APIRouter

from src.api.v1.endpoints.classify import router as classify_router
from src.api.v1.endpoints.intents import router as intents_router
from src.api.v1.endpoints.metrics import router as metrics_router
from src.api.v1.endpoints.model import router as model_router

api_router = APIRouter()

api_router.include_router(classify_router, tags=["intent"])
api_router.include_router(intents_router, tags=["meta"])
api_router.include_router(metrics_router, tags=["monitoring"])
api_router.include_router(model_router, tags=["model"])
