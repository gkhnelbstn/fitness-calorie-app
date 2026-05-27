"""Türkçe metin normalizasyonu — alias eşleştirme için ortak biçim."""

from __future__ import annotations


def normalize_tr(value: str) -> str:
    """Küçült + boşlukları sadeleştir + baş/son noktalama temizle.

    Alias tablosu da aynı biçimle saklanır; eşleştirme bunun üzerinden olur.
    """
    cleaned = value.strip().strip(".,;:!?").casefold()
    return " ".join(cleaned.split())
