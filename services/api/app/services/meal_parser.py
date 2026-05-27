"""Kurallı Türkçe yemek ayrıştırıcı (LLM yoksa fallback).

"öğlen 1 kase kuru fasulye, 1 kase pilav, 1 ayran içtim"
  → [(kuru fasulye,1,kase), (pilav,1,kase), (ayran,1,None)]

LLM yalnızca {isim,miktar,birim} çıkarır; bu da aynı sözleşmeyi üretir.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .text import normalize_tr
from .units import KNOWN_UNITS

# Türkçe sayı sözcükleri
_WORD_NUM: dict[str, float] = {
    "yarım": 0.5,
    "yarim": 0.5,
    "bir": 1,
    "iki": 2,
    "üç": 3,
    "uc": 3,
    "dört": 4,
    "dort": 4,
    "beş": 5,
    "bes": 5,
}

# Atılacak dolgu/zaman/fiil sözcükleri
_STOP = {
    "sabah",
    "öğlen",
    "öğle",
    "ogle",
    "akşam",
    "aksam",
    "gece",
    "gün",
    "kahvaltı",
    "kahvaltıda",
    "kahvaltida",
    "öğünde",
    "ogunde",
    "bugün",
    "bugun",
    "yedim",
    "içtim",
    "ictim",
    "aldım",
    "aldim",
    "tükettim",
    "tukettim",
    "de",
    "da",
}

_SPLIT = re.compile(r"\s*(?:,|;|\bve\b|\bile\b|\n)\s*", flags=re.IGNORECASE)


@dataclass
class ParsedItem:
    name: str
    quantity: float | None = None
    unit: str | None = None


def _as_number(token: str) -> float | None:
    if token in _WORD_NUM:
        return _WORD_NUM[token]
    try:
        return float(token.replace(",", "."))
    except ValueError:
        return None


def _match_unit(tokens: list[str]) -> tuple[str | None, int]:
    """tokens başında birim ifadesi ara. (unit, tüketilen_token_sayısı)."""
    for size in (3, 2, 1):
        if len(tokens) >= size:
            phrase = normalize_tr(" ".join(tokens[:size]))
            if phrase in KNOWN_UNITS:
                return phrase, size
    return None, 0


def _clean_name(tokens: list[str]) -> str:
    kept = [t for t in tokens if normalize_tr(t) not in _STOP]
    return " ".join(kept).strip()


def parse_meal_text(text: str) -> list[ParsedItem]:
    items: list[ParsedItem] = []
    for chunk in _SPLIT.split(text):
        chunk = chunk.strip()
        if not chunk:
            continue
        tokens = chunk.split()

        # İlk sayısal token = miktar
        qty: float | None = None
        qty_idx = -1
        for i, tok in enumerate(tokens):
            n = _as_number(normalize_tr(tok))
            if n is not None:
                qty, qty_idx = n, i
                break

        if qty_idx == -1:
            name = _clean_name(tokens)
            if name:
                items.append(ParsedItem(name=name))
            continue

        rest = tokens[qty_idx + 1 :]
        unit, used = _match_unit(rest)
        name = _clean_name(rest[used:])
        if not name:  # sayı vardı ama isim yok → atla
            continue
        items.append(ParsedItem(name=name, quantity=qty, unit=unit))
    return items
