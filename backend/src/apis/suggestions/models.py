from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
from uuid import UUID


class SuggestionResponse(BaseModel):
    id: int
    user_id: UUID
    pattern_id: Optional[int] = None
    action_type: str  # "SCHEDULE" | "ALERT" | "AUTOMATION"
    suggestion_text: str
    suggestion_json: Optional[dict[str, Any]] = None
    was_accepted: Optional[bool] = None
    latest_feedback_type: Optional[str] = None
    latest_feedback_reason: Optional[str] = None
    feedback_time: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SuggestionsListResponse(BaseModel):
    total: int
    suggestions: list[SuggestionResponse]


class SuggestionAcceptRequest(BaseModel):
    was_accepted: bool
    action_taken: Optional[str] = None  # e.g., "SCHEDULED", "DISMISSED"


class SuggestionFeedbackRequest(BaseModel):
    feedback_type: str  # ACCEPT | REJECT | IGNORE
    feedback_reason: Optional[str] = None


class SuggestionFeedbackResponse(BaseModel):
    suggestion_id: int
    user_id: UUID
    feedback_type: str
    feedback_reason: Optional[str] = None
    feedback_time: datetime


# ─── Dashboard Metrics ───────────────────────────────────────────────────────

class FeedbackStats(BaseModel):
    accepted: int
    rejected: int
    ignored: int
    total_feedback: int


class ActionTypeStats(BaseModel):
    SCHEDULE: int
    ALERT: int
    AUTOMATION: int


class TrendPoint(BaseModel):
    date: str
    count: int


class PatternEfficiency(BaseModel):
    pattern_type: str
    sent: int
    accepted: int
    accept_rate: float


class SuggestionDashboardResponse(BaseModel):
    # A. Suggestion Metrics
    sent_count: int
    feedback: FeedbackStats
    
    # B. Quality Metrics
    effective_accept_rate: float  # accepted / (sent - suppressed) -> thực ra là accepted / total_sent trong DB
    rejection_rate: float
    ignore_rate: float
    false_alert_rate: float       # rejected / total_sent
    
    # C. Guardrail Metrics
    cooldown_suppressions: int
    avg_suggestions_per_day: float
    
    # Distributions & Trends
    action_type_dist: ActionTypeStats
    top_accepted_patterns: list[PatternEfficiency]
    daily_trend: list[TrendPoint]
    
    # Additional Context
    top_rejection_reasons: list[dict[str, Any]]
