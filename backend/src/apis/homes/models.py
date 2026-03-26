from uuid import UUID
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# --- Home ---
class HomeCreate(BaseModel):
    name: str
    address: Optional[str] = None

class HomeUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None

class HomeResponse(BaseModel):
    id: str
    owner_id: str
    name: str
    address: Optional[str]
    created_at: datetime
    room_count: int = 0
    device_count: int = 0
    active_devices: int = 0
    class Config:
        from_attributes = True

class HomeMemberResponse(BaseModel):
    id: str
    user_id: str
    email: str
    full_name: str
    role: str
    class Config:
        from_attributes = True

class AddMemberRequest(BaseModel):
    email: str
    role: str = "member"
