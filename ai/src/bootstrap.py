"""Application bootstrap and shared resource initialization.

This module centralizes creation of long-lived objects (classifiers, cache,
rate limiter, preprocessing) and stores them on FastAPI `app.state`.

Keeping this logic in one place avoids circular imports between `src.main`
and endpoint modules.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI

from src.api.rate_limiter import RateLimiter
from src.api.response_builder import ResponseBuilder
from src.cache.response_cache import ResponseCache
from src.classifiers.hybrid import HybridClassifier
from src.classifiers.ml_based import MLBasedClassifier
from src.classifiers.rule_based import RuleBasedClassifier
from src.config.settings import settings
from src.entities.entity_extractor import EntityExtractor
from src.monitoring.logger import StructuredLogger
from src.preprocessing.pipeline import PreprocessingPipeline

logger = logging.getLogger(__name__)


def _resolve_model_dir(model_path: str) -> Path:
    path = Path(model_path)
    # Support either a directory (preferred) or a direct file path.
    return path.parent if path.suffix else path


def load_models(app: FastAPI) -> None:
    """(Re)load ML + hybrid classifiers and attach to app.state."""
    rule_classifier = RuleBasedClassifier()
    app.state.rule_classifier = rule_classifier

    ml_classifier: Optional[MLBasedClassifier] = None
    model_dir = _resolve_model_dir(settings.model_path)
    try:
        ml_classifier = MLBasedClassifier(
            model_path=str(model_dir),
            use_onnx=settings.use_onnx,
        )
    except Exception as exc:
        logger.warning(
            "Failed to initialize ML classifier with ONNX=%s: %s",
            settings.use_onnx,
            exc,
        )

        # Retry with PyTorch inference if ONNX failed or was misconfigured.
        if settings.use_onnx:
            try:
                ml_classifier = MLBasedClassifier(
                    model_path=str(model_dir),
                    use_onnx=False,
                )
                logger.info("Fell back to PyTorch inference for ML classifier")
            except Exception as retry_exc:
                logger.warning(
                    "Failed to initialize ML classifier with PyTorch fallback: %s",
                    retry_exc,
                )

    app.state.ml_classifier = ml_classifier
    app.state.hybrid_classifier = (
        HybridClassifier(rule_classifier, ml_classifier) if ml_classifier else None
    )

    if ml_classifier:
        # Keep stable order by intent id.
        app.state.available_intents = [
            ml_classifier.id_to_intent[i] for i in sorted(ml_classifier.id_to_intent)
        ]
    else:
        app.state.available_intents = [
            "control_device",
            "environmental_comfort",
            "query_sensor",
            "query_device_status",
            "security_mode",
            "security_alert",
            "activate_scene",
            "unknown",
        ]


def init_app_state(app: FastAPI) -> None:
    """Initialize shared resources and attach them to app.state."""
    app.state.settings = settings
    app.state.response_builder = ResponseBuilder()
    app.state.preprocessing = PreprocessingPipeline()
    app.state.entity_extractor = EntityExtractor()
    app.state.structured_logger = StructuredLogger("nlp_server")

    app.state.rate_limiter = RateLimiter(
        rate=settings.rate_limit_per_minute,
        per=60,
        burst=max(settings.rate_limit_per_minute, 1),
    )

    app.state.cache = ResponseCache(
        redis_url=settings.redis_url,
        ttl=settings.cache_ttl_seconds,
    )

    load_models(app)
