import asyncio
import json
import os
import sys
from typing import Any, Dict

try:
    import websockets
except ImportError:
    print("Missing dependency: websockets. Install with: pip install websockets")
    sys.exit(1)

WS_BASE_URL = os.getenv("WS_BASE_URL", "ws://127.0.0.1:8000")
HOME_ID = "72e41416-0821-4a39-92f3-0903c534ca16"
TOKEN = os.getenv("ACCESS_TOKEN") or os.getenv("WS_TOKEN") or ""
DEVICE_ID = os.getenv("DEVICE_ID") or ""


def _match_device(message: Dict[str, Any]) -> bool:
    if not DEVICE_ID:
        return True
    return str(message.get("device_id", "")) == DEVICE_ID


async def listen() -> None:
    if not HOME_ID:
        print("HOME_ID is required")
        return

    token_param = f"?token={TOKEN}" if TOKEN else ""
    ws_url = f"{WS_BASE_URL.rstrip('/')}/ws/home/{HOME_ID}{token_param}"
    print(f"[WS] Connecting to {ws_url}")

    async with websockets.connect(ws_url) as websocket:
        print("[WS] Connected")
        while True:
            raw = await websocket.recv()
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                print(f"[WS] Raw: {raw}")
                continue

            if not _match_device(message):
                continue

            pretty = json.dumps(message, ensure_ascii=False, indent=2)
            print(f"[WS] {pretty}")


if __name__ == "__main__":
    try:
        asyncio.run(listen())
    except KeyboardInterrupt:
        pass
