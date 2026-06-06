from dataclasses import dataclass

from app.agent.intent_router import _normalize


@dataclass(frozen=True)
class DeviceCommand:
    action: str
    device_hint: str | None
    device_type_hint: str | None = None


def parse_device_command(message: str) -> DeviceCommand | None:
    normalized = _normalize(message)
    words = set(normalized.split())

    action: str | None = None
    if {"tat", "off"} & words or "turn off" in normalized:
        action = "turn_off"
    elif {"bat", "on"} & words or "turn on" in normalized:
        action = "turn_on"
    elif {"khoa", "lock"} & words:
        action = "lock"
    elif "mo khoa" in normalized or "unlock" in normalized:
        action = "unlock"
    elif {"mo", "open"} & words:
        action = "open"
    elif {"dong", "close"} & words:
        action = "close"

    if not action:
        return None

    device_words = [
        "den bep",
        "den phong ngu",
        "den phong khach",
        "den tran phong khach",
        "dieu hoa phong ngu",
        "dieu hoa phong khach",
        "dieu hoa",
        "may lanh",
        "quat phong ngu",
        "quat phong khach",
        "quat",
        "rem",
        "cua garage",
        "cua chinh",
        "khoa cua",
        "garage door",
        "smart tv backlight",
        "smart light philips",
        "smart ac daikin",
    ]
    device_hint = next((candidate for candidate in device_words if candidate in normalized), None)
    if not device_hint:
        for generic in ["den", "light", "ac", "dieu hoa", "quat", "fan", "lock", "khoa", "cua"]:
            if generic in normalized:
                device_hint = generic
                break

    return DeviceCommand(action=action, device_hint=device_hint, device_type_hint=_infer_device_type(normalized, device_hint))


def _infer_device_type(normalized: str, device_hint: str | None) -> str | None:
    source = f"{normalized} {device_hint or ''}"
    if any(token in source for token in ["dieu hoa", "may lanh", " ac ", "smart ac"]):
        return "ac"
    if any(token in source for token in ["den", "light"]):
        return "light"
    if any(token in source for token in ["quat", "fan"]):
        return "fan"
    if any(token in source for token in ["khoa", "cua", "lock", "door"]):
        return "lock"
    return None
