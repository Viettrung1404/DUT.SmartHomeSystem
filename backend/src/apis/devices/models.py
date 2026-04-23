from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class DeviceCreate(BaseModel):
    home_id: str
    name: str
    type: str  # 'light', 'ac', 'sensor', 'camera', 'lock', 'fan', 'curtain'
    location: Optional[str] = None  # 'phòng khách', 'phòng ngủ', 'bếp', v.v.
    metadata: Optional[dict] = None


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    metadata: Optional[dict] = None


class DeviceResponse(BaseModel):
    id: str
    home_id: str
    name: str
    type: str
    location: Optional[str] = None
    status: bool
    online_status: bool
    last_seen: Optional[datetime]
    metadata: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DeviceToggleRequest(BaseModel):
    status: bool


class DeviceCommandRequest(BaseModel):
    command: str  # 'set_brightness', 'set_temperature', 'set_mode', 'lock', 'unlock'
    value: Optional[Any] = None


class DeviceLogResponse(BaseModel):
    id: str
    device_id: str
    action: str
    value: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True
