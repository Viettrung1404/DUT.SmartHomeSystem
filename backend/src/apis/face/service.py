import base64
import logging
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


def topic_safe_home(home_id: str) -> str:
    h = _safe_segment(home_id)
    if not h:
        raise HTTPException(status_code=400, detail="home_id is invalid")
    return h


def _gallery_dir_for_safe_home(safe_home: str) -> str:
    return os.path.join(FACE_GALLERY_DIR, safe_home)


def _last_image_path_safe(safe_home: str) -> str:
    parent = os.path.dirname(FACE_LAST_IMAGE_PATH) or "."
    base = os.path.join(parent, "face_last_homes")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "{}.jpg".format(safe_home))


def _save_last_image(safe_home: str, image_bytes: bytes) -> None:
    path = _last_image_path_safe(safe_home)
    with open(path, "wb") as image_file:
        image_file.write(image_bytes)


def enroll_face(
    person_id: str, image_base64: str, home_id: str
) -> Tuple[bool, str | None, str | None]:
    safe_home = topic_safe_home(home_id)
    safe_person_id = _safe_segment(person_id)
    if not safe_person_id:
        return False, None, "person_id is invalid"

    gallery_home = _gallery_dir_for_safe_home(safe_home)
    os.makedirs(gallery_home, exist_ok=True)
    person_dir = os.path.join(gallery_home, safe_person_id)
    os.makedirs(person_dir, exist_ok=True)

    image_bytes = _decode_image(image_base64)
    _save_last_image(safe_home, image_bytes)
    filename = "face_{}.jpg".format(int.from_bytes(os.urandom(4), "big"))
    image_path = os.path.join(person_dir, filename)
    with open(image_path, "wb") as image_file:
        image_file.write(image_bytes)
    embedding_reason = None
    if is_recognition_available():
        _, embedding_reason = save_embedding_for_image(image_bytes, image_path)

    return True, image_path, embedding_reason


def enroll_face_batch(
    person_id: str,
    images_base64: list[str],
    home_id: str,
) -> dict:
    safe_home = topic_safe_home(home_id)
    safe_person_id = _safe_segment(person_id)
    if not safe_person_id:
        return {
            "saved": False,
            "home_id": safe_home,
            "person_id": person_id,
            "total_images": len(images_base64),
            "saved_images": 0,
            "embedded_images": 0,
            "image_paths": [],
            "failed_indexes": [],
            "failures": ["person_id is invalid"],
            "reason": "person_id is invalid",
        }

    if len(images_base64) != 5:
        return {
            "saved": False,
            "home_id": safe_home,
            "person_id": safe_person_id,
            "total_images": len(images_base64),
            "saved_images": 0,
            "embedded_images": 0,
            "image_paths": [],
            "failed_indexes": [],
            "failures": ["images_base64 must contain exactly 5 images"],
            "reason": "images_base64 must contain exactly 5 images",
        }

    gallery_home = _gallery_dir_for_safe_home(safe_home)
    os.makedirs(gallery_home, exist_ok=True)
    person_dir = os.path.join(gallery_home, safe_person_id)
    os.makedirs(person_dir, exist_ok=True)

    saved_images = 0
    embedded_images = 0
    image_paths: list[str] = []
    failed_indexes: list[int] = []
    failures: list[str] = []

    for idx, image_base64 in enumerate(images_base64, start=1):
        try:
            image_bytes = _decode_image(image_base64)
            _save_last_image(safe_home, image_bytes)

            filename = "face_batch_{}_{}.jpg".format(
                idx, int.from_bytes(os.urandom(3), "big")
            )
            image_path = os.path.join(person_dir, filename)
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

            image_paths.append(image_path)
            saved_images += 1

            if not is_recognition_available():
                failed_indexes.append(idx)
                failures.append("#{}: insightface dependency not installed".format(idx))
                continue

            embedded_ok, embedding_reason = save_embedding_for_image(image_bytes, image_path)
            if embedded_ok:
                embedded_images += 1
            else:
                failed_indexes.append(idx)
                failures.append("#{}: {}".format(idx, embedding_reason or "embedding failed"))
        except HTTPException as exc:
            failed_indexes.append(idx)
            failures.append("#{}: {}".format(idx, exc.detail))
        except Exception as exc:
            failed_indexes.append(idx)
            failures.append("#{}: {}".format(idx, str(exc)))

    all_embedded = embedded_images == len(images_base64)
    reason = None if all_embedded else "One or more images failed to generate embeddings"

    logging.info(
        "face_enroll_batch home=%s person=%s total=%s saved=%s embedded=%s",
        safe_home,
        safe_person_id,
        len(images_base64),
        saved_images,
        embedded_images,
    )

    return {
        "saved": all_embedded,
        "home_id": safe_home,
        "person_id": safe_person_id,
        "total_images": len(images_base64),
        "saved_images": saved_images,
        "embedded_images": embedded_images,
        "image_paths": image_paths,
        "failed_indexes": failed_indexes,
        "failures": failures,
        "reason": reason,
    }


def verify_face_image(
    image_base64: str, home_id: str
) -> Tuple[bool, str | None, float | None, str | None]:
    safe_home = topic_safe_home(home_id)
    image_bytes = _decode_image(image_base64)
    _save_last_image(safe_home, image_bytes)
    gallery_dir = _gallery_dir_for_safe_home(safe_home)
    if not is_recognition_available():
        return False, None, None, "insightface dependency not installed"

    return verify_face(image_bytes, gallery_dir, FACE_MATCH_THRESHOLD)


def upload_face_image(
    image_base64: str, home_id: str
) -> Tuple[bool, str | None]:
    safe_home = topic_safe_home(home_id)
    image_bytes = _decode_image(image_base64)
    _save_last_image(safe_home, image_bytes)
    return True, None


def last_face_image_path(home_id: str) -> str:
    safe_home = topic_safe_home(home_id)
    return _last_image_path_safe(safe_home)
