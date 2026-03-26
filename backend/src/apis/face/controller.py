import os

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse
from starlette import status

from . import models
from . import service
from ...rate_limiter import limiter
from ...mqtt_client import publish_command
from ...config.env import DOOR_OPEN_COMMAND, FACE_LAST_IMAGE_PATH

router = APIRouter(
    prefix="/face",
    tags=["Face"]
)


@router.post("/verify", response_model=models.FaceVerifyResponse, status_code=status.HTTP_200_OK)
@limiter.limit("60/minute")
async def verify_face(request: Request, payload: models.FaceVerifyRequest):
    verified, match_id, confidence, reason = service.verify_face_image(payload.image_base64)
    if verified:
        publish_command(DOOR_OPEN_COMMAND)
    return models.FaceVerifyResponse(
        verified=verified,
        match_id=match_id,
        confidence=confidence,
        reason=reason
    )


@router.post("/enroll", response_model=models.FaceEnrollResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def enroll_face(request: Request, payload: models.FaceEnrollRequest):
    saved, image_path, reason = service.enroll_face(payload.person_id, payload.image_base64)
    return models.FaceEnrollResponse(
        saved=saved,
        person_id=payload.person_id,
        image_path=image_path,
        reason=reason
    )


@router.post("/upload", response_model=models.FaceUploadResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("120/minute")
async def upload_face(request: Request, payload: models.FaceUploadRequest):
    saved, reason = service.upload_face_image(payload.image_base64)
    return models.FaceUploadResponse(saved=saved, reason=reason)


@router.get("/last.jpg", status_code=status.HTTP_200_OK)
async def get_last_face_image():
    if not os.path.exists(FACE_LAST_IMAGE_PATH):
        raise HTTPException(status_code=404, detail="No image available")
    return FileResponse(FACE_LAST_IMAGE_PATH, media_type="image/jpeg")
