from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RoomContext(BaseModel):
    id: str | None = None
    name: str
    aliases: list[str] = Field(default_factory=list)


class DeviceContext(BaseModel):
    id: str | None = None
    room_id: str | None = None
    name: str
    type: str
    aliases: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    online_status: bool = True
    status: bool = False


class HomeContext(BaseModel):
    rooms: list[RoomContext] = Field(default_factory=list)
    devices: list[DeviceContext] = Field(default_factory=list)
    current_state_notes: list[str] = Field(default_factory=list)


class CandidateIntent(BaseModel):
    name: str
    score: float
    source: str


class ActionDraft(BaseModel):
    device_id: str | None = None
    device_type: str | None = None
    room_id: str | None = None
    action: str
    value: Any | None = None
    scope: str | None = None


class TopSignal(BaseModel):
    feature: str
    importance: float
    value: float | int | bool | None = None


class PredictionInterval(BaseModel):
    lower: float
    median: float
    upper: float


class HealthModelStatus(BaseModel):
    name: str
    artifact_present: bool
    version: str
    status: str
    metrics_available: bool


class TimestampedValue(BaseModel):
    timestamp: datetime
    value: float
