import base64
from typing import Any, Dict, Optional

import requests


def post_face_image(
    image_bytes: bytes,
    url: str,
    device_id: str,
    person_id: Optional[str] = None,
    timeout_seconds: float = 10.0
) -> Dict[str, Any]:
    image_b64 = base64.b64encode(image_bytes).decode("ascii")
    payload = {
        "device_id": device_id,
        "image_base64": image_b64
    }
    if person_id:
        payload["person_id"] = person_id

    response = requests.post(url, json=payload, timeout=timeout_seconds)
    response.raise_for_status()
    return response.json()
