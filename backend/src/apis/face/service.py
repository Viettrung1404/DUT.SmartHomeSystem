import base64
import os
import shutil
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


def _safe_home_id(home_id: str) -> str:
    safe = "".join(ch for ch in home_id if ch.isalnum() or ch in "-_")
    return safe


def _home_gallery_dir(home_id: str) -> str:
    safe_home_id = _safe_home_id(home_id)
    if not safe_home_id:
        raise HTTPException(status_code=400, detail="home_id is invalid")
    return os.path.join(FACE_GALLERY_DIR, safe_home_id)


def _save_last_image(image_bytes: bytes) -> None:
    os.makedirs(os.path.dirname(FACE_LAST_IMAGE_PATH), exist_ok=True)
    with open(FACE_LAST_IMAGE_PATH, "wb") as image_file:
        image_file.write(image_bytes)


def _clear_home_gallery(home_id: str) -> int:
    home_dir = _home_gallery_dir(home_id)
    if not os.path.isdir(home_dir):
        return 0

    deleted_count = 0
    for root, dirs, files in os.walk(home_dir, topdown=False):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            try:
                os.remove(file_path)
                deleted_count += 1
            except FileNotFoundError:
                continue
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                shutil.rmtree(dir_path)
            except FileNotFoundError:
                continue

    return deleted_count


def enroll_face(home_id: str, person_id: str, image_base64: str) -> Tuple[bool, str | None, str | None]:
    safe_person_id = _safe_person_id(person_id)
    if not safe_person_id:
        return False, None, "person_id is invalid"

    home_dir = _home_gallery_dir(home_id)
    os.makedirs(home_dir, exist_ok=True)

    image_bytes = _decode_image(image_base64)
    _save_last_image(image_bytes)
    filename = "{}_face_{}.jpg".format(safe_person_id, int.from_bytes(os.urandom(4), "big"))
    image_path = os.path.join(home_dir, filename)
    with open(image_path, "wb") as image_file:
        image_file.write(image_bytes)
    embedding_reason = None
    if is_recognition_available():
        _, embedding_reason = save_embedding_for_image(image_bytes, image_path)

    return True, image_path, embedding_reason


def replace_face_gallery(home_id: str, person_id: str, images_base64: list[str]) -> Tuple[int, int, list[str], str | None]:
    safe_person_id = _safe_person_id(person_id)
    if not safe_person_id:
        return 0, 0, [], "person_id is invalid"

    if len(images_base64) != 5:
        return 0, 0, [], "exactly 5 images are required"

    decoded_images = [_decode_image(image_base64) for image_base64 in images_base64]
    home_dir = _home_gallery_dir(home_id)
    os.makedirs(home_dir, exist_ok=True)

    deleted_count = _clear_home_gallery(home_id)
    os.makedirs(home_dir, exist_ok=True)

    saved_paths: list[str] = []
    last_reason = None
    for index, image_bytes in enumerate(decoded_images, start=1):
        _save_last_image(image_bytes)
        filename = "{}_face_{:02d}_{}.jpg".format(
            safe_person_id,
            index,
            int.from_bytes(os.urandom(4), "big"),
        )
        image_path = os.path.join(home_dir, filename)
        with open(image_path, "wb") as image_file:
            image_file.write(image_bytes)
        saved_paths.append(image_path)

        if is_recognition_available():
            _, last_reason = save_embedding_for_image(image_bytes, image_path)

    return len(saved_paths), deleted_count, saved_paths, last_reason


def verify_face_image(image_base64: str) -> Tuple[bool, str | None, float | None, str | None]:
    return False, None, None, "home_id is required"


def verify_face_image_for_home(home_id: str, image_base64: str) -> Tuple[bool, str | None, float | None, str | None]:
    image_bytes = _decode_image(image_base64)
    _save_last_image(image_bytes)
    if not is_recognition_available():
        return False, None, None, "insightface dependency not installed"

    return verify_face(image_bytes, _home_gallery_dir(home_id), FACE_MATCH_THRESHOLD)


def upload_face_image(home_id: str, image_base64: str) -> Tuple[bool, str | None]:
    image_bytes = _decode_image(image_base64)
    _save_last_image(image_bytes)
    return True, None
