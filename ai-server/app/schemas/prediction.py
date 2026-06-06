from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from .common import PredictionInterval, TopSignal


class InlineHistoryPoint(BaseModel):
    timestamp: datetime
    temperature: float
    humidity: float
    occupancy_ratio: float | None = None
    fan_on: bool | None = None
    rain_detected: bool | None = None
    outdoor_temp: float | None = None


class DBSource(BaseModel):
    home_id: str | None = None
    room_id: str | None = None
    device_id: str | None = None
    lookback_minutes: int = 180


class PredictEnvironmentRequest(BaseModel):
    inline_history: list[InlineHistoryPoint] | None = None
    db_source: DBSource | None = None
    horizon_minutes: int = 30
    locale: str = "vi-VN"

    @model_validator(mode="after")
    def validate_source(self) -> "PredictEnvironmentRequest":
        if not self.inline_history and not self.db_source:
            raise ValueError("inline_history hoặc db_source là bắt buộc")
        return self


class PredictEnvironmentResponse(BaseModel):
    temperature_next_30min: float
    humidity_next_30min: float
    temperature_interval: PredictionInterval
    humidity_interval: PredictionInterval
    comfort_proxy: str
    comfort_note: str
    recommended_action_hint: str
    top_signals: list[TopSignal] = Field(default_factory=list)
    model_version: str
    training_metrics: dict = Field(default_factory=dict)


class BatchPredictionItem(BaseModel):
    request_id: str
    request: PredictEnvironmentRequest


class BatchPredictionRequest(BaseModel):
    items: list[BatchPredictionItem]


class BatchPredictionResult(BaseModel):
    request_id: str
    prediction: PredictEnvironmentResponse
