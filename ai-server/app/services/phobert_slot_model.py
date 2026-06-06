from __future__ import annotations

from dataclasses import dataclass
import json
import re

from app.core.capabilities import ACTION_ALIASES, DEVICE_TYPE_ALIASES, ROOM_ALIASES, SENSOR_TYPE_ALIASES
from app.core.settings import get_settings
from app.schemas.nlp import ExtractedEntities
from app.services.text_normalizer import normalize_text


TOKEN_PATTERN = re.compile(r"[0-9A-Za-zÀ-ỹà-ỹđĐ_]+", re.UNICODE)


@dataclass(frozen=True)
class SlotModelResult:
    entities: ExtractedEntities
    evidence: list[str]


class PhoBERTSlotModel:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._model = None
        self._tokenizer = None
        self._label_list: list[str] = []
        self._available = False
        if self.settings.enable_hybrid_slot_model:
            self._available = self._load()

    @property
    def available(self) -> bool:
        return self._available

    def _load(self) -> bool:
        model_dir = self.settings.phobert_slot_dir
        metadata_path = model_dir / "slot_metadata.json"
        if not model_dir.exists() or not metadata_path.exists():
            return False
        try:
            from transformers import AutoModelForTokenClassification, AutoTokenizer
        except Exception:
            return False
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        self._label_list = list(metadata.get("label_list", []))
        self._tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self._model = AutoModelForTokenClassification.from_pretrained(model_dir)
        self._model.eval()
        return bool(self._label_list)

    def extract_entities(self, text: str) -> SlotModelResult:
        if not self.available or self._model is None or self._tokenizer is None:
            return SlotModelResult(entities=ExtractedEntities(), evidence=["slot_model_unavailable"])
        tokens = TOKEN_PATTERN.findall(text)
        if not tokens:
            return SlotModelResult(entities=ExtractedEntities(), evidence=["slot_model_empty_input"])
        pieces: list[int] = [self._tokenizer.cls_token_id]
        token_to_piece_index: list[int] = []
        for token in tokens:
            token_pieces = self._tokenizer.convert_tokens_to_ids(self._tokenizer.tokenize(token))
            if not token_pieces:
                token_pieces = [self._tokenizer.unk_token_id]
            token_to_piece_index.append(len(pieces))
            pieces.extend(token_pieces)
        pieces.append(self._tokenizer.sep_token_id)
        attention_mask = [1] * len(pieces)
        import torch
        with torch.no_grad():
            outputs = self._model(
                input_ids=torch.tensor([pieces], dtype=torch.long),
                attention_mask=torch.tensor([attention_mask], dtype=torch.long),
            )
        logits = outputs.logits[0]
        pred_ids = torch.argmax(logits, dim=-1).tolist()
        word_tags = [self._label_list[pred_ids[piece_idx]] for piece_idx in token_to_piece_index]
        spans = self._decode_spans(tokens, word_tags)
        entities = self._spans_to_entities(spans)
        evidence = [f"slot_model=phobert_slot_hybrid", f"slot_tags={word_tags}"]
        return SlotModelResult(entities=entities, evidence=evidence)

    def _decode_spans(self, tokens: list[str], tags: list[str]) -> dict[str, str]:
        spans: dict[str, str] = {}
        current_label: str | None = None
        current_tokens: list[str] = []
        for token, tag in zip(tokens, tags, strict=True):
            if tag == "O":
                if current_label and current_tokens:
                    spans.setdefault(current_label, " ".join(current_tokens))
                current_label = None
                current_tokens = []
                continue
            prefix, label = tag.split("-", 1)
            if prefix == "B":
                if current_label and current_tokens:
                    spans.setdefault(current_label, " ".join(current_tokens))
                current_label = label
                current_tokens = [token]
            elif prefix == "I" and current_label == label:
                current_tokens.append(token)
            else:
                if current_label and current_tokens:
                    spans.setdefault(current_label, " ".join(current_tokens))
                current_label = None
                current_tokens = []
        if current_label and current_tokens:
            spans.setdefault(current_label, " ".join(current_tokens))
        return spans

    def _spans_to_entities(self, spans: dict[str, str]) -> ExtractedEntities:
        entities = ExtractedEntities()
        room_text = spans.get("room")
        if room_text:
            entities.room_name = self._canonical_from_alias(room_text, ROOM_ALIASES)
        device_name = spans.get("device_name")
        if device_name:
            entities.device_name = device_name
        device_type = spans.get("device_type")
        if device_type:
            entities.device_type = self._canonical_from_alias(device_type, DEVICE_TYPE_ALIASES) or normalize_text(device_type)
        action_text = spans.get("action")
        if action_text:
            entities.action = self._canonical_action(action_text)
        sensor_text = spans.get("sensor_type")
        if sensor_text:
            entities.sensor_type = self._canonical_from_alias(sensor_text, SENSOR_TYPE_ALIASES) or normalize_text(sensor_text)
        comparison = spans.get("comparison")
        if comparison:
            normalized = normalize_text(comparison)
            if "nong" in normalized or "bi" in normalized:
                entities.comfort_type = "cooling"
            elif "toi" in normalized:
                entities.comfort_type = "lighting"
            elif "am" in normalized:
                entities.comfort_type = "humidity"
        return entities

    def _canonical_from_alias(self, text: str, alias_map: dict[str, list[str]]) -> str | None:
        normalized = normalize_text(text)
        for canonical, aliases in alias_map.items():
            if normalized == canonical or normalized in aliases:
                return canonical
        return None

    def _canonical_action(self, text: str) -> str:
        normalized = normalize_text(text)
        for canonical, aliases in ACTION_ALIASES.items():
            if normalized == canonical or normalized in aliases:
                return canonical
        return normalized
