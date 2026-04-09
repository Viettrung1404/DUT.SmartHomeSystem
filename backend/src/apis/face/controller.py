import os

from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import FileResponse
from starlette import status

from . import models
from . import service
from ...rate_limiter import limiter
from ...mqtt_client import publish_command
from ...config.env import DOOR_OPEN_COMMAND, DEFAULT_HOME_ID, DEFAULT_DEVICE_ID

router = APIRouter(
    prefix="/face",
    tags=["Face"]
)


@router.post("/verify", response_model=models.FaceVerifyResponse, status_code=status.HTTP_200_OK)
@limiter.limit("60/minute")
async def verify_face(request: Request, payload: models.FaceVerifyRequest):
    safe_home, safe_device = service.topic_safe_home_device(
        payload.home_id, payload.device_id
    )
    verified, match_id, confidence, reason = service.verify_face_image(
        payload.image_base64, payload.home_id, payload.device_id
    )
    if verified:
        publish_command(DOOR_OPEN_COMMAND, safe_home, safe_device)
    return models.FaceVerifyResponse(
        verified=verified,
        match_id=match_id,
        confidence=confidence,
        reason=reason
    )


@router.post("/enroll", response_model=models.FaceEnrollResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def enroll_face(request: Request, payload: models.FaceEnrollRequest):
    saved, image_path, reason = service.enroll_face(
        payload.person_id, payload.image_base64, payload.home_id, payload.device_id
    )
    return models.FaceEnrollResponse(
        saved=saved,
        person_id=payload.person_id,
        image_path=image_path,
        reason=reason
    )


@router.post("/upload", response_model=models.FaceUploadResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("120/minute")
async def upload_face(request: Request, payload: models.FaceUploadRequest):
    saved, reason = service.upload_face_image(
        payload.image_base64, payload.home_id, payload.device_id
    )
    return models.FaceUploadResponse(saved=saved, reason=reason)


@router.get("/last.jpg", status_code=status.HTTP_200_OK)
async def get_last_face_image(
    home_id: str | None = Query(default=None),
    device_id: str | None = Query(default=None),
):
    hid = (home_id or DEFAULT_HOME_ID).strip()
    did = (device_id or DEFAULT_DEVICE_ID).strip()
    path = service.last_face_image_path(hid, did)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="No image available")
    return FileResponse(path, media_type="image/jpeg")
