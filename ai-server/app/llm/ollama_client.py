import json
import logging
from typing import Any

import httpx

from app.config import get_settings
from app.llm.prompts import SYSTEM_PROMPT, build_user_prompt


logger = logging.getLogger("ai_server.ollama")


def check_ollama() -> str:
    settings = get_settings()
    try:
        with httpx.Client(timeout=3) as client:
            response = client.get(f"{settings.ollama_url.rstrip('/')}/api/tags")
            return "ok" if response.status_code < 500 else "error"
    except Exception:
        return "unavailable"


def generate_answer(message: str, memory_context: dict[str, Any] | None, tool_results: list[dict[str, Any]]) -> dict[str, Any] | None:
    settings = get_settings()
    payload = {
        "model": settings.ollama_model,
        "stream": False,
        "format": "json",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(message, memory_context, tool_results)},
        ],
    }
    try:
        with httpx.Client(timeout=settings.request_timeout_seconds) as client:
            response = client.post(f"{settings.ollama_url.rstrip('/')}/api/chat", json=payload)
            response.raise_for_status()
            content = response.json().get("message", {}).get("content", "{}")
            parsed = json.loads(content)
            if isinstance(parsed, dict) and parsed.get("answer"):
                return parsed
    except Exception as exc:
        logger.warning("ollama.generate_failed url=%s model=%s error=%s", settings.ollama_url, settings.ollama_model, exc)
        return None
    return None
