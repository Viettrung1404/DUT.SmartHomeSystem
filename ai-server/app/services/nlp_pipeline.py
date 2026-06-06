from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

import numpy as np

from app.core.capabilities import (
    ACTION_ALIASES,
    DEVICE_TYPE_ALIASES,
    ROOM_ALIASES,
    SENSOR_TYPE_ALIASES,
)
from app.core.settings import get_settings
from app.schemas.common import ActionDraft, CandidateIntent, DeviceContext, HomeContext, RoomContext
from app.schemas.nlp import ExtractedEntities, ParseResponse
from app.services.diacritic_restorer import VietnameseDiacriticRestorer
from app.services.nlp_training import ensure_nlp_bundle
from app.services.phobert_slot_model import PhoBERTSlotModel
from app.services.text_normalizer import normalize_text


@dataclass
class GroundingResult:
    room: RoomContext | None
    device: DeviceContext | None
    evidence: list[str]


class NLUPipeline:
    def __init__(self) -> None:
        self.bundle = ensure_nlp_bundle()
        self.restorer = VietnameseDiacriticRestorer()
        self.slot_model = PhoBERTSlotModel()

    def parse(self, text: str, context: HomeContext | None = None) -> ParseResponse:
        normalized = normalize_text(text)
        restored_text = text
        restoration_applied = False
        if self.restorer.is_likely_unaccented(text):
            candidate = self.restorer.restore_text(text)
            if candidate.strip():
                restored_text = candidate
                restoration_applied = normalize_text(candidate) == normalized
        rule_intent, rule_evidence = self._rule_intent(normalized)
        entities = self._extract_entities(normalized, context)
        slot_evidence: list[str] = []
        if self.slot_model.available:
            slot_result = self.slot_model.extract_entities(restored_text)
            entities = self._merge_entities(slot_result.entities, entities)
            slot_evidence.extend(slot_result.evidence)
        else:
            slot_evidence.append("slot_model=fallback_rule_lexicon")
        grounding = self._ground_entities(entities, context)
        model_probs = self.bundle.pipeline.predict_proba([normalized])[0]
        classes = list(self.bundle.pipeline.classes_)
        ranked = sorted(
            zip(classes, model_probs),
            key=lambda item: item[1],
            reverse=True,
        )
        model_intent, model_score = ranked[0]
        candidate_intents = [
            CandidateIntent(name=name, score=round(float(score), 4), source="classifier")
            for name, score in ranked[:3]
        ]

        final_intent = model_intent
        explanation = [f"classifier={model_intent}:{model_score:.2f}"]
        if rule_intent:
            explanation.append(f"rule={rule_intent}")
            high_precision_rules = {
                "greeting",
                "query_sensor",
                "query_device_status",
            }
            if (
                rule_intent == model_intent
                or model_score < 0.58
                or rule_intent in high_precision_rules
            ):
                final_intent = rule_intent

        missing_slots = self._detect_missing_slots(final_intent, entities, grounding, context)
        action_draft = self._build_action_draft(final_intent, entities, grounding)
        confidence = self._combine_confidence(
            model_score=model_score,
            rule_match=rule_intent is not None,
            intent_agreement=rule_intent == model_intent if rule_intent else False,
            missing_slots=missing_slots,
        )

        out_of_scope = final_intent == "out_of_scope"
        if confidence < get_settings().nlp_oos_threshold and not rule_intent:
            out_of_scope = True
            final_intent = "out_of_scope"
            action_draft = None
            explanation.append("low_confidence_routed_to_oos")
        elif final_intent not in {"greeting", "out_of_scope"} and confidence < get_settings().nlp_confidence_threshold:
            explanation.append("needs_confirmation_low_confidence")

        explanation.append("intent_model=baseline_tfidf_lr")
        if restoration_applied:
            explanation.append(f"restored_text={restored_text}")
        explanation.extend(slot_evidence)
        if rule_evidence:
            explanation.extend(rule_evidence)
        if grounding.evidence:
            explanation.extend(grounding.evidence)

        if grounding.room is not None:
            entities.room_id = grounding.room.id
            entities.room_name = grounding.room.name
        if grounding.device is not None:
            entities.device_id = grounding.device.id
            entities.device_name = grounding.device.name
            entities.device_type = grounding.device.type.lower()

        return ParseResponse(
            intent=final_intent,
            confidence=round(confidence, 4),
            normalized_text=normalized,
            entities=entities,
            candidate_intents=candidate_intents,
            missing_slots=missing_slots,
            out_of_scope=out_of_scope,
            explanation=explanation,
            action_draft=action_draft,
        )

    def _merge_entities(self, primary: ExtractedEntities, fallback: ExtractedEntities) -> ExtractedEntities:
        merged = fallback.model_copy(deep=True)
        for field_name in ExtractedEntities.model_fields:
            primary_value = getattr(primary, field_name)
            if primary_value not in (None, "", []):
                setattr(merged, field_name, primary_value)
        return merged

    def _combine_confidence(
        self,
        *,
        model_score: float,
        rule_match: bool,
        intent_agreement: bool,
        missing_slots: list[str],
    ) -> float:
        confidence = float(model_score)
        if rule_match:
            confidence += 0.12
        if intent_agreement:
            confidence += 0.08
        confidence -= 0.12 * len(missing_slots)
        return max(0.05, min(0.99, confidence))

    def _rule_intent(self, normalized: str) -> tuple[str | None, list[str]]:
        evidence: list[str] = []
        if re.search(r"\b(xin chao|chao|hello|hi|alo)\b", normalized):
            return "greeting", ["matched_greeting_pattern"]
        if any(alias in normalized for aliases in SENSOR_TYPE_ALIASES.values() for alias in aliases) and any(
            token in normalized for token in ["bao nhieu", "kiem tra", "co", "hien tai", "dang", "muc"]
        ):
            return "query_sensor", ["matched_sensor_query_pattern"]
        if any(token in normalized for token in ["trang thai", "dang bat", "dang tat", "dang mo", "da khoa"]):
            return "query_device_status", ["matched_status_query_pattern"]
        if any(token in normalized for token in ["nong qua", "am qua", "toi qua", "lanh qua", "kho chiu"]):
            return "environmental_comfort", ["matched_comfort_pattern"]
        if any(alias in normalized for aliases in ACTION_ALIASES.values() for alias in aliases):
            return "control_device", ["matched_control_pattern"]
        return None, evidence

    def _extract_entities(self, normalized: str, context: HomeContext | None) -> ExtractedEntities:
        entities = ExtractedEntities()
        for room_name, aliases in ROOM_ALIASES.items():
            if any(alias in normalized for alias in aliases):
                entities.room_name = room_name
                break
        for device_type, aliases in DEVICE_TYPE_ALIASES.items():
            if any(alias in normalized for alias in aliases):
                entities.device_type = device_type
                break
        for sensor_type, aliases in SENSOR_TYPE_ALIASES.items():
            if any(alias in normalized for alias in aliases):
                entities.sensor_type = sensor_type
                break

        if any(token in normalized for token in ["nong", "hot"]):
            entities.comfort_type = "cooling"
        elif any(token in normalized for token in ["lanh", "cold"]):
            entities.comfort_type = "warming"
        elif "am" in normalized:
            entities.comfort_type = "humidity"
        elif "toi" in normalized:
            entities.comfort_type = "lighting"

        action_patterns = [
            ("unlock", [r"\bmo khoa\b", r"\bunlock\b"]),
            ("lock", [r"\bkhoa\b", r"\block\b"]),
            ("set_speed", [r"\btoc do\b", r"\bset speed\b"]),
            ("set_temperature", [r"\b\d+\s*do c\b", r"\bset temperature\b"]),
            ("turn_off", [r"\btat\b", r"\bswitch off\b"]),
            ("turn_on", [r"\bbat\b", r"\bswitch on\b"]),
            ("close", [r"\bdong\b"]),
            ("open", [r"\bmo\b"]),
        ]
        for action, patterns in action_patterns:
            if any(re.search(pattern, normalized) for pattern in patterns):
                entities.action = action
                break

        if entities.device_type in {"door_servo", "roof_servo"}:
            if "mo " in f"{normalized} ":
                entities.action = "open"
            elif "dong " in f"{normalized} ":
                entities.action = "close"
        if entities.device_type == "door_servo" and "mo khoa" in normalized:
            entities.action = "unlock"
        elif entities.device_type == "door_servo" and "khoa" in normalized:
            entities.action = "lock"

        numeric_match = re.search(r"\b(\d+(?:\.\d+)?)\b", normalized)
        if numeric_match:
            value = float(numeric_match.group(1))
            entities.value = int(value) if value.is_integer() else value

        if "manh" in normalized or "strong" in normalized:
            entities.value = "strong"
            if entities.action is None:
                entities.action = "set_speed"
        elif "yeu" in normalized or "weak" in normalized:
            entities.value = "weak"
            if entities.action is None:
                entities.action = "set_speed"

        if context:
            for device in context.devices:
                device_name = normalize_text(device.name)
                if device_name and device_name in normalized:
                    entities.device_name = device.name
                    break
        return entities

    def _ground_entities(self, entities: ExtractedEntities, context: HomeContext | None) -> GroundingResult:
        if context is None:
            return GroundingResult(room=None, device=None, evidence=[])
        evidence: list[str] = []
        room_match: RoomContext | None = None
        device_match: DeviceContext | None = None

        if entities.room_name:
            for room in context.rooms:
                if self._canonical_room_name(room) == entities.room_name:
                    room_match = room
                    evidence.append(f"grounded_room={room.name}")
                    break

        candidate_devices = context.devices
        if room_match is not None:
            candidate_devices = [device for device in candidate_devices if device.room_id == room_match.id]

        if entities.device_name:
            for device in candidate_devices:
                names = [normalize_text(device.name), *(normalize_text(alias) for alias in device.aliases)]
                if normalize_text(entities.device_name) in names:
                    device_match = device
                    evidence.append(f"grounded_device_name={device.name}")
                    break

        if device_match is None and entities.device_type:
            typed_candidates = [
                device
                for device in candidate_devices
                if normalize_text(device.type) == normalize_text(entities.device_type)
            ]
            if len(typed_candidates) == 1:
                device_match = typed_candidates[0]
                evidence.append(f"grounded_device_type={device_match.type}:{device_match.name}")
            elif len(typed_candidates) > 1:
                evidence.append(f"ambiguous_device_type_candidates={len(typed_candidates)}")

        if device_match is not None and room_match is None and device_match.room_id:
            for room in context.rooms:
                if room.id == device_match.room_id:
                    room_match = room
                    evidence.append(f"derived_room_from_device={room.name}")
                    break

        return GroundingResult(room=room_match, device=device_match, evidence=evidence)

    def _canonical_room_name(self, room: RoomContext) -> str | None:
        room_aliases = [normalize_text(room.name), *(normalize_text(alias) for alias in room.aliases)]
        for canonical, aliases in ROOM_ALIASES.items():
            if any(alias in room_aliases for alias in aliases):
                return canonical
        return None

    def _detect_missing_slots(
        self,
        intent: str,
        entities: ExtractedEntities,
        grounding: GroundingResult,
        context: HomeContext | None,
    ) -> list[str]:
        missing: list[str] = []
        if intent == "control_device":
            if entities.action is None:
                missing.append("action")
            if grounding.device is None and entities.device_type is None and entities.scope is None:
                missing.append("device")
            explicit_target_missing = entities.room_name is None and entities.device_name is None
            if (
                entities.scope is None
                and context
                and len(context.rooms) > 1
                and explicit_target_missing
            ):
                missing.append("room")
            if entities.action == "set_temperature" and entities.value is None:
                missing.append("value")
        elif intent in {"query_sensor", "query_device_status"}:
            if entities.sensor_type is None and intent == "query_sensor":
                missing.append("sensor_type")
            if grounding.device is None and grounding.room is None and context and len(context.rooms) > 1:
                missing.append("target")
        return missing

    def _build_action_draft(
        self,
        intent: str,
        entities: ExtractedEntities,
        grounding: GroundingResult,
    ) -> ActionDraft | None:
        if intent == "environmental_comfort":
            if entities.comfort_type == "cooling":
                return ActionDraft(
                    device_id=grounding.device.id if grounding.device else None,
                    device_type="fan",
                    room_id=grounding.room.id if grounding.room else None,
                    action="turn_on",
                )
            if entities.comfort_type == "lighting":
                return ActionDraft(
                    device_id=grounding.device.id if grounding.device else None,
                    device_type="light",
                    room_id=grounding.room.id if grounding.room else None,
                    action="turn_on",
                )
            return None
        if intent != "control_device":
            return None
        if entities.action is None:
            return None
        return ActionDraft(
            device_id=grounding.device.id if grounding.device else None,
            device_type=entities.device_type,
            room_id=grounding.room.id if grounding.room else None,
            action=entities.action,
            value=entities.value,
            scope=entities.scope,
        )
