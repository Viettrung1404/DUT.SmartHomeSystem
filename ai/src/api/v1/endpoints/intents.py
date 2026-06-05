from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Request

from src.api.auth import get_current_user

router = APIRouter()


@router.get("/intents")
async def list_intents(
    request: Request,
    _user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    intents: List[str] = getattr(request.app.state, "available_intents", [])
    return {"intents": intents, "count": len(intents)}
