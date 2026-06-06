from fastapi import Header, HTTPException, status

from app.config import get_settings


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    expected = get_settings().ai_server_api_key
    if expected and expected != "change_me" and x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid AI Server API key",
        )

