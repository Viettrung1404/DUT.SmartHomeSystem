from dataclasses import dataclass

from app.agent.intent_router import _normalize


@dataclass(frozen=True)
class DeviceCommand:
    action: str
    device_hint: str | None
    device_type_hint: str | None = None
    target_all: bool = False
    room_hint: str | None = None
    exclude_room_hint: str | None = None
    target_count: int | None = None


QUESTION_OR_ANALYTIC_PHRASES = [
    "tai sao",
    "vi sao",
    "goi y",
    "de xuat",
    "quen tat",
    "bat thuong",
    "canh bao",
    "hoat dong",
    "lau nhat",
    "thiet bi nao",
    "bao lau",
    "may lan",
    "lich su",
    "chay nhieu",
    "su dung",
]


DEVICE_CANDIDATES = [
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


GENERIC_DEVICE_CANDIDATES = ["den", "light", "ac", "dieu hoa", "quat", "fan", "lock", "khoa", "cua"]
COMMAND_CONNECTORS = [" va ", " and ", ",", ";"]
ALL_TARGET_PHRASES = ["tat ca", "toan bo", "het"]
ROOM_CANDIDATES = [
    "phong ngu chinh",
    "phong ngu con",
    "phong ngu",
    "phong khach",
    "nha tam",
    "bep",
    "garage",
    "living room",
    "master bedroom",
    "kitchen",
]


def parse_device_command(message: str) -> DeviceCommand | None:
    commands = parse_device_commands(message)
    return commands[0] if commands else None


def parse_device_commands(message: str) -> list[DeviceCommand]:
    normalized = _normalize(message)
    if any(phrase in normalized for phrase in QUESTION_OR_ANALYTIC_PHRASES):
        return []

    segments = _split_command_segments(normalized)
    commands: list[DeviceCommand] = []
    previous_command: DeviceCommand | None = None
    for segment in segments:
        command = _parse_normalized_device_command(segment)
        if command is None and previous_command is not None:
            command = _parse_inherited_segment(segment, previous_command)
        if command is None:
            continue
        commands.append(command)
        previous_command = command
    return commands


def _split_command_segments(normalized: str) -> list[str]:
    segments = [normalized]
    for connector in COMMAND_CONNECTORS:
        next_segments: list[str] = []
        for segment in segments:
            next_segments.extend(part.strip() for part in segment.split(connector) if part.strip())
        segments = next_segments
    return segments or [normalized]


def _parse_normalized_device_command(normalized: str) -> DeviceCommand | None:
    if any(phrase in normalized for phrase in QUESTION_OR_ANALYTIC_PHRASES):
        return None

    words = set(normalized.split())

    action: str | None = None
    if {"bat", "on"} & words or "turn on" in normalized:
        action = "turn_on"
    elif {"tat", "off"} & words or "turn off" in normalized:
        action = "turn_off"
    elif {"khoa", "lock"} & words:
        action = "lock"
    elif "mo khoa" in normalized or "unlock" in normalized:
        action = "unlock"
    elif {"mo", "open"} & words:
        action = "open"
    elif "close" in words or normalized.startswith("dong ") or " dong cua" in f" {normalized}":
        action = "close"

    if not action:
        return None

    device_hint = next((candidate for candidate in DEVICE_CANDIDATES if candidate in normalized), None)
    if not device_hint:
        device_hint = next((candidate for candidate in GENERIC_DEVICE_CANDIDATES if _contains_generic_candidate(candidate, words, normalized)), None)

    return DeviceCommand(
        action=action,
        device_hint=device_hint,
        device_type_hint=_infer_device_type(normalized, device_hint),
        target_all=_is_all_target(normalized),
        room_hint=None if _extract_exclude_room_hint(normalized) else _extract_room_hint(normalized),
        exclude_room_hint=_extract_exclude_room_hint(normalized),
        target_count=_extract_target_count(words),
    )


def _parse_inherited_segment(segment: str, previous_command: DeviceCommand) -> DeviceCommand | None:
    if previous_command.device_type_hint == "light":
        prefix = "den"
    elif previous_command.device_type_hint == "fan":
        prefix = "quat"
    elif previous_command.device_type_hint == "ac":
        prefix = "dieu hoa"
    elif previous_command.device_type_hint == "lock":
        prefix = "khoa cua"
    else:
        return None

    inherited_text = f"{_action_text(previous_command.action)} {prefix} {segment}".strip()
    return _parse_normalized_device_command(inherited_text)


def _is_all_target(normalized: str) -> bool:
    return any(phrase in normalized for phrase in ALL_TARGET_PHRASES) or ("ngoai" in normalized and "thiet bi" in normalized)


def _contains_generic_candidate(candidate: str, words: set[str], normalized: str) -> bool:
    if " " in candidate:
        return candidate in normalized
    return candidate in words


def _extract_room_hint(normalized: str) -> str | None:
    return next((candidate for candidate in ROOM_CANDIDATES if candidate in normalized), None)


def _extract_exclude_room_hint(normalized: str) -> str | None:
    if "ngoai" not in normalized:
        return None
    after_exclusion = normalized.split("ngoai", 1)[1]
    return _extract_room_hint(after_exclusion)


def _extract_target_count(words: set[str]) -> int | None:
    for word in words:
        if word.isdigit():
            value = int(word)
            return value if value > 0 else None
    return None


def _action_text(action: str) -> str:
    return {
        "turn_on": "bat",
        "turn_off": "tat",
        "lock": "khoa",
        "unlock": "mo khoa",
        "open": "mo",
        "close": "dong",
    }.get(action, action)


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
