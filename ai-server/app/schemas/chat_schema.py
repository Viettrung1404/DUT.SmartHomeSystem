from typing import Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)
    home_id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    timezone: str = "Asia/Ho_Chi_Minh"


class ResetMemoryRequest(BaseModel):
    session_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)


class ChatResponse(BaseModel):
    answer: str
    intent: str
    used_tools: list[str] = []
    evidence: list[dict[str, Any]] = []
    suggested_actions: list[str] = []
    memory_updated: bool = False
    severity: str = "none"
    device_command: dict[str, Any] | None = None
    device_commands: list[dict[str, Any]] = []
