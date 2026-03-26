import argparse
import os
import time

from face_capture import capture_face_jpeg
from face_uploader import post_face_image

FACE_SERVER_URL = os.getenv("FACE_SERVER_URL", "http://localhost:8000/face/verify")
FACE_ENROLL_URL = os.getenv("FACE_ENROLL_URL", "http://localhost:8000/face/enroll")
FACE_UPLOAD_URL = os.getenv("FACE_UPLOAD_URL", "http://localhost:8000/face/upload")
FACE_MODE = os.getenv("FACE_MODE", "upload").lower()
DEVICE_ID = os.getenv("DEVICE_ID", "raspi-01")
PERSON_ID = os.getenv("PERSON_ID")
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
DETECT_INTERVAL = float(os.getenv("DETECT_INTERVAL", "0.2"))
MIN_FACE_SIZE = int(os.getenv("MIN_FACE_SIZE", "80"))
TIMEOUT_SECONDS = float(os.getenv("CAPTURE_TIMEOUT_SECONDS", "5"))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Face capture and upload client")
    parser.add_argument("--mode", choices=["verify", "enroll", "upload"], default=FACE_MODE)
    parser.add_argument("--device-id", default=DEVICE_ID)
    parser.add_argument("--person-id", default=PERSON_ID)
    parser.add_argument("--verify-url", default=FACE_SERVER_URL)
    parser.add_argument("--enroll-url", default=FACE_ENROLL_URL)
    parser.add_argument("--upload-url", default=FACE_UPLOAD_URL)
    parser.add_argument("--camera-index", type=int, default=CAMERA_INDEX)
    parser.add_argument("--interval", type=float, default=DETECT_INTERVAL)
    parser.add_argument("--min-face-size", type=int, default=MIN_FACE_SIZE)
    parser.add_argument("--timeout", type=float, default=TIMEOUT_SECONDS)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    while True:
        try:
            image_bytes, bbox = capture_face_jpeg(
                camera_index=args.camera_index,
                min_size=args.min_face_size,
                timeout_seconds=args.timeout
            )
            if not image_bytes:
                print("No face detected.")
            else:
                if args.mode == "enroll":
                    if not args.person_id:
                        print("PERSON_ID is required for enroll mode")
                    else:
                        result = post_face_image(
                            image_bytes,
                            args.enroll_url,
                            args.device_id,
                            person_id=args.person_id
                        )
                        print("Enroll response: {}".format(result))
                elif args.mode == "upload":
                    result = post_face_image(image_bytes, args.upload_url, args.device_id)
                    print("Upload response: {}".format(result))
                else:
                    result = post_face_image(image_bytes, args.verify_url, args.device_id)
                    print("Verify response: {}".format(result))
        except Exception as exc:
            print("Face client error: {}".format(exc))

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
