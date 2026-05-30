"""Ev-ölçü porsiyon tabloları — bir yiyecek için seçilebilir ölçüler + gram karşılığı.

Kullanıcı "1 tabak / 2 kaşık / 1 kase" gibi seçim yapabilsin diye. Ölçü→gram
kabaca; units.py ile uyumlu. Kategoriye göre mantıklı ölçü kümesi sunulur
(ör. içeceğe "dilim" önerilmez). Malzeme-özel override mümkün.
"""

from __future__ import annotations

# Ölçü etiketi → 1 birim gram (units.py UNIT_GRAMS ile uyumlu, porsiyon odaklı).
MEASURE_GRAMS: dict[str, float] = {
    "porsiyon": 250,
    "tabak": 300,
    "kase": 250,
    "su bardağı": 200,
    "çay bardağı": 100,
    "dilim": 30,
    "adet": 50,
    "avuç": 30,
    "yemek kaşığı": 15,
    "tatlı kaşığı": 7,
    "çay kaşığı": 3,
}

# Kategori (IngredientCanonical.category) → uygun ölçüler (sıralı, ilk = varsayılan).
_BY_CATEGORY: dict[str, list[str]] = {
    "içecek": ["su bardağı", "çay bardağı"],
    "çorba": ["kase", "tabak", "porsiyon"],
    "tatlı": ["porsiyon", "dilim", "kase"],
    "fırın": ["dilim", "adet", "porsiyon"],
    "hamur işi": ["dilim", "adet", "porsiyon"],
    "fast food": ["porsiyon", "adet"],
    "et yemeği": ["porsiyon", "adet", "tabak"],
    "süt": ["porsiyon", "dilim", "yemek kaşığı"],
    "meze": ["porsiyon", "kase", "yemek kaşığı"],
    "salata": ["porsiyon", "tabak", "kase"],
    "kahvaltı": ["porsiyon", "tabak", "adet"],
    "tahıl": ["porsiyon", "kase", "tabak"],
    "baklagil": ["porsiyon", "kase", "tabak"],
    "protein": ["porsiyon", "adet", "tabak"],
    "sebze": ["porsiyon", "tabak", "yemek kaşığı"],
    "baharat": ["çay kaşığı", "tatlı kaşığı", "yemek kaşığı"],
    "konserve": ["yemek kaşığı", "tatlı kaşığı"],
}
_DEFAULT: list[str] = ["porsiyon", "tabak", "kase", "adet", "yemek kaşığı"]

# Malzeme-özel ölçü override (slug → ölçü listesi). Kategori yetmediğinde.
_BY_SLUG: dict[str, list[str]] = {
    "ekmek": ["dilim", "adet"],
    "yumurta": ["adet", "porsiyon"],
    "muz": ["adet"],
    "elma": ["adet"],
    "portakal": ["adet"],
    "zeytin": ["adet", "yemek kaşığı"],
    "ayran": ["su bardağı", "çay bardağı"],
    "kahve": ["çay bardağı", "su bardağı"],
    "kola": ["su bardağı", "çay bardağı"],
}


def measures_for(slug: str | None, category: str | None) -> list[str]:
    """Bir yiyecek için seçilebilir ölçüler (sıralı). slug override > kategori > varsayılan."""
    if slug and slug in _BY_SLUG:
        return _BY_SLUG[slug]
    return _BY_CATEGORY.get((category or "").strip().lower(), _DEFAULT)


def measure_grams(measure: str) -> float | None:
    return MEASURE_GRAMS.get(measure)
