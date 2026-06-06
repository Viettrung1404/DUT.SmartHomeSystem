from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .common import ActionDraft, HomeContext
from .nlp import ParseResponse


class ChatRequest(BaseModel):
    message: str
    conversation_state: dict[str, Any] | None = None
    home_context: HomeContext | None = None


class ChatResponse(BaseModel):
    reply_text: str
    nlu: ParseResponse
    grounding: dict[str, Any] = Field(default_factory=dict)
    action_draft: ActionDraft | None = None
    follow_up_question: str | None = None
    safety_flags: list[str] = Field(default_factory=list)
