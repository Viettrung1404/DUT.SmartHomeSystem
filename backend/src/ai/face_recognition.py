from __future__ import annotations

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


def is_recognition_available() -> bool:
    return cv2 is not None and np is not None and FaceAnalysis is not None


def _get_face_app() -> FaceAnalysis:
    global _face_app
    if _face_app is not None:
        return _face_app

    providers = [p.strip() for p in FACE_PROVIDER.split(",") if p.strip()]
    det_size_parts = [int(part) for part in FACE_DET_SIZE.split(",") if part.strip().isdigit()]
    det_size = (det_size_parts[0], det_size_parts[1]) if len(det_size_parts) == 2 else (640, 640)

    app = FaceAnalysis(name=FACE_MODEL_NAME, providers=providers)
    app.prepare(ctx_id=0, det_size=det_size)
    _face_app = app
    return app


def _load_image_bytes(image_bytes: bytes):
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    return cv2.imdecode(image_array, cv2.IMREAD_COLOR)


def _extract_embedding(image) -> np.ndarray | None:
    app = _get_face_app()
    faces = app.get(image)
    if not faces:
        return None
    return faces[0].embedding


def extract_embedding_from_bytes(image_bytes: bytes) -> np.ndarray | None:
    if not is_recognition_available():
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

    embedding = extract_embedding_from_bytes(image_bytes)
    if embedding is None:
        return False, "no face detected"

    embedding_path = _embedding_path_for_image(image_path)
    try:
        np.save(embedding_path, embedding)
    except Exception:
        return False, "failed to save embedding"
    return True, None


def _load_embedding_from_file(embedding_path: str) -> np.ndarray | None:
    try:
        return np.load(embedding_path)
    except Exception:
        return None


def _load_gallery_embeddings(gallery_dir: str) -> Tuple[List[str], List[np.ndarray]]:
    match_ids: List[str] = []
    embeddings: List[np.ndarray] = []
    if not os.path.isdir(gallery_dir):
        return match_ids, embeddings

    for root, _, files in os.walk(gallery_dir):
        for filename in files:
            if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            person_id = os.path.basename(root)
            file_path = os.path.join(root, filename)
            embedding_path = _embedding_path_for_image(file_path)
            try:
                embedding = None
                if os.path.exists(embedding_path):
                    embedding = _load_embedding_from_file(embedding_path)
                if embedding is None:
                    image = cv2.imread(file_path)
                    if image is None:
                        continue
                    embedding = _extract_embedding(image)
                    if embedding is not None:
                        np.save(embedding_path, embedding)
                if embedding is None:
                    continue
                match_ids.append(person_id)
                embeddings.append(embedding)
            except Exception:
                continue

    return match_ids, embeddings


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a_norm = a / (np.linalg.norm(a) + 1e-8)
    b_norm = b / (np.linalg.norm(b) + 1e-8)
    return float(np.dot(a_norm, b_norm))


def verify_face(image_bytes: bytes, gallery_dir: str, threshold: float) -> Tuple[bool, str | None, float | None, str | None]:
    if not is_recognition_available():
        return False, None, None, "insightface dependency not installed"

    match_ids, known_embeddings = _load_gallery_embeddings(gallery_dir)
    if not known_embeddings:
        return False, None, None, "no known faces enrolled"

    image = _load_image_bytes(image_bytes)
    if image is None:
        return False, None, None, "invalid image"

    probe_embedding = _extract_embedding(image)
    if probe_embedding is None:
        return False, None, None, "no face detected"

    similarities = [
        _cosine_similarity(probe_embedding, embedding)
        for embedding in known_embeddings
    ]
    best_index = int(np.argmax(similarities))
    best_similarity = float(similarities[best_index])
    confidence = round(max(0.0, min(1.0, best_similarity)), 3)

    if best_similarity >= threshold:
        return True, match_ids[best_index], confidence, None

    return False, None, confidence, "no match"
