from pydantic import BaseModel, Field
from typing import Optional


class FaceVerifyRequest(BaseModel):
    home_id: str = Field(..., min_length=1)
    image_base64: str = Field(..., min_length=1)


class FaceVerifyResponse(BaseModel):
    verified: bool
    match_id: Optional[str] = None
    confidence: Optional[float] = None
    reason: Optional[str] = None


class FaceEnrollRequest(BaseModel):
    home_id: str = Field(..., min_length=1)
    person_id: str = Field(..., min_length=1)
    image_base64: str = Field(..., min_length=1)


class FaceEnrollResponse(BaseModel):
    saved: bool
    person_id: str
    image_path: Optional[str] = None
    reason: Optional[str] = None


class FaceEnrollBatchRequest(BaseModel):
    home_id: str = Field(..., min_length=1)
    person_id: str = Field(..., min_length=1)
    images_base64: list[str] = Field(..., min_length=5, max_length=5)


class FaceEnrollBatchResponse(BaseModel):
    saved: bool
    home_id: str
    person_id: str
    total_images: int
    saved_images: int
    embedded_images: int
    image_paths: list[str] = Field(default_factory=list)
    failed_indexes: list[int] = Field(default_factory=list)
    failures: list[str] = Field(default_factory=list)
    reason: Optional[str] = None


class FaceUploadRequest(BaseModel):
    home_id: str = Field(..., min_length=1)
    image_base64: str = Field(..., min_length=1)


class FaceUploadResponse(BaseModel):
    saved: bool
    reason: Optional[str] = None
