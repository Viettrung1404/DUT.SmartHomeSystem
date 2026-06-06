import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.config.env import AI_SERVER_API_KEY, AI_SERVER_URL
from src.entities.models import HomeUser


def ensure_home_member(db: Session, home_id, user_id) -> None:
    member = (
        db.query(HomeUser)
        .filter(HomeUser.home_id == home_id, HomeUser.user_id == user_id)
        .first()
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of this home",
        )


async def forward_chat(payload: dict) -> dict:
    headers = {}
    if AI_SERVER_API_KEY:
        headers["X-API-Key"] = AI_SERVER_API_KEY

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{AI_SERVER_URL.rstrip('/')}/v1/chat",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"AI Server rejected request: {exc.response.text}",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Trợ lý AI hiện chưa sẵn sàng, vui lòng thử lại sau.",
        ) from exc


async def reset_memory(payload: dict) -> dict:
    headers = {}
    if AI_SERVER_API_KEY:
        headers["X-API-Key"] = AI_SERVER_API_KEY

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{AI_SERVER_URL.rstrip('/')}/v1/chat/reset",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Trợ lý AI hiện chưa sẵn sàng, vui lòng thử lại sau.",
        ) from exc

