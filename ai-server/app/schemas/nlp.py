from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .common import ActionDraft, CandidateIntent, HomeContext


class ExtractedEntities(BaseModel):
    room_name: str | None = None
    room_id: str | None = None
    device_name: str | None = None
    device_id: str | None = None
    device_type: str | None = None
    action: str | None = None
    value: Any | None = None
    scope: str | None = None
    scene: str | None = None
    sensor_type: str | None = None
    comfort_type: str | None = None


class ParseRequest(BaseModel):
    text: str
    locale: str = "vi-VN"
    context: HomeContext | None = None


class ParseResponse(BaseModel):
    intent: str
    confidence: float
    normalized_text: str
    entities: ExtractedEntities
    candidate_intents: list[CandidateIntent] = Field(default_factory=list)
    missing_slots: list[str] = Field(default_factory=list)
    out_of_scope: bool = False
    explanation: list[str] = Field(default_factory=list)
    action_draft: ActionDraft | None = None
