from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class SmartHomeChatRequest(BaseModel):
    home_id: UUID
    message: str = Field(min_length=1)
    session_id: str | None = None
    timezone: str = "Asia/Ho_Chi_Minh"


class SmartHomeChatResponse(BaseModel):
    answer: str
    intent: str
    used_tools: list[str] = []
    evidence: list[dict[str, Any]] = []
    suggested_actions: list[str] = []
    memory_updated: bool = False
    severity: str = "none"
    device_command: dict[str, Any] | None = None
    device_commands: list[dict[str, Any]] = []
    command_executed: bool = False
    command_result: dict[str, Any] | None = None
    command_results: list[dict[str, Any]] = []


class ResetSmartHomeChatRequest(BaseModel):
    session_id: str
