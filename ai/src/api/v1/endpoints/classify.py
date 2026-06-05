from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional, Tuple, Union

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from src.api.auth import get_current_user
from src.api.error_handler import RateLimitError, ServiceUnavailableError
from src.models.schemas import IntentClassificationRequest
from src.monitoring.metrics import (
    API_REQUEST_DURATION_SECONDS,
    API_REQUESTS_TOTAL,
    CACHE_HITS_TOTAL,
    CACHE_MISSES_TOTAL,
    CLASSIFICATION_CONFIDENCE,
    RATE_LIMITED_TOTAL,
)

router = APIRouter()


def _top_intents_to_dicts(top_k: Optional[List[Tuple[str, float]]]) -> List[Dict[str, Any]]:
    if not top_k:
        return []
    return [{"intent": intent, "confidence": float(conf)} for intent, conf in top_k[:3]]


def _normalize_result(result: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
    if isinstance(result, dict):
        return result

    normalized = {
        "intent": getattr(result, "intent", "unknown"),
        "entities": getattr(result, "entities", {}) or {},
        "confidence": float(getattr(result, "confidence", 0.0) or 0.0),
        "classifier_type": getattr(result, "classifier_type", "fallback"),
    }

    top_k = getattr(result, "top_k_intents", None)
    if top_k is not None:
        normalized["top_k_intents"] = top_k

    return normalized


def _suggestions_for(top_intents: List[Dict[str, Any]]) -> List[str]:
    if not top_intents:
        return [
            "Bạn có thể nói rõ yêu cầu được không?",
            "Ví dụ: 'Bật đèn phòng khách' hoặc 'Kiểm tra nhiệt độ'.",
        ]

    intent = str(top_intents[0].get("intent") or "unknown")
    mapping = {
        "control_device": "Bạn muốn bật/tắt thiết bị nào và ở phòng nào?",
        "query_sensor": "Bạn muốn kiểm tra cảm biến nào (nhiệt độ/độ ẩm/gas...)?",
        "query_device_status": "Bạn muốn kiểm tra trạng thái thiết bị nào?",
        "activate_scene": "Bạn muốn kích hoạt ngữ cảnh nào (đi ngủ/xem phim/về nhà...)?",
        "environmental_comfort": "Bạn muốn điều chỉnh thoải mái môi trường như thế nào (mát hơn/ấm hơn...)?",
        "security_mode": "Bạn muốn bật hay tắt chế độ an ninh?",
        "security_alert": "Bạn đang báo động sự cố gì (cháy/gas/đột nhập)?",
    }

    return [mapping.get(intent, "Bạn có thể nói rõ yêu cầu được không?")]


async def _classify_with_timeout(
    request: Request,
    sentence: str,
    context_for_ml: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    settings = request.app.state.settings

    hybrid = getattr(request.app.state, "hybrid_classifier", None)
    rule = getattr(request.app.state, "rule_classifier", None)

    if hybrid is not None:
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(hybrid.classify, sentence, context_for_ml),
                timeout=float(settings.inference_timeout_seconds),
            )
        except asyncio.TimeoutError:
            # Fall back to rule-based on timeout.
            if rule is None:
                return {
                    "intent": "unknown",
                    "entities": {},
                    "confidence": 0.0,
                    "classifier_type": "fallback",
                    "fallback_reason": "timeout",
                }

            rule_result = rule.classify(sentence)
            if not rule_result:
                return {
                    "intent": "unknown",
                    "entities": {},
                    "confidence": 0.0,
                    "classifier_type": "rule",
                    "fallback_reason": "timeout",
                }

            return {
                "intent": rule_result.intent,
                "entities": rule_result.entities,
                "confidence": rule_result.confidence,
                "classifier_type": rule_result.classifier_type,
                "fallback_reason": "timeout",
            }

    if rule is None:
        raise ServiceUnavailableError("No classifier available")

    rule_result = rule.classify(sentence)
    if not rule_result:
        return {
            "intent": "unknown",
            "entities": {},
            "confidence": 0.0,
            "classifier_type": "rule",
        }

    return {
        "intent": rule_result.intent,
        "entities": rule_result.entities,
        "confidence": rule_result.confidence,
        "classifier_type": rule_result.classifier_type,
    }


@router.post("/intent/classify")
async def classify_intent(
    payload: IntentClassificationRequest,
    request: Request,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Any:
    endpoint_label = "intent_classify"
    start = time.perf_counter()

    settings = request.app.state.settings
    response_builder = request.app.state.response_builder
    preprocessing = request.app.state.preprocessing
    entity_extractor = request.app.state.entity_extractor
    structured_logger = request.app.state.structured_logger
    rate_limiter = getattr(request.app.state, "rate_limiter", None)
    cache = getattr(request.app.state, "cache", None)

    user_id = payload.user_id or str(user.get("user_id") or user.get("sub") or "unknown")

    if rate_limiter and not rate_limiter.is_allowed(user_id):
        RATE_LIMITED_TOTAL.labels(endpoint=endpoint_label).inc()
        API_REQUESTS_TOTAL.labels(endpoint=endpoint_label, status="rate_limited").inc()
        raise RateLimitError("Rate limit exceeded")

    validation = response_builder.validate_and_build(payload.text)
    if validation.get("status_code"):
        API_REQUESTS_TOTAL.labels(endpoint=endpoint_label, status="validation_error").inc()
        return JSONResponse(status_code=validation["status_code"], content=validation)

    processed = preprocessing.preprocess(payload.text)
    normalized_text = processed.normalized_text
    sentences = processed.sentences

    context_obj = payload.device_context
    context_for_ml = context_obj.model_dump() if context_obj else None

    if cache:
        cached = cache.get(normalized_text, context=context_for_ml)
        if cached is not None:
            CACHE_HITS_TOTAL.labels(endpoint=endpoint_label).inc()
            API_REQUESTS_TOTAL.labels(endpoint=endpoint_label, status="cache_hit").inc()
            duration_s = time.perf_counter() - start
            API_REQUEST_DURATION_SECONDS.labels(endpoint=endpoint_label).observe(duration_s)
            return cached
        CACHE_MISSES_TOTAL.labels(endpoint=endpoint_label).inc()

    intent_responses: List[Dict[str, Any]] = []
    last_intent = "unknown"
    last_confidence = 0.0
    last_classifier_type = "fallback"

    for sentence in sentences:
        result = _normalize_result(await _classify_with_timeout(request, sentence, context_for_ml))

        intent = str(result.get("intent") or "unknown")
        confidence = float(result.get("confidence") or 0.0)
        classifier_type = str(result.get("classifier_type") or "fallback")

        CLASSIFICATION_CONFIDENCE.observe(confidence)

        # Merge entities from classifier (rule-based) and extractor.
        base_entities = dict(result.get("entities") or {})
        extracted_entities = entity_extractor.extract(sentence, intent, context=context_obj)
        merged_entities = {**base_entities, **extracted_entities}

        priority = merged_entities.pop("priority", None)
        if intent == "security_alert":
            priority = priority or "high"

        is_low_conf = confidence < float(settings.confidence_threshold)

        if len(sentences) == 1 and is_low_conf:
            top_intents = _top_intents_to_dicts(result.get("top_k_intents"))
            suggestions = _suggestions_for(top_intents)
            fallback = response_builder.build_fallback_response(
                confidence=confidence,
                suggestions=suggestions,
                top_intents=top_intents,
            )

            if cache:
                cache.set(normalized_text, fallback, context=context_for_ml)

            duration_s = time.perf_counter() - start
            API_REQUESTS_TOTAL.labels(endpoint=endpoint_label, status="fallback").inc()
            API_REQUEST_DURATION_SECONDS.labels(endpoint=endpoint_label).observe(duration_s)

            structured_logger.log_request(
                user_id=user_id,
                text=payload.text,
                intent="unknown",
                confidence=confidence,
                response_time_ms=duration_s * 1000.0,
                classifier_type=classifier_type,
                mode="fallback",
            )
            return fallback

        if is_low_conf:
            # For multi-intent requests, keep the response shape stable.
            intent = "unknown"

        intent_response = response_builder.build_success_response(
            intent=intent,
            entities=merged_entities,
            confidence=confidence,
            classifier_type=classifier_type,
            priority=priority,
        )
        intent_responses.append(intent_response)

        last_intent = intent
        last_confidence = confidence
        last_classifier_type = classifier_type

    if len(intent_responses) == 1:
        final_response: Dict[str, Any] = intent_responses[0]
    else:
        final_response = response_builder.build_multi_intent_response(intent_responses)

    if cache:
        cache.set(normalized_text, final_response, context=context_for_ml)

    duration_s = time.perf_counter() - start
    API_REQUESTS_TOTAL.labels(endpoint=endpoint_label, status="ok").inc()
    API_REQUEST_DURATION_SECONDS.labels(endpoint=endpoint_label).observe(duration_s)

    structured_logger.log_request(
        user_id=user_id,
        text=payload.text,
        intent=last_intent,
        confidence=last_confidence,
        response_time_ms=duration_s * 1000.0,
        classifier_type=last_classifier_type,
    )

    return final_response
