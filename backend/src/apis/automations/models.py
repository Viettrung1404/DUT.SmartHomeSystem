from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ConditionCreate(BaseModel):
    condition_type: str  # 'time', 'device_status', 'motion', 'energy', 'temperature'
    value: str


class ActionCreate(BaseModel):
    device_id: Optional[str] = None
    action: str  # 'toggle', 'set_brightness', 'set_temperature', 'lock', 'notify'
    value: Optional[str] = None


class AutomationCreate(BaseModel):
    home_id: str
    name: str
    conditions: List[ConditionCreate]
    actions: List[ActionCreate]


class AutomationUpdate(BaseModel):
    name: Optional[str] = None
    enabled: Optional[bool] = None


class ConditionResponse(BaseModel):
    id: str
    condition_type: str
    value: str
    class Config:
        from_attributes = True


class ActionResponse(BaseModel):
    id: str
    device_id: Optional[str]
    action: str
    value: Optional[str]
    class Config:
        from_attributes = True


class AutomationResponse(BaseModel):
    id: str
    home_id: str
    name: str
    enabled: bool
    created_at: datetime
    conditions: List[ConditionResponse] = []
    actions: List[ActionResponse] = []
    class Config:
        from_attributes = True
