import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class IntentResult:
    intent: str
    device_hint: str | None = None
    time_range: str | None = None
    needs_memory: bool = False


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", text).strip()


def classify_intent(message: str) -> IntentResult:
    normalized = _normalize(message)
    needs_memory = any(
        phrase in normalized
        for phrase in ["the thi", "the tuan", "con ", "thiet bi do", "tai sao lai vay", "co nghiem trong"]
    )

    if any(word in normalized for word in ["quen tat", "hay bi quen", "forgot off"]):
        intent = "FORGOT_OFF_QUERY"
    elif any(word in normalized for word in ["bat thuong", "canh bao", "nguy hiem", "bao dong", "an ninh"]):
        intent = "GUARDIAN_EVENT_QUERY"
    elif any(word in normalized for word in ["tai sao", "vi sao", "goi y", "de xuat"]):
        intent = "SUGGESTION_EXPLAIN"
    elif any(word in normalized for word in ["trang thai", "dang bat", "dang tat", "online", "offline"]):
        intent = "DEVICE_STATUS_QUERY"
    elif any(word in normalized for word in ["bao lau", "may lan", "lich su", "chay nhieu", "su dung"]):
        intent = "DEVICE_HISTORY"
    elif _looks_like_direct_command(normalized):
        intent = "DEVICE_COMMAND"
    elif needs_memory:
        intent = "FOLLOW_UP"
    else:
        intent = "GENERAL_SMART_HOME_QUERY"

    return IntentResult(
        intent=intent,
        device_hint=_extract_device_hint(normalized),
        time_range=_extract_time_range(normalized),
        needs_memory=needs_memory,
    )


def _looks_like_direct_command(normalized: str) -> bool:
    if any(phrase in normalized for phrase in ["tai sao", "vi sao", "goi y", "quen tat", "bat thuong", "canh bao"]):
        return False
    words = set(re.sub(r"[^\w\s]", " ", normalized).split())
    return bool({"tat", "bat", "off", "on", "khoa", "lock", "unlock", "mo", "dong", "open", "close"} & words)


def _extract_time_range(normalized: str) -> str | None:
    if "toi qua" in normalized or "dem qua" in normalized:
        return "last_night"
    if "hom qua" in normalized:
        return "yesterday"
    if "tuan nay" in normalized:
        return "this_week"
    if "tuan truoc" in normalized:
        return "last_week"
    if "hom nay" in normalized:
        return "today"
    return None


def _extract_device_hint(normalized: str) -> str | None:
    candidates = [
        "den bep",
        "den phong khach",
        "dieu hoa phong ngu",
        "dieu hoa",
        "may lanh",
        "cua chinh",
        "den",
        "quat",
        "camera",
        "khoa",
    ]
    for candidate in candidates:
        if candidate in normalized:
            return candidate
    return None
