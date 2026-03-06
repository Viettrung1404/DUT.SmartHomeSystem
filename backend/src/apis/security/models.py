from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SecurityEventCreate(BaseModel):
    home_id: str
    event_type: str
    severity: str = "low"
    description: str


class SecurityEventResponse(BaseModel):
    id: str
    home_id: str
    event_type: str
    severity: str
    description: str
    timestamp: datetime

    class Config:
        from_attributes = True


class SecuritySummaryResponse(BaseModel):
    risk_level: str  # 'low', 'medium', 'high'
    total_events: int
    high_count: int
    medium_count: int
    low_count: int
    recent_events: List[SecurityEventResponse]
