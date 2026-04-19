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
    created_at: datetime

    class Config:
        from_attributes = True


class SuggestionsListResponse(BaseModel):
    total: int
    suggestions: list[SuggestionResponse]


class SuggestionAcceptRequest(BaseModel):
    was_accepted: bool
    action_taken: Optional[str] = None  # e.g., "SCHEDULED", "DISMISSED"
