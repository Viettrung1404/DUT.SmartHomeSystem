from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
import json
import re

from app.core.settings import get_settings
from app.datasets.smarthome_corpus import TRAIN_SPLIT, build_restoration_lexicon, load_jsonl
from app.services.text_normalizer import strip_accents


TOKEN_PATTERN = re.compile(r"[0-9A-Za-zÀ-ỹà-ỹđĐ_]+", re.UNICODE)
DIACRITIC_PATTERN = re.compile(r"[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]", re.IGNORECASE)


class VietnameseDiacriticRestorer:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.lexicon = self._load_or_build_lexicon()

    def _load_or_build_lexicon(self) -> dict[str, str]:
        path = self.settings.restoration_lexicon_path
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        train_records = load_jsonl(self.settings.nlp_data_dir / f"{TRAIN_SPLIT}.jsonl")
        if not train_records:
            return {}
        lexicon = build_restoration_lexicon(train_records)
        path.write_text(json.dumps(lexicon, ensure_ascii=False, indent=2), encoding="utf-8")
        return lexicon

    def has_lexicon(self) -> bool:
        return bool(self.lexicon)

    def is_likely_unaccented(self, text: str) -> bool:
        stripped = text.strip()
        if not stripped:
            return False
        tokens = [token for token in TOKEN_PATTERN.findall(stripped) if token]
        if not tokens:
            return False
        has_diacritic = bool(DIACRITIC_PATTERN.search(stripped))
        ascii_ratio = sum(1 for token in tokens if strip_accents(token).lower() == token.lower()) / max(1, len(tokens))
        return not has_diacritic and ascii_ratio >= 0.8

    def restore_tokens(self, tokens: Sequence[str]) -> list[str]:
        return [self.lexicon.get(token.lower(), token) for token in tokens]

    def restore_text(self, text: str) -> str:
        pieces = TOKEN_PATTERN.findall(text)
        if not pieces:
            return text
        restored = self.restore_tokens([piece.lower() for piece in pieces])
        return " ".join(restored)

    def coverage_for_tokens(self, tokens: Sequence[str]) -> float:
        lowered = [token.lower() for token in tokens if token]
        if not lowered:
            return 0.0
        covered = sum(1 for token in lowered if token in self.lexicon)
        return covered / len(lowered)
