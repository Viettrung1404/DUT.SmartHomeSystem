from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class DeviceCreate(BaseModel):
    room_id: str
    name: str
    type: str  # 'light', 'ac', 'sensor', 'camera', 'lock', 'fan', 'curtain'
    metadata: Optional[dict] = None


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    metadata: Optional[dict] = None


class DeviceResponse(BaseModel):
    id: str
    room_id: str
    name: str
    type: str
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
