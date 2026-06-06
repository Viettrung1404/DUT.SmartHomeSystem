from __future__ import annotations

from fastapi import APIRouter, FastAPI, HTTPException

from app.core.capabilities import (
    CAPABILITY_NOTE,
    DEVICE_TYPE_ALIASES,
    INTENTS,
    ROOM_ALIASES,
    SENSOR_TYPE_ALIASES,
)
from app.core.model_registry import registry
from app.schemas.assistant import ChatRequest, ChatResponse
from app.schemas.nlp import ParseRequest, ParseResponse
from app.schemas.prediction import (
    BatchPredictionRequest,
    BatchPredictionResult,
    PredictEnvironmentRequest,
    PredictEnvironmentResponse,
)
from app.services.assistant_service import AssistantService
from app.services.environment_predictor import EnvironmentPredictor
from app.services.nlp_pipeline import NLUPipeline


router = APIRouter()
nlp_pipeline = NLUPipeline()
assistant_service = AssistantService(nlp_pipeline)
environment_predictor = EnvironmentPredictor()


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "ai-server",
        "models": [item.model_dump() for item in registry.health_models()],
    }


@router.get("/api/v1/meta/capabilities")
def capabilities() -> dict:
    return {
        "intents": INTENTS,
        "room_aliases": ROOM_ALIASES,
        "device_type_aliases": DEVICE_TYPE_ALIASES,
        "sensor_type_aliases": SENSOR_TYPE_ALIASES,
        "forecast": {
            "supported_sources": ["inline_history", "db_source"],
            "default_horizon_minutes": 30,
            "required_inline_fields": ["timestamp", "temperature", "humidity"],
            "note": CAPABILITY_NOTE,
        },
    }


@router.post("/api/v1/nlp/parse", response_model=ParseResponse)
def parse_nlp(request: ParseRequest) -> ParseResponse:
    return nlp_pipeline.parse(request.text, request.context)


@router.post("/api/v1/assistant/chat", response_model=ChatResponse)
def assistant_chat(request: ChatRequest) -> ChatResponse:
    return assistant_service.respond(request.message, request.home_context)


@router.post("/api/v1/predict/environment", response_model=PredictEnvironmentResponse)
def predict_environment(request: PredictEnvironmentRequest) -> PredictEnvironmentResponse:
    try:
        return environment_predictor.predict_from_request(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/api/v1/predict/environment/batch", response_model=list[BatchPredictionResult])
def predict_environment_batch(request: BatchPredictionRequest) -> list[BatchPredictionResult]:
    results: list[BatchPredictionResult] = []
    for item in request.items:
        try:
            prediction = environment_predictor.predict_from_request(item.request)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"{item.request_id}: {exc}") from exc
        results.append(BatchPredictionResult(request_id=item.request_id, prediction=prediction))
    return results


def register_routes(app: FastAPI) -> None:
    app.include_router(router)
