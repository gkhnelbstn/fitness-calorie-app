"""İkame kural motoru — deterministik. LLM değil; kural tablosu karar verir.

Mantık (tarif adaptasyonunda kullanılır):
- Blacklist'teki malzeme tarifte 'optional' ise → çıkarılır.
- Değilse ve SUBSTITUTES'te ikamesi varsa (ve ikame blacklist'te değilse) → ikame edilir.
- İkisi de yoksa → tarif bu blacklist için uyarlanamaz (elenir).
"""

from __future__ import annotations

# canonical slug → ikame canonical slug (zorunlu malzeme için yedek)
SUBSTITUTES: dict[str, str] = {
    "tereyagi": "zeytinyagi",
    "zeytinyagi": "tereyagi",
    "sehriye": "pirinc",
    "pirinc": "sehriye",
}


def substitute_for(slug: str) -> str | None:
    return SUBSTITUTES.get(slug)
