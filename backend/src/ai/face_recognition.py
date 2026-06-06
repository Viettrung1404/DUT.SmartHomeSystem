from __future__ import annotations

import logging
import os
from typing import List, Tuple

try:
    import cv2
    import numpy as np
    from insightface.app import FaceAnalysis
except ImportError:
    cv2 = None
    np = None
    FaceAnalysis = None

from src.config.env import FACE_MODEL_NAME, FACE_PROVIDER, FACE_DET_SIZE


_face_app: FaceAnalysis | None = None


logger = logging.getLogger(__name__)


def is_recognition_available() -> bool:
    return cv2 is not None and np is not None and FaceAnalysis is not None


def _get_face_app() -> FaceAnalysis:
    global _face_app
    if _face_app is not None:
        return _face_app

    logger.info(
        "Face recognition initializing model name=%s providers=%s det_size=%s",
        FACE_MODEL_NAME,
        FACE_PROVIDER,
        FACE_DET_SIZE,
    )
    providers = [p.strip() for p in FACE_PROVIDER.split(",") if p.strip()]
    det_size_parts = [int(part) for part in FACE_DET_SIZE.split(",") if part.strip().isdigit()]
    det_size = (det_size_parts[0], det_size_parts[1]) if len(det_size_parts) == 2 else (640, 640)

    app = FaceAnalysis(name=FACE_MODEL_NAME, providers=providers)
    app.prepare(ctx_id=0, det_size=det_size)
    _face_app = app
    return app


def _load_image_bytes(image_bytes: bytes):
    logger.info("Face recognition decoding image bytes size=%s", len(image_bytes))
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if image is None:
        logger.info("Face recognition failed to decode image bytes into cv2 image")
        return None
    logger.info("Face recognition decoded image shape=%s", getattr(image, "shape", None))
    return image


def _extract_embedding(image) -> np.ndarray | None:
    app = _get_face_app()
    faces = app.get(image)
    logger.info("Face recognition detected faces count=%s", len(faces))
    if not faces:
        return None
    embedding = faces[0].embedding
    logger.info(
        "Face recognition using first detected face embedding_length=%s",
        len(embedding) if embedding is not None else None,
    )
    return embedding


def extract_embedding_from_bytes(image_bytes: bytes) -> np.ndarray | None:
    if not is_recognition_available():
        logger.info("Face recognition unavailable while extracting embedding from bytes")
        return None
    image = _load_image_bytes(image_bytes)
    if image is None:
        return None
    return _extract_embedding(image)


def _embedding_path_for_image(image_path: str) -> str:
    base, _ = os.path.splitext(image_path)
    return "{}.npy".format(base)


def save_embedding_for_image(image_bytes: bytes, image_path: str) -> Tuple[bool, str | None]:
    if not is_recognition_available():
        return False, "insightface dependency not installed"

    logger.info("Face recognition saving embedding image_path=%s", image_path)
    embedding = extract_embedding_from_bytes(image_bytes)
    if embedding is None:
        logger.info("Face recognition could not create embedding for image_path=%s", image_path)
        return False, "no face detected"

    embedding_path = _embedding_path_for_image(image_path)
    try:
        np.save(embedding_path, embedding)
        logger.info("Face recognition saved embedding_path=%s", embedding_path)
    except Exception:
        return False, "failed to save embedding"
    return True, None


def _load_embedding_from_file(embedding_path: str) -> np.ndarray | None:
    try:
        embedding = np.load(embedding_path)
        logger.info(
            "Face recognition loaded embedding_path=%s embedding_length=%s",
            embedding_path,
            len(embedding) if embedding is not None else None,
        )
        return embedding
    except Exception:
        logger.info("Face recognition failed loading embedding_path=%s", embedding_path)
        return None


def _load_gallery_embeddings(gallery_dir: str) -> Tuple[List[str], List[np.ndarray]]:
    match_ids: List[str] = []
    embeddings: List[np.ndarray] = []
    if not os.path.isdir(gallery_dir):
        logger.info("Face recognition gallery directory missing gallery_dir=%s", gallery_dir)
        return match_ids, embeddings

    logger.info("Face recognition scanning gallery_dir=%s", gallery_dir)
    home_id = os.path.basename(os.path.normpath(gallery_dir))
    for entry_name in sorted(os.listdir(gallery_dir)):
        entry_path = os.path.join(gallery_dir, entry_name)
        lower_name = entry_name.lower()

        if os.path.isdir(entry_path):
            logger.info(
                "Face recognition skipping nested folder in home gallery home_id=%s folder=%s",
                home_id,
                entry_path,
            )
            continue

        try:
            embedding = None
            if lower_name.endswith(".npy"):
                logger.info(
                    "Face recognition loading home-level embedding home_id=%s file=%s",
                    home_id,
                    entry_path,
                )
                embedding = _load_embedding_from_file(entry_path)
            elif lower_name.endswith((".jpg", ".jpeg", ".png")):
                embedding_path = _embedding_path_for_image(entry_path)
                logger.info(
                    "Face recognition inspecting home-level image home_id=%s file=%s embedding_path=%s",
                    home_id,
                    entry_path,
                    embedding_path,
                )
                if os.path.exists(embedding_path):
                    logger.info("Face recognition found cached embedding for home-level image file=%s", entry_path)
                    embedding = _load_embedding_from_file(embedding_path)
                if embedding is None:
                    logger.info("Face recognition extracting embedding from home-level image file=%s", entry_path)
                    image = cv2.imread(entry_path)
                    if image is None:
                        logger.info("Face recognition failed to read home-level image file=%s", entry_path)
                        continue
                    embedding = _extract_embedding(image)
                    if embedding is not None:
                        np.save(embedding_path, embedding)
                        logger.info("Face recognition cached home-level embedding_path=%s", embedding_path)
            else:
                continue

            if embedding is None:
                logger.info("Face recognition skipped empty embedding file=%s", entry_path)
                continue

            match_ids.append(home_id)
            embeddings.append(embedding)
            logger.info(
                "Face recognition enrolled home-level entry home_id=%s source=%s total_loaded=%s",
                home_id,
                entry_path,
                len(embeddings),
            )
        except Exception:
            logger.exception("Face recognition error while loading home-level file=%s", entry_path)
            continue

    return match_ids, embeddings


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a_norm = a / (np.linalg.norm(a) + 1e-8)
    b_norm = b / (np.linalg.norm(b) + 1e-8)
    return float(np.dot(a_norm, b_norm))


def verify_face(image_bytes: bytes, gallery_dir: str, threshold: float) -> Tuple[bool, str | None, float | None, str | None]:
    if not is_recognition_available():
        return False, None, None, "insightface dependency not installed"

    logger.info("Face recognition verify start gallery_dir=%s threshold=%.3f", gallery_dir, threshold)
    match_ids, known_embeddings = _load_gallery_embeddings(gallery_dir)
    logger.info("Face recognition gallery load complete match_count=%s", len(known_embeddings))
    if not known_embeddings:
        return False, None, None, "no known faces enrolled"

    image = _load_image_bytes(image_bytes)
    if image is None:
        return False, None, None, "invalid image"

    probe_embedding = _extract_embedding(image)
    if probe_embedding is None:
        return False, None, None, "no face detected"

    logger.info("Face recognition probe embedding ready length=%s", len(probe_embedding))

    similarities = []
    for match_id, embedding in zip(match_ids, known_embeddings):
        similarity = _cosine_similarity(probe_embedding, embedding)
        similarities.append(similarity)
        logger.info(
            "Face recognition compare match_id=%s similarity=%.4f threshold=%.4f",
            match_id,
            similarity,
            threshold,
        )

    best_index = int(np.argmax(similarities))
    best_similarity = float(similarities[best_index])
    confidence = round(max(0.0, min(1.0, best_similarity)), 3)
    logger.info(
        "Face recognition best match match_id=%s similarity=%.4f confidence=%.3f threshold=%.4f",
        match_ids[best_index],
        best_similarity,
        confidence,
        threshold,
    )

    if best_similarity >= threshold:
        return True, match_ids[best_index], confidence, None

    return False, None, confidence, "no match"
