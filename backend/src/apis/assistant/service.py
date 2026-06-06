from __future__ import annotations

from typing import Any
from uuid import UUID

import httpx
from sqlalchemy.orm import Session

from src.apis.devices import models as device_models
from src.apis.devices import service as devices_service
from src.config.env import AI_ASSISTANT_ROUTE, AI_SERVER_BASE_URL
from src.entities.models import Home, HomeUser, Room
from src.exceptions import DeviceOfflineError, ForbiddenError


SAFE_AUTORUN_ACTIONS = {"turn_on", "turn_off", "open", "close", "lock", "unlock"}
SAFE_AUTORUN_INTENTS = {"control_device", "environmental_comfort"}
MIN_AUTORUN_CONFIDENCE = 0.85


class AssistantProxyError(RuntimeError):
    """Raised when backend cannot reach the AI server."""


def resolve_home_for_user(db: Session, user_id: UUID, home_id: str | None) -> Home:
    query = (
        db.query(Home)
        .join(HomeUser, HomeUser.home_id == Home.id)
        .filter(HomeUser.user_id == user_id)
        .order_by(Home.created_at.asc())
    )
    if home_id:
        try:
            requested_home_id = UUID(home_id)
        except ValueError as exc:
            raise ForbiddenError("Home id khong hop le") from exc
        home = query.filter(Home.id == requested_home_id).first()
    else:
        home = query.first()

    if not home:
        raise ForbiddenError("Ban khong co nha hop le de su dung tro ly")
    return home


def _room_aliases(name: str) -> list[str]:
    normalized = name.strip().lower()
    aliases: list[str] = []
    if "khach" in normalized:
        aliases.extend(["pk", "living room"])
    if "ngu" in normalized:
        aliases.extend(["pn", "bedroom"])
    if "bep" in normalized:
        aliases.extend(["kitchen", "nha bep"])
    if "ve sinh" in normalized or "tam" in normalized:
        aliases.extend(["wc", "bathroom"])
    return aliases


def _device_aliases(device_name: str, room_name: str) -> list[str]:
    lowered_name = device_name.strip().lower()
    lowered_room = room_name.strip().lower()
    aliases: list[str] = []
    if "den" in lowered_name and "khach" in lowered_room:
        aliases.append("den khach")
    if "quat" in lowered_name and "khach" in lowered_room:
        aliases.append("quat khach")
    if "den" in lowered_name and "ngu" in lowered_room:
        aliases.append("den ngu")
    if "quat" in lowered_name and "ngu" in lowered_room:
        aliases.append("quat ngu")
    if "den" in lowered_name and ("ve sinh" in lowered_room or "tam" in lowered_room):
        aliases.append("den wc")
    return aliases


def build_home_context(db: Session, home: Home, user_id: UUID) -> dict[str, Any]:
    rooms = (
        db.query(Room)
        .filter(Room.home_id == home.id)
        .order_by(Room.created_at.asc())
        .all()
    )

    room_payload = [
        {
            "id": str(room.id),
            "name": room.name,
            "aliases": _room_aliases(room.name),
        }
        for room in rooms
    ]

    device_payload: list[dict[str, Any]] = []
    for room in rooms:
        devices = devices_service.get_devices_by_room(db, room.id, user_id)
        for device in devices:
            dto = devices_service.to_response(device)
            device_payload.append(
                {
                    "id": dto.id,
                    "room_id": dto.room_id,
                    "name": dto.name,
                    "type": dto.type,
                    "aliases": _device_aliases(dto.name, room.name),
                    "metadata": dto.metadata or {},
                    "status": dto.status,
                    "online_status": dto.online_status,
                }
            )

    return {"rooms": room_payload, "devices": device_payload, "current_state_notes": []}


async def call_ai_assistant(message: str, home_context: dict[str, Any]) -> dict[str, Any]:
    url = f"{AI_SERVER_BASE_URL}{AI_ASSISTANT_ROUTE}"
    payload = {"message": message, "home_context": home_context}
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, json=payload)
    except httpx.HTTPError as exc:
        raise AssistantProxyError("Khong the ket noi toi AI server") from exc

    if response.status_code >= 500:
        raise AssistantProxyError("AI server dang khong san sang")
    if response.status_code >= 400:
        detail = response.text.strip() or "AI server tra ve loi"
        raise AssistantProxyError(detail)
    return response.json()


def should_autorun(ai_payload: dict[str, Any], execute_if_confident: bool) -> tuple[bool, str | None]:
    if not execute_if_confident:
        return False, "Auto-run bi tat o request"

    nlu = ai_payload.get("nlu") or {}
    action_draft = ai_payload.get("action_draft") or {}
    if nlu.get("intent") not in SAFE_AUTORUN_INTENTS:
        return False, "Intent khong nam trong tap auto-run"
    if bool(nlu.get("out_of_scope")):
        return False, "Yeu cau nam ngoai pham vi tro ly"
    if list(nlu.get("missing_slots") or []):
        return False, "Can lam ro them thiet bi hoac phong"
    if float(nlu.get("confidence") or 0.0) < MIN_AUTORUN_CONFIDENCE:
        return False, "Confidence chua du cao de auto-run"
    if not action_draft.get("device_id"):
        return False, "Action draft chua resolve duoc device_id"
    if action_draft.get("action") not in SAFE_AUTORUN_ACTIONS:
        return False, "Action chua duoc cho phep auto-run"
    return True, None


def execute_action_draft(db: Session, user_id: UUID, ai_payload: dict[str, Any]) -> dict[str, Any]:
    action_draft = ai_payload.get("action_draft") or {}
    device_id = action_draft.get("device_id")
    action = action_draft.get("action")
    value = action_draft.get("value")
    if not device_id or not action:
        return {"status": "skipped", "reason": "Action draft khong du thong tin"}

    command_request = device_models.DeviceCommandRequest(command=str(action), value=value)
    try:
        devices_service.send_command(db, UUID(device_id), user_id, command_request)
    except DeviceOfflineError:
        return {
            "status": "failed",
            "device_id": str(device_id),
            "command": str(action),
            "value": value,
            "reason": "Thiet bi dang offline",
        }
    except ForbiddenError as exc:
        return {
            "status": "failed",
            "device_id": str(device_id),
            "command": str(action),
            "value": value,
            "reason": str(exc),
        }
    except Exception as exc:
        return {
            "status": "failed",
            "device_id": str(device_id),
            "command": str(action),
            "value": value,
            "reason": str(exc),
        }

    return {
        "status": "executed",
        "device_id": str(device_id),
        "command": str(action),
        "value": value,
        "reason": None,
    }
