from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class AssistantChatRequest(BaseModel):
    message: str
    home_id: str | None = None
    execute_if_confident: bool = True


class AssistantExecutionResult(BaseModel):
    status: Literal["executed", "skipped", "failed"]
    device_id: str | None = None
    command: str | None = None
    value: Any | None = None
    reason: str | None = None


class AssistantChatResponse(BaseModel):
    reply_text: str
    nlu: dict[str, Any]
    grounding: dict[str, Any] = Field(default_factory=dict)
    action_draft: dict[str, Any] | None = None
    follow_up_question: str | None = None
    safety_flags: list[str] = Field(default_factory=list)
    execution: AssistantExecutionResult
    home_id: str
