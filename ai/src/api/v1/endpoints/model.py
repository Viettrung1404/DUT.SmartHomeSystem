from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, Request

from src.api.auth import require_admin
from src.bootstrap import load_models
from src.monitoring.metrics import MODEL_RELOADS_TOTAL

router = APIRouter()


@router.post("/model/reload")
async def reload_model(
    request: Request,
    _user: Dict[str, Any] = Depends(require_admin),
) -> Dict[str, Any]:
    try:
        load_models(request.app)
        MODEL_RELOADS_TOTAL.labels(status="ok").inc()
        return {"status": "ok", "message": "Models reloaded"}
    except Exception:
        MODEL_RELOADS_TOTAL.labels(status="error").inc()
        raise
