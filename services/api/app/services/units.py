"""Birim → gram dönüşümü (yaklaşık). Kalori hesabı için porsiyon ağırlığı.

Değerler kabaca; Faz 1 MVP. İleride malzeme-özel porsiyon tabloları eklenir.
"""

from __future__ import annotations

from .text import normalize_tr

# Normalize edilmiş birim → gram
UNIT_GRAMS: dict[str, float] = {
    "g": 1,
    "gr": 1,
    "gram": 1,
    "kase": 200,
    "kâse": 200,
    "bardak": 200,
    "su bardağı": 200,
    "su bardagi": 200,
    "çay bardağı": 100,
    "cay bardagi": 100,
    "dilim": 30,
    "adet": 50,
    "tane": 50,
    "tabak": 300,
    "porsiyon": 250,
    "yemek kaşığı": 15,
    "kaşık": 15,
    "kasik": 15,
    "tatlı kaşığı": 7,
    "çay kaşığı": 3,
}

# Bilinen birim ifadeleri (en uzun önce eşleşsin diye sıralı)
KNOWN_UNITS: list[str] = sorted(UNIT_GRAMS, key=len, reverse=True)


def resolve_grams(quantity: float | None, unit: str | None) -> float | None:
    """quantity + unit → gram. Hesaplanamıyorsa None."""
    if quantity is None:
        return None
    if unit is None:
        # Birimsiz sayı (ör. "2 yumurta") = adet varsay.
        return quantity * UNIT_GRAMS["adet"]
    grams = UNIT_GRAMS.get(normalize_tr(unit))
    if grams is None:
        return None
    return quantity * grams
