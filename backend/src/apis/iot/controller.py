from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ...mqtt_client import publish_command, get_last_status, get_mqtt_debug
from ...config.env import DEFAULT_HOME_ID, DEFAULT_DEVICE_ID

router = APIRouter(
    prefix="/iot",
    tags=["IoT"],
)


class IoTCommandRequest(BaseModel):
    command: str
    home_id: Optional[str] = None
    device_id: Optional[str] = None


class IoTCommandResponse(BaseModel):
    ok: bool
    command: str


ALLOWED_COMMANDS = {
    "den khach on",
    "den khach off",
    "den khach toggle",
    "den ngu on",
    "den ngu off",
    "den ngu toggle",
    "quat khach on",
    "quat khach off",
    "quat khach weak",
    "quat khach strong",
    "quat khach toggle",
    "quat ngu on",
    "quat ngu off",
    "quat ngu weak",
    "quat ngu strong",
    "quat ngu toggle",
    "light on",
    "light off",
    "light toggle",
    "fan on",
    "fan off",
    "fan toggle",
    "buzzer on",
    "buzzer off",
    "buzzer toggle",
    "door open",
    "door close",
    "all on",
    "all off",
    "status",
}


def _segment(value: Optional[str], default: str, field: str) -> str:
    raw = (value if value is not None else default).strip()
    safe = "".join(ch for ch in raw if ch.isalnum() or ch in "-_")
    if not safe:
        raise HTTPException(status_code=400, detail="Invalid {}".format(field))
    return safe


@router.get("/status")
async def iot_status(
    home_id: Optional[str] = Query(default=None),
    device_id: Optional[str] = Query(default=None),
) -> Dict[str, Any]:
    hid = _segment(home_id, DEFAULT_HOME_ID, "home_id")
    did = _segment(device_id, DEFAULT_DEVICE_ID, "device_id")
    return get_last_status(hid, did)


@router.get("/debug")
async def iot_debug() -> Dict[str, Any]:
    return get_mqtt_debug()


@router.post("/command", response_model=IoTCommandResponse)
async def iot_command(payload: IoTCommandRequest) -> IoTCommandResponse:
    command = payload.command.strip().lower()
    if command in {"on", "off", "toggle"}:
        command = "den khach {}".format(command)

    command_aliases = {
        "light on": "den khach on",
        "light off": "den khach off",
        "light toggle": "den khach toggle",
        "fan on": "quat khach on",
        "fan off": "quat khach off",
        "fan toggle": "quat khach toggle",
        "quat khach yeu": "quat khach weak",
        "quat khach manh": "quat khach strong",
        "quat ngu yeu": "quat ngu weak",
        "quat ngu manh": "quat ngu strong",
    }
    command = command_aliases.get(command, command)

    if command not in ALLOWED_COMMANDS:
        raise HTTPException(status_code=400, detail="Invalid command")

    hid = _segment(payload.home_id, DEFAULT_HOME_ID, "home_id")
    did = _segment(payload.device_id, DEFAULT_DEVICE_ID, "device_id")
    publish_command(command, hid, did)
    return IoTCommandResponse(ok=True, command=command)
