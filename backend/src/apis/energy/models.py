from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class EnergyDataPoint(BaseModel):
    label: str
    value: float


class EnergyBreakdown(BaseModel):
    device_name: str
    device_type: str
    usage: float
    percentage: float


class EnergySummaryResponse(BaseModel):
    total: float
    data: List[EnergyDataPoint]
    breakdown: List[EnergyBreakdown] = []
    comparison: Optional[float] = None  # percentage change from previous period
