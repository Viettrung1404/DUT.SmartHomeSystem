import time
from typing import Optional, Tuple

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from picamera import PiCamera
    from picamera.array import PiRGBArray
except ImportError:
    PiCamera = None
    PiRGBArray = None


def capture_face_jpeg(
    camera_index: int = 0,
    min_size: int = 80,
    scale_factor: float = 1.1,
    min_neighbors: int = 5,
    timeout_seconds: float = 5.0,
    jpeg_quality: int = 85
) -> Tuple[Optional[bytes], Optional[Tuple[int, int, int, int]]]:
    if cv2 is None:
        raise RuntimeError("OpenCV is not installed")

    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)

    if PiCamera is not None:
        camera = PiCamera()
        camera.resolution = (640, 480)
        camera.framerate = 24
        raw_capture = PiRGBArray(camera, size=(640, 480))
        time.sleep(0.1)

        try:
            deadline = time.monotonic() + timeout_seconds
            for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
                if time.monotonic() > deadline:
                    return None, None

                image = frame.array
                raw_capture.truncate(0)

                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=scale_factor,
                    minNeighbors=min_neighbors,
                    minSize=(min_size, min_size)
                )

                if len(faces) == 0:
                    continue

                x, y, w, h = max(faces, key=lambda box: box[2] * box[3])
                face_image = image[y:y + h, x:x + w]
                success, buffer = cv2.imencode(
                    ".jpg",
                    face_image,
                    [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
                )
                if success:
                    return buffer.tobytes(), (x, y, w, h)

            return None, None
        finally:
            camera.close()

    capture = cv2.VideoCapture(camera_index)
    if not capture.isOpened():
        raise RuntimeError("Unable to open camera index {}".format(camera_index))

    try:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            ok, frame = capture.read()
            if not ok:
                time.sleep(0.05)
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=scale_factor,
                minNeighbors=min_neighbors,
                minSize=(min_size, min_size)
            )

            if len(faces) == 0:
                continue

            x, y, w, h = max(faces, key=lambda box: box[2] * box[3])
            face_image = frame[y:y + h, x:x + w]
            success, buffer = cv2.imencode(
                ".jpg",
                face_image,
                [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
            )
            if success:
                return buffer.tobytes(), (x, y, w, h)

        return None, None
    finally:
        capture.release()
