from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RoomCreate(BaseModel):
    home_id: str
    name: str
    icon: Optional[str] = "home"


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None


class RoomResponse(BaseModel):
    id: str
    home_id: str
    name: str
    icon: Optional[str]
    created_at: datetime
    device_count: int = 0
    active_devices: int = 0
    energy_today: float = 0.0
    is_online: bool = True

    class Config:
        from_attributes = True
