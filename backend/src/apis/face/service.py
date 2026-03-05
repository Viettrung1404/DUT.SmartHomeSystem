import base64
import os
from typing import Tuple

from fastapi import HTTPException

from src.config.env import FACE_GALLERY_DIR, FACE_MATCH_THRESHOLD, FACE_LAST_IMAGE_PATH
from src.ai.face_recognition import verify_face, is_recognition_available, save_embedding_for_image


def _strip_base64_prefix(image_base64: str) -> str:
    if "," in image_base64:
        return image_base64.split(",", 1)[1]
    return image_base64


def _decode_image(image_base64: str) -> bytes:
    try:
        return base64.b64decode(_strip_base64_prefix(image_base64), validate=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid image_base64") from exc


def _safe_person_id(person_id: str) -> str:
    safe = "".join(ch for ch in person_id if ch.isalnum() or ch in "-_")
    return safe


def _save_last_image(image_bytes: bytes) -> None:
    os.makedirs(os.path.dirname(FACE_LAST_IMAGE_PATH), exist_ok=True)
    with open(FACE_LAST_IMAGE_PATH, "wb") as image_file:
        image_file.write(image_bytes)


def enroll_face(person_id: str, image_base64: str) -> Tuple[bool, str | None, str | None]:
    safe_person_id = _safe_person_id(person_id)
    if not safe_person_id:
        return False, None, "person_id is invalid"

    os.makedirs(FACE_GALLERY_DIR, exist_ok=True)
    person_dir = os.path.join(FACE_GALLERY_DIR, safe_person_id)
    os.makedirs(person_dir, exist_ok=True)

    image_bytes = _decode_image(image_base64)
    _save_last_image(image_bytes)
    filename = "face_{}.jpg".format(int.from_bytes(os.urandom(4), "big"))
    image_path = os.path.join(person_dir, filename)
    with open(image_path, "wb") as image_file:
        image_file.write(image_bytes)
    embedding_reason = None
    if is_recognition_available():
        _, embedding_reason = save_embedding_for_image(image_bytes, image_path)

    return True, image_path, embedding_reason


def verify_face_image(image_base64: str) -> Tuple[bool, str | None, float | None, str | None]:
    image_bytes = _decode_image(image_base64)
    _save_last_image(image_bytes)
    if not is_recognition_available():
        return False, None, None, "insightface dependency not installed"

    return verify_face(image_bytes, FACE_GALLERY_DIR, FACE_MATCH_THRESHOLD)


def upload_face_image(image_base64: str) -> Tuple[bool, str | None]:
    image_bytes = _decode_image(image_base64)
    _save_last_image(image_bytes)
    return True, None
