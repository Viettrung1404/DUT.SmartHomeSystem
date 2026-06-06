from __future__ import annotations

import re
import unicodedata


def strip_accents(value: str) -> str:
    value = value.replace("đ", "d").replace("Đ", "D")
    normalized = unicodedata.normalize("NFD", value)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def normalize_text(text: str) -> str:
    text = text.strip().lower()
    text = text.replace("°c", " do c ").replace("ºc", " do c ")
    text = text.replace("%", " phan tram ")
    text = strip_accents(text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
