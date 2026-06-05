from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from src.api.auth import get_current_user

router = APIRouter()


@router.get("/metrics")
async def get_metrics(
    _user: Dict[str, Any] = Depends(get_current_user),
) -> Response:
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
