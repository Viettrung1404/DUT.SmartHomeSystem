from pydantic import BaseModel, Field
from typing import Optional


class FaceVerifyRequest(BaseModel):
    home_id: str = Field(..., min_length=1)
    device_id: str = Field(..., min_length=1)
    image_base64: str = Field(..., min_length=1)


class FaceVerifyResponse(BaseModel):
    verified: bool
    match_id: Optional[str] = None
    confidence: Optional[float] = None
    reason: Optional[str] = None


class FaceEnrollRequest(BaseModel):
    home_id: str = Field(..., min_length=1)
    device_id: str = Field(..., min_length=1)
    person_id: str = Field(..., min_length=1)
    image_base64: str = Field(..., min_length=1)


class FaceEnrollResponse(BaseModel):
    saved: bool
    person_id: str
    image_path: Optional[str] = None
    reason: Optional[str] = None


class FaceUploadRequest(BaseModel):
    home_id: str = Field(..., min_length=1)
    device_id: str = Field(..., min_length=1)
    image_base64: str = Field(..., min_length=1)


class FaceUploadResponse(BaseModel):
    saved: bool
    reason: Optional[str] = None
