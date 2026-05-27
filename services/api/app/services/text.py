"""Türkçe metin normalizasyonu — alias eşleştirme için ortak biçim."""

from __future__ import annotations

import re

_TR_MAP = str.maketrans(
    {
        "ç": "c",
        "Ç": "c",
        "ğ": "g",
        "Ğ": "g",
        "ı": "i",
        "İ": "i",
        "ö": "o",
        "Ö": "o",
        "ş": "s",
        "Ş": "s",
        "ü": "u",
        "Ü": "u",
        "â": "a",
        "î": "i",
        "û": "u",
    }
)


def slugify_tr(value: str) -> str:
    """Türkçe metni ascii slug'a çevir. Ör. 'Mercimek Çorbası' → 'mercimek-corbasi'."""
    s = value.strip().translate(_TR_MAP).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def normalize_tr(value: str) -> str:
    """Küçült + boşlukları sadeleştir + baş/son noktalama temizle.

    Alias tablosu da aynı biçimle saklanır; eşleştirme bunun üzerinden olur.
    """
    cleaned = value.strip().strip(".,;:!?").casefold()
    return " ".join(cleaned.split())
