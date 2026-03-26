import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = SCRIPT_DIR.parent
sys.path.append(str(BACKEND_ROOT))

from src.config.env import FACE_GALLERY_DIR
from src.ai.face_recognition import save_embedding_for_image, is_recognition_available


def iter_image_files(root: Path):
    for path in root.rglob("*"):
        if path.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            yield path


def main() -> int:
    gallery_root = Path(FACE_GALLERY_DIR)
    if not gallery_root.exists():
        print("Gallery dir not found: {}".format(gallery_root))
        return 1

    if not is_recognition_available():
        print("InsightFace not installed. Install requirements-face.txt")
        return 1

    total = 0
    success = 0
    for image_path in iter_image_files(gallery_root):
        total += 1
        image_bytes = image_path.read_bytes()
        ok, reason = save_embedding_for_image(image_bytes, str(image_path))
        if ok:
            success += 1
        else:
            print("Skip {}: {}".format(image_path, reason))

    print("Processed {} images, embeddings saved for {}.".format(total, success))
    return 0


if __name__ == "__main__":
    sys.exit(main())
