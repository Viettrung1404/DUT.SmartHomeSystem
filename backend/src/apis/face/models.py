from pydantic import BaseModel, Field
from typing import Optional


class FaceVerifyRequest(BaseModel):
    home_id: str = Field(..., min_length=1)
    device_id: str = Field(..., min_length=1)
    image_base64: str = Field(..., min_length=1)


class FaceVerifyResponse(BaseModel):
    verified: bool
    match_id: Optional[str] = None
    confidence: Optional[float] = Field(None, description="Match confidence from 0.0 to 1.0 (multiply by 100 for percentage)")
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


class FaceEnrollBatchRequest(BaseModel):
    home_id: str = Field(..., min_length=1)
    person_id: str = Field(..., min_length=1)
    images_base64: list[str]


class FaceEnrollBatchResponse(BaseModel):
    saved_count: int
    deleted_count: int
    person_id: str
    image_paths: list[str] = Field(default_factory=list)
    reason: Optional[str] = None
