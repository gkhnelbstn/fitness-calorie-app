"""Yemek planı parser — markdown formatlı plan metnini parse eder.

Format örneği:
    # Gün 0
    - Kahvaltı: 2 yumurta, 1 simit
    - Öğle: 1 kase pilav, 1 ayran
    # Gün 1
    - Kahvaltı: omlet
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_DAY_RE = re.compile(r"^\s*#+\s*Gün\s+(\d+)\s*$", re.IGNORECASE)
_MEAL_RE = re.compile(r"^\s*[-*]\s*([^:]+):\s*(.+)$")

_MEAL_TYPE_MAP = {
    "kahvaltı": "kahvalti",
    "kahvalti": "kahvalti",
    "öğle": "ogle",
    "ogle": "ogle",
    "öğlen": "ogle",
    "akşam": "aksam",
    "aksam": "aksam",
    "atıştırma": "atistirma",
    "atistirma": "atistirma",
    "ara öğün": "ara_ogun",
    "ara ogun": "ara_ogun",
}


@dataclass
class PlanEntry:
    day_offset: int
    meal_type: str
    raw_text: str


def parse_plan(text: str) -> list[PlanEntry]:
    entries: list[PlanEntry] = []
    current_day = 0
    for line in text.splitlines():
        m = _DAY_RE.match(line)
        if m:
            current_day = int(m.group(1))
            continue
        mm = _MEAL_RE.match(line)
        if mm:
            label = mm.group(1).strip().casefold()
            meal_type = _MEAL_TYPE_MAP.get(label, label)
            entries.append(
                PlanEntry(
                    day_offset=current_day,
                    meal_type=meal_type,
                    raw_text=mm.group(2).strip(),
                )
            )
    return entries
