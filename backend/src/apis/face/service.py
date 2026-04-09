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


def _safe_segment(value: str) -> str:
    safe = "".join(ch for ch in value.strip() if ch.isalnum() or ch in "-_")
    return safe


def topic_safe_home_device(home_id: str, device_id: str) -> tuple[str, str]:
    h = _safe_segment(home_id)
    d = _safe_segment(device_id)
    if not h or not d:
        raise HTTPException(status_code=400, detail="home_id or device_id is invalid")
    return h, d


def _gallery_dir_for_safe_home(safe_home: str) -> str:
    return os.path.join(FACE_GALLERY_DIR, safe_home)


def _last_image_path_safe(safe_home: str, safe_device: str) -> str:
    parent = os.path.dirname(FACE_LAST_IMAGE_PATH) or "."
    base = os.path.join(parent, "face_last_devices")
    directory = os.path.join(base, safe_home)
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, "{}.jpg".format(safe_device))


def _save_last_image(safe_home: str, safe_device: str, image_bytes: bytes) -> None:
    path = _last_image_path_safe(safe_home, safe_device)
    with open(path, "wb") as image_file:
        image_file.write(image_bytes)


def enroll_face(
    person_id: str, image_base64: str, home_id: str, device_id: str
) -> Tuple[bool, str | None, str | None]:
    safe_home, safe_device = topic_safe_home_device(home_id, device_id)
    safe_person_id = _safe_segment(person_id)
    if not safe_person_id:
        return False, None, "person_id is invalid"

    gallery_home = _gallery_dir_for_safe_home(safe_home)
    os.makedirs(gallery_home, exist_ok=True)
    person_dir = os.path.join(gallery_home, safe_person_id)
    os.makedirs(person_dir, exist_ok=True)

    image_bytes = _decode_image(image_base64)
    _save_last_image(safe_home, safe_device, image_bytes)
    filename = "face_{}.jpg".format(int.from_bytes(os.urandom(4), "big"))
    image_path = os.path.join(person_dir, filename)
    with open(image_path, "wb") as image_file:
        image_file.write(image_bytes)
    embedding_reason = None
    if is_recognition_available():
        _, embedding_reason = save_embedding_for_image(image_bytes, image_path)

    return True, image_path, embedding_reason


def verify_face_image(
    image_base64: str, home_id: str, device_id: str
) -> Tuple[bool, str | None, float | None, str | None]:
    safe_home, safe_device = topic_safe_home_device(home_id, device_id)
    image_bytes = _decode_image(image_base64)
    _save_last_image(safe_home, safe_device, image_bytes)
    gallery_dir = _gallery_dir_for_safe_home(safe_home)
    if not is_recognition_available():
        return False, None, None, "insightface dependency not installed"

    return verify_face(image_bytes, gallery_dir, FACE_MATCH_THRESHOLD)


def upload_face_image(
    image_base64: str, home_id: str, device_id: str
) -> Tuple[bool, str | None]:
    safe_home, safe_device = topic_safe_home_device(home_id, device_id)
    image_bytes = _decode_image(image_base64)
    _save_last_image(safe_home, safe_device, image_bytes)
    return True, None


def last_face_image_path(home_id: str, device_id: str) -> str:
    safe_home, safe_device = topic_safe_home_device(home_id, device_id)
    return _last_image_path_safe(safe_home, safe_device)
