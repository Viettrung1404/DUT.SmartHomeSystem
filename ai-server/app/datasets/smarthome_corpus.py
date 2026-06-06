from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path
import json
import re

from app.services.text_normalizer import normalize_text


CORE_INTENTS = [
    "control_device",
    "query_sensor",
    "query_device_status",
    "environmental_comfort",
    "greeting",
    "out_of_scope",
]

TARGET_CORPUS_SIZE = 4200
TRAIN_SPLIT = "train"
VALIDATION_SPLIT = "val"
TEST_SPLIT = "test"
SPLIT_RATIOS = ((TRAIN_SPLIT, 70), (VALIDATION_SPLIT, 15), (TEST_SPLIT, 15))


@dataclass(frozen=True)
class DeviceDefinition:
    name: str
    room: str
    device_type: str
    surfaces: tuple[str, ...]
    room_surfaces: tuple[str, ...]
    actions: tuple[str, ...]
    room_only_targets: tuple[str, ...] = ()


@dataclass(frozen=True)
class SensorDefinition:
    sensor_type: str
    room: str
    device_name: str
    surfaces: tuple[str, ...]
    room_surfaces: tuple[str, ...]
    status_surface: str


CONTROL_DEVICES: tuple[DeviceDefinition, ...] = (
    DeviceDefinition(
        name="living_light",
        room="living_room",
        device_type="light",
        surfaces=("đèn phòng khách", "đèn khách", "đèn pk", "đèn living room"),
        room_surfaces=("phòng khách", "pk", "living room", "phòng tiếp khách"),
        actions=("turn_on", "turn_off"),
        room_only_targets=("đèn ở phòng khách", "đèn tại pk"),
    ),
    DeviceDefinition(
        name="living_fan",
        room="living_room",
        device_type="fan",
        surfaces=("quạt phòng khách", "quạt khách", "quạt pk", "quạt living room"),
        room_surfaces=("phòng khách", "pk", "living room", "phòng tiếp khách"),
        actions=("turn_on", "turn_off", "set_speed"),
        room_only_targets=("quạt ở phòng khách", "quạt tại pk"),
    ),
    DeviceDefinition(
        name="bedroom_light",
        room="bedroom",
        device_type="light",
        surfaces=("đèn phòng ngủ", "đèn ngủ", "đèn pn", "đèn bedroom"),
        room_surfaces=("phòng ngủ", "pn", "bedroom", "phòng riêng"),
        actions=("turn_on", "turn_off"),
        room_only_targets=("đèn ở phòng ngủ", "đèn tại pn"),
    ),
    DeviceDefinition(
        name="bedroom_fan",
        room="bedroom",
        device_type="fan",
        surfaces=("quạt phòng ngủ", "quạt ngủ", "quạt pn", "quạt bedroom"),
        room_surfaces=("phòng ngủ", "pn", "bedroom", "phòng riêng"),
        actions=("turn_on", "turn_off", "set_speed"),
        room_only_targets=("quạt ở phòng ngủ", "quạt tại pn"),
    ),
    DeviceDefinition(
        name="bathroom_light",
        room="bathroom",
        device_type="light",
        surfaces=("đèn nhà vệ sinh", "đèn wc", "đèn phòng tắm", "đèn bathroom"),
        room_surfaces=("nhà vệ sinh", "wc", "phòng tắm", "bathroom"),
        actions=("turn_on", "turn_off"),
        room_only_targets=("đèn ở wc", "đèn tại nhà vệ sinh"),
    ),
    DeviceDefinition(
        name="main_door",
        room="main_door",
        device_type="door_servo",
        surfaces=("cửa chính", "cửa trước", "servo cửa chính", "khóa cửa chính"),
        room_surfaces=("cửa chính", "cửa trước", "main door"),
        actions=("open", "close", "lock", "unlock"),
    ),
    DeviceDefinition(
        name="roof_servo",
        room="roof_zone",
        device_type="roof_servo",
        surfaces=("trần servo", "mái che", "trần mái", "servo mái che"),
        room_surfaces=("khu mái", "sân thượng", "ngoài trời", "roof zone"),
        actions=("open", "close"),
    ),
)

SENSOR_DEFINITIONS: tuple[SensorDefinition, ...] = (
    SensorDefinition(
        sensor_type="temperature",
        room="living_room",
        device_name="dht11_sensor",
        surfaces=("nhiệt độ phòng khách", "nhiệt độ pk", "nhiệt độ living room"),
        room_surfaces=("phòng khách", "pk", "living room"),
        status_surface="DHT11",
    ),
    SensorDefinition(
        sensor_type="humidity",
        room="living_room",
        device_name="dht11_sensor",
        surfaces=("độ ẩm phòng khách", "độ ẩm pk", "độ ẩm living room"),
        room_surfaces=("phòng khách", "pk", "living room"),
        status_surface="DHT11",
    ),
    SensorDefinition(
        sensor_type="rain_detected",
        room="roof_zone",
        device_name="rain_sensor",
        surfaces=("cảm biến mưa", "trời mưa", "mưa ngoài trời", "mưa trên mái"),
        room_surfaces=("ngoài trời", "khu mái", "roof zone"),
        status_surface="cảm biến mưa",
    ),
    SensorDefinition(
        sensor_type="gas_detected",
        room="kitchen",
        device_name="gas_sensor",
        surfaces=("cảm biến gas", "gas bếp", "rò gas", "khí gas nhà bếp"),
        room_surfaces=("phòng bếp", "bếp", "kitchen", "nhà bếp"),
        status_surface="cảm biến gas",
    ),
    SensorDefinition(
        sensor_type="fire_detected",
        room="kitchen",
        device_name="fire_sensor",
        surfaces=("cảm biến cháy", "báo cháy", "khói bếp", "lửa bếp"),
        room_surfaces=("phòng bếp", "bếp", "kitchen", "nhà bếp"),
        status_surface="cảm biến cháy",
    ),
    SensorDefinition(
        sensor_type="occupancy",
        room="bathroom",
        device_name="bathroom_ultrasonic_sensor",
        surfaces=("có người trong nhà vệ sinh", "wc có người", "nhà vệ sinh có người", "phòng tắm có người"),
        room_surfaces=("nhà vệ sinh", "wc", "phòng tắm", "bathroom"),
        status_surface="cảm biến siêu âm",
    ),
)

ACTION_VARIANTS = {
    "turn_on": ("bật", "mở", "cho chạy", "kích hoạt"),
    "turn_off": ("tắt", "ngắt", "cho dừng", "vô hiệu hóa"),
    "open": ("mở", "kéo lên", "bật mở"),
    "close": ("đóng", "khép lại", "hạ xuống"),
    "lock": ("khóa", "khóa lại", "chốt"),
    "unlock": ("mở khóa", "bỏ khóa", "unlock"),
    "set_speed": ("chỉnh tốc độ", "đặt tốc độ", "đổi mức gió"),
}

SPEED_VALUES = (
    ("nhẹ", "low"),
    ("vừa", "medium"),
    ("mạnh", "high"),
)

POLITE_SUFFIXES = ("", " giúp tôi", " nhé", " đi", " ngay", " được không")
CONTROL_PREFIXES = ("", "làm ơn ", "trợ lý ơi ", "bạn ơi ")
STATUS_PREFIXES = ("", "kiểm tra ", "xem ", "cho tôi biết ")
QUERY_PREFIXES = ("", "kiểm tra ", "xem ", "cho tôi biết ")
GREETING_VARIANTS = (
    "xin chào",
    "chào bạn",
    "hello",
    "hi trợ lý",
    "alo trợ lý",
    "chào buổi tối",
    "hey trợ lý",
)
OOS_TEMPLATES = (
    "mở youtube cho tôi",
    "gọi điện cho mẹ",
    "đặt báo thức lúc 5 giờ sáng",
    "hôm nay giá vàng bao nhiêu",
    "viết email xin nghỉ phép",
    "đặt đồ ăn tối giúp tôi",
    "mở bản đồ tới trường",
    "đặt vé xe khách đi đà lạt",
    "cho tôi một câu chuyện cười",
    "tóm tắt tin tức hôm nay",
)
GREETING_PREFIXES = ("", "trợ lý ơi ", "hey ", "alo ")
GREETING_SUFFIXES = ("", " nhé", " nè", " ơi")
TARGET_INTENT_COUNTS = {
    "control_device": 2400,
    "query_sensor": 700,
    "query_device_status": 700,
    "environmental_comfort": 100,
    "greeting": 100,
    "out_of_scope": 200,
}
VARIANT_QUOTAS = {
    "standard": 0.7,
    "alias": 0.15,
    "asr_no_accent": 0.15,
}


def _slot(value: str, text: str) -> dict[str, str]:
    return {"value": value, "text": text}


def _hash_percent(value: str) -> int:
    digest = sha1(value.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 100


def _pick_split(group: str) -> str:
    marker = _hash_percent(group)
    threshold = 0
    for split_name, weight in SPLIT_RATIOS:
        threshold += weight
        if marker < threshold:
            return split_name
    return TEST_SPLIT


def _tokens(text: str) -> list[str]:
    return normalize_text(text).split()


def _find_span(tokens: Sequence[str], phrase_tokens: Sequence[str]) -> tuple[int, int] | None:
    if not phrase_tokens:
        return None
    last_start = len(tokens) - len(phrase_tokens)
    for start in range(last_start + 1):
        if list(tokens[start : start + len(phrase_tokens)]) == list(phrase_tokens):
            return start, start + len(phrase_tokens)
    return None


def _build_bio_tags(normalized_text: str, slots: dict[str, dict[str, str]]) -> tuple[list[str], list[str]]:
    tokens = normalized_text.split()
    tags = ["O"] * len(tokens)
    ranked_slots = sorted(
        (
            (slot_name, normalize_text(slot_payload.get("text", "")))
            for slot_name, slot_payload in slots.items()
            if slot_payload.get("text")
        ),
        key=lambda item: len(item[1].split()),
        reverse=True,
    )
    for slot_name, slot_text in ranked_slots:
        phrase_tokens = slot_text.split()
        span = _find_span(tokens, phrase_tokens)
        if span is None:
            continue
        start, end = span
        if any(tag != "O" for tag in tags[start:end]):
            continue
        tags[start] = f"B-{slot_name}"
        for idx in range(start + 1, end):
            tags[idx] = f"I-{slot_name}"
    return tokens, tags


def _sample_record(
    *,
    sample_id: str,
    text: str,
    intent: str,
    slots: dict[str, dict[str, str]] | None = None,
    source: str = "manual_seed",
    split_group: str,
    language_variant: str,
    notes: str,
) -> dict[str, object]:
    normalized_text = normalize_text(text)
    payload_slots = slots or {}
    tokens, slot_tags = _build_bio_tags(normalized_text, payload_slots)
    return {
        "id": sample_id,
        "text": text,
        "normalized_text": normalized_text,
        "intent": intent,
        "slots": payload_slots,
        "source": source,
        "split_group": split_group,
        "split": _pick_split(split_group),
        "language_variant": language_variant,
        "notes": notes,
        "tokens": tokens,
        "slot_tags": slot_tags,
    }


def _no_accent_variant(text: str) -> str:
    return normalize_text(text)


def _control_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    counter = 0
    control_templates = (
        "{prefix}{action} {target}{suffix}",
        "{prefix}{action} {target} lên{suffix}",
        "{prefix}{action} cho {target}{suffix}",
        "{prefix}{action} {target} ngay{suffix}",
        "{prefix}{action} giúp tôi {target}{suffix}",
    )
    room_templates = (
        "{prefix}{action} {device_type} ở {room}{suffix}",
        "{prefix}{action} {device_type} tại {room}{suffix}",
        "{prefix}{action} {device_type} bên {room}{suffix}",
    )
    device_type_text = {
        "light": "đèn",
        "fan": "quạt",
        "door_servo": "cửa",
        "roof_servo": "trần servo",
    }

    for device in CONTROL_DEVICES:
        for action in device.actions:
            for action_text in ACTION_VARIANTS[action]:
                for prefix in CONTROL_PREFIXES:
                    for suffix in POLITE_SUFFIXES:
                        family_tag = f"control::{device.name}::{action}::{normalize_text(action_text)}"
                        for template_idx, template in enumerate(control_templates):
                            for target in device.surfaces:
                                counter += 1
                                records.append(
                                    _sample_record(
                                        sample_id=f"control-{counter:05d}",
                                        text=template.format(
                                            prefix=prefix,
                                            action=action_text,
                                            target=target,
                                            suffix=suffix,
                                        ).strip(),
                                        intent="control_device",
                                        slots={
                                            "room": _slot(device.room, device.room_surfaces[0]),
                                            "device_type": _slot(device.device_type, device_type_text[device.device_type]),
                                            "device_name": _slot(device.name, target),
                                            "action": _slot(action, action_text),
                                        },
                                        split_group=f"{family_tag}::target::{template_idx}",
                                        language_variant="standard",
                                        notes="template_bootstrap_control",
                                    )
                                )
                                if template_idx == 0 and suffix == "" and prefix == "":
                                    counter += 1
                                    records.append(
                                        _sample_record(
                                            sample_id=f"control-{counter:05d}",
                                            text=_no_accent_variant(
                                                template.format(
                                                    prefix=prefix,
                                                    action=action_text,
                                                    target=target,
                                                    suffix=suffix,
                                                )
                                            ),
                                            intent="control_device",
                                            slots={
                                                "room": _slot(device.room, device.room_surfaces[0]),
                                                "device_type": _slot(device.device_type, device_type_text[device.device_type]),
                                                "device_name": _slot(device.name, target),
                                                "action": _slot(action, action_text),
                                            },
                                            split_group=f"{family_tag}::no_accent",
                                            language_variant="asr_no_accent",
                                            notes="template_bootstrap_control",
                                        )
                                    )
                        for room_target in device.room_only_targets:
                            for template_idx, template in enumerate(room_templates):
                                counter += 1
                                records.append(
                                    _sample_record(
                                        sample_id=f"control-{counter:05d}",
                                        text=template.format(
                                            prefix=prefix,
                                            action=action_text,
                                            device_type=device_type_text[device.device_type],
                                            room=room_target.replace("đèn ở ", "").replace("quạt ở ", ""),
                                            suffix=suffix,
                                        ).strip(),
                                        intent="control_device",
                                        slots={
                                            "room": _slot(device.room, device.room_surfaces[0]),
                                            "device_type": _slot(device.device_type, device_type_text[device.device_type]),
                                            "action": _slot(action, action_text),
                                        },
                                        split_group=f"{family_tag}::room_target::{template_idx}",
                                        language_variant="alias" if "pk" in room_target or "pn" in room_target else "standard",
                                        notes="template_bootstrap_control",
                                    )
                                )
                if action == "set_speed":
                    for speed_text, speed_value in SPEED_VALUES:
                        for target in device.surfaces:
                            counter += 1
                            records.append(
                                _sample_record(
                                    sample_id=f"control-{counter:05d}",
                                    text=f"chỉnh {target} mức {speed_text}",
                                    intent="control_device",
                                    slots={
                                        "room": _slot(device.room, device.room_surfaces[0]),
                                        "device_type": _slot(device.device_type, device_type_text[device.device_type]),
                                        "device_name": _slot(device.name, target),
                                        "action": _slot("set_speed", "chỉnh"),
                                        "value": _slot(speed_value, speed_text),
                                    },
                                    split_group=f"control::{device.name}::set_speed::{speed_value}",
                                    language_variant="standard",
                                    notes="template_bootstrap_control",
                                )
                            )
    return records


def _query_sensor_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    counter = 0
    sensor_templates = (
        "{prefix}{surface} {tail}",
        "{prefix}{tail} {surface}",
        "{prefix}{surface} hiện tại {tail}",
        "{prefix}{surface} bây giờ {tail}",
    )
    query_tails = ("bao nhiêu", "thế nào", "ra sao", "có ổn không")
    for sensor in SENSOR_DEFINITIONS:
        for prefix in QUERY_PREFIXES:
            for surface in sensor.surfaces:
                for tail in query_tails:
                    for template_idx, template in enumerate(sensor_templates):
                        counter += 1
                        records.append(
                            _sample_record(
                                sample_id=f"sensor-{counter:05d}",
                                text=template.format(prefix=prefix, surface=surface, tail=tail).strip(),
                                intent="query_sensor",
                                slots={
                                    "room": _slot(sensor.room, sensor.room_surfaces[0]),
                                    "sensor_type": _slot(sensor.sensor_type, surface.split()[0] if " " in surface else surface),
                                    "device_name": _slot(sensor.device_name, sensor.status_surface),
                                },
                                split_group=f"sensor::{sensor.sensor_type}::{normalize_text(surface)}::{template_idx}",
                                language_variant="alias" if any(alias in surface for alias in ("pk", "wc", "bếp")) else "standard",
                                notes="template_bootstrap_query_sensor",
                            )
                        )
                        if template_idx == 0 and prefix == "":
                            counter += 1
                            records.append(
                                _sample_record(
                                    sample_id=f"sensor-{counter:05d}",
                                    text=_no_accent_variant(template.format(prefix=prefix, surface=surface, tail=tail)),
                                    intent="query_sensor",
                                    slots={
                                        "room": _slot(sensor.room, sensor.room_surfaces[0]),
                                        "sensor_type": _slot(sensor.sensor_type, surface.split()[0] if " " in surface else surface),
                                        "device_name": _slot(sensor.device_name, sensor.status_surface),
                                    },
                                    split_group=f"sensor::{sensor.sensor_type}::{normalize_text(surface)}::no_accent",
                                    language_variant="asr_no_accent",
                                    notes="template_bootstrap_query_sensor",
                                )
                            )
    return records


def _status_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    counter = 0
    status_templates = (
        "{prefix}{target} đang {tail}",
        "{prefix}trạng thái {target} {tail}",
        "{prefix}{target} {tail} chưa",
        "{prefix}xem giúp tôi {target} {tail}",
    )
    status_tails_by_type = {
        "light": ("bật hay tắt", "còn sáng không", "đang chạy không"),
        "fan": ("bật hay tắt", "đang quay không", "ở mức nào"),
        "door_servo": ("mở hay đóng", "đã khóa chưa", "đang khóa không"),
        "roof_servo": ("mở hay đóng", "đang khép không", "đã đóng chưa"),
    }
    for device in CONTROL_DEVICES:
        for prefix in STATUS_PREFIXES:
            for target in device.surfaces:
                for tail in status_tails_by_type[device.device_type]:
                    for template_idx, template in enumerate(status_templates):
                        counter += 1
                        records.append(
                            _sample_record(
                                sample_id=f"status-{counter:05d}",
                                text=template.format(prefix=prefix, target=target, tail=tail).strip(),
                                intent="query_device_status",
                                slots={
                                    "room": _slot(device.room, device.room_surfaces[0]),
                                    "device_type": _slot(device.device_type, target.split()[0]),
                                    "device_name": _slot(device.name, target),
                                },
                                split_group=f"status::{device.name}::{normalize_text(tail)}::{template_idx}",
                                language_variant="standard",
                                notes="template_bootstrap_query_status",
                            )
                        )
    return records


def _comfort_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    counter = 0
    templates = (
        "{room} {phrase}",
        "{phrase} ở {room}",
        "hình như {room} {phrase}",
        "trong {room} đang {phrase}",
        "giúp tôi vì {room} {phrase}",
        "{room} mà {phrase}",
    )
    variants = (
        ("living_room", "phòng khách", "nóng quá", "cooling"),
        ("living_room", "pk", "ẩm quá", "humidity"),
        ("bedroom", "phòng ngủ", "bí quá", "cooling"),
        ("bedroom", "pn", "tối quá", "lighting"),
        ("bathroom", "nhà vệ sinh", "ẩm quá", "humidity"),
        ("bathroom", "wc", "tối quá", "lighting"),
    )
    prefixes = ("", "trợ lý ơi, ", "bạn ơi, ")
    suffixes = ("", " quá", " thật", " ghê")
    for room_value, room_surface, phrase, comfort_type in variants:
        for prefix in prefixes:
            for suffix in suffixes:
                spoken_phrase = phrase if suffix in phrase else f"{phrase}{suffix}".strip()
                for template_idx, template in enumerate(templates):
                    counter += 1
                    records.append(
                        _sample_record(
                            sample_id=f"comfort-{counter:05d}",
                            text=template.format(room=room_surface, phrase=spoken_phrase, prefix=prefix),
                            intent="environmental_comfort",
                            slots={
                                "room": _slot(room_value, room_surface),
                                "comparison": _slot(comfort_type, spoken_phrase),
                            },
                            split_group=f"comfort::{room_value}::{normalize_text(phrase)}::{template_idx}",
                            language_variant="alias" if room_surface in {"pk", "pn", "wc"} else "standard",
                            notes="template_bootstrap_comfort",
                        )
                    )
                    if template_idx == 0 and prefix == "" and suffix == "":
                        counter += 1
                        records.append(
                            _sample_record(
                                sample_id=f"comfort-{counter:05d}",
                                text=_no_accent_variant(template.format(room=room_surface, phrase=spoken_phrase, prefix=prefix)),
                                intent="environmental_comfort",
                                slots={
                                    "room": _slot(room_value, room_surface),
                                    "comparison": _slot(comfort_type, spoken_phrase),
                                },
                                split_group=f"comfort::{room_value}::{normalize_text(phrase)}::no_accent",
                                language_variant="asr_no_accent",
                                notes="template_bootstrap_comfort",
                            )
                        )
    return records


def _greeting_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    counter = 0
    for text in GREETING_VARIANTS:
        for prefix in GREETING_PREFIXES:
            for suffix in GREETING_SUFFIXES:
                counter += 1
                spoken = f"{prefix}{text}{suffix}".strip()
                records.append(
                    _sample_record(
                        sample_id=f"greeting-{counter:05d}",
                        text=spoken,
                        intent="greeting",
                        split_group=f"greeting::{normalize_text(text)}",
                        language_variant="standard",
                        notes="manual_seed_greeting",
                    )
                )
                counter += 1
                records.append(
                    _sample_record(
                        sample_id=f"greeting-{counter:05d}",
                        text=_no_accent_variant(spoken),
                        intent="greeting",
                        split_group=f"greeting::{normalize_text(text)}::no_accent",
                        language_variant="asr_no_accent",
                        notes="manual_seed_greeting",
                    )
                )
    return records


def _out_of_scope_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    counter = 0
    prefixes = ("", "làm ơn ", "giúp tôi ", "cho tôi ", "bạn có thể ")
    suffixes = ("", " được không", " nhé", " ngay")
    for text in OOS_TEMPLATES:
        for prefix in prefixes:
            for suffix in suffixes:
                spoken = f"{prefix}{text}{suffix}".strip()
                counter += 1
                records.append(
                    _sample_record(
                        sample_id=f"oos-{counter:05d}",
                        text=spoken,
                        intent="out_of_scope",
                        split_group=f"oos::{normalize_text(text)}",
                        language_variant="standard",
                        notes="curated_oos_negative",
                    )
                )
                counter += 1
                records.append(
                    _sample_record(
                        sample_id=f"oos-{counter:05d}",
                        text=_no_accent_variant(spoken),
                        intent="out_of_scope",
                        split_group=f"oos::{normalize_text(text)}::no_accent",
                        language_variant="asr_no_accent",
                        notes="curated_oos_negative",
                    )
                )
    return records


def _select_balanced_records(records: Sequence[dict[str, object]]) -> list[dict[str, object]]:
    by_intent: dict[str, list[dict[str, object]]] = {}
    for record in records:
        by_intent.setdefault(str(record["intent"]), []).append(record)
    selected: list[dict[str, object]] = []
    for intent, target_count in TARGET_INTENT_COUNTS.items():
        candidates = sorted(by_intent.get(intent, []), key=lambda item: str(item["id"]))
        if len(candidates) < target_count:
            raise ValueError(f"Not enough records for {intent}: {len(candidates)} < {target_count}")
        chosen_ids: set[str] = set()
        by_variant: dict[str, list[dict[str, object]]] = {}
        for candidate in candidates:
            by_variant.setdefault(str(candidate["language_variant"]), []).append(candidate)
        for variant_name, quota in VARIANT_QUOTAS.items():
            variant_candidates = sorted(by_variant.get(variant_name, []), key=lambda item: str(item["id"]))
            target_variant = min(len(variant_candidates), int(target_count * quota))
            for candidate in variant_candidates[:target_variant]:
                selected.append(candidate)
                chosen_ids.add(str(candidate["id"]))
        remaining = [candidate for candidate in candidates if str(candidate["id"]) not in chosen_ids]
        need = target_count - len(chosen_ids)
        selected.extend(remaining[:need])
    return sorted(selected, key=lambda item: (str(item["intent"]), str(item["id"])))


def build_bootstrap_corpus(target_size: int = TARGET_CORPUS_SIZE) -> list[dict[str, object]]:
    records = (
        _control_records()
        + _query_sensor_records()
        + _status_records()
        + _comfort_records()
        + _greeting_records()
        + _out_of_scope_records()
    )
    deduped: dict[tuple[str, str], dict[str, object]] = {}
    for record in records:
        key = (str(record["intent"]), str(record["text"]))
        deduped.setdefault(key, record)
    final_records = _select_balanced_records(list(deduped.values()))
    if len(final_records) != target_size:
        raise ValueError(f"Balanced corpus size mismatch: {len(final_records)} != {target_size}")
    return final_records


def split_records(records: Iterable[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    grouped = {TRAIN_SPLIT: [], VALIDATION_SPLIT: [], TEST_SPLIT: []}
    for record in records:
        grouped[str(record["split"])].append(record)
    return grouped


def corpus_summary(records: Sequence[dict[str, object]]) -> dict[str, object]:
    split_counts = Counter(str(record["split"]) for record in records)
    intent_counts = Counter(str(record["intent"]) for record in records)
    variant_counts = Counter(str(record["language_variant"]) for record in records)
    return {
        "rows": len(records),
        "intent_counts": dict(intent_counts),
        "split_counts": dict(split_counts),
        "variant_counts": dict(variant_counts),
        "core_intents": list(CORE_INTENTS),
    }


def build_restoration_lexicon(records: Sequence[dict[str, object]]) -> dict[str, str]:
    token_pattern = re.compile(r"[0-9A-Za-zÀ-ỹà-ỹđĐ_]+", re.UNICODE)
    counts: dict[str, Counter[str]] = {}
    for record in records:
        normalized_tokens = [str(token) for token in record.get("tokens", [])]
        surface_tokens = [token.lower() for token in token_pattern.findall(str(record.get("text", "")))]
        if len(surface_tokens) != len(normalized_tokens):
            continue
        for normalized_token, surface_token in zip(normalized_tokens, surface_tokens, strict=True):
            if normalize_text(surface_token) != normalized_token:
                continue
            counts.setdefault(normalized_token, Counter())[surface_token] += 1
    return {
        normalized_token: max(token_counts.items(), key=lambda item: (item[1], len(item[0]), item[0]))[0]
        for normalized_token, token_counts in counts.items()
    }


def write_jsonl(path: Path, records: Sequence[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]
