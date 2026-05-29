"""Türkçe → İngilizce yemek terimi sözlüğü + TheMealDB sorgu çözümleme.

Amaç: arama çevirisini LLM'e bağımlı olmaktan kurtarmak. Yaygın Türkçe yemekler
(tavuk/et/köfte/salata/pirinç...) deterministik olarak İngilizce ada + TheMealDB
kategori/malzeme/bölge ipuçlarına eşlenir. Sözlük ıskalarsa LLM'e düşülür.

TheMealDB kategorileri: Beef, Chicken, Dessert, Lamb, Miscellaneous, Pasta, Pork,
Seafood, Side, Starter, Vegan, Vegetarian, Breakfast, Goat.
filter.php?i=<ingredient> çok-kelime için alt çizgi (ör. chicken_breast).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..services.text import normalize_tr


@dataclass
class TermHints:
    names: set[str] = field(default_factory=set)  # search.php?s=
    categories: set[str] = field(default_factory=set)  # filter.php?c=
    ingredients: set[str] = field(default_factory=set)  # filter.php?i=
    areas: set[str] = field(default_factory=set)  # filter.php?a=

    def any(self) -> bool:
        return bool(self.names or self.categories or self.ingredients or self.areas)

    def merge(self, other: TermHints) -> None:
        self.names |= other.names
        self.categories |= other.categories
        self.ingredients |= other.ingredients
        self.areas |= other.areas


# tr terim → (en adlar, kategoriler, malzemeler, bölgeler)
_MAP: dict[str, TermHints] = {
    "tavuk": TermHints({"chicken"}, {"Chicken"}, {"chicken_breast", "chicken"}, set()),
    "tavuk göğsü": TermHints({"chicken breast"}, {"Chicken"}, {"chicken_breast"}, set()),
    "et": TermHints({"beef"}, {"Beef"}, {"beef"}, set()),
    "dana": TermHints({"beef"}, {"Beef"}, {"beef"}, set()),
    "biftek": TermHints({"steak"}, {"Beef"}, {"beef"}, set()),
    "kıyma": TermHints({"minced beef"}, {"Beef"}, {"minced_beef", "beef"}, set()),
    "kuzu": TermHints({"lamb"}, {"Lamb"}, {"lamb"}, set()),
    "köfte": TermHints({"kofta", "meatball"}, set(), {"minced_beef"}, {"Turkish"}),
    "kebap": TermHints({"kebab"}, set(), set(), {"Turkish"}),
    "balık": TermHints({"fish"}, {"Seafood"}, {"salmon", "cod"}, set()),
    "somon": TermHints({"salmon"}, {"Seafood"}, {"salmon"}, set()),
    "karides": TermHints({"prawns", "shrimp"}, {"Seafood"}, {"prawns"}, set()),
    "ton balığı": TermHints({"tuna"}, {"Seafood"}, {"tuna"}, set()),
    "salata": TermHints({"salad"}, {"Starter", "Side"}, set(), set()),
    "pirinç": TermHints({"rice", "rice pilaf"}, set(), {"rice"}, set()),
    "pilav": TermHints({"rice", "pilaf"}, set(), {"rice"}, {"Turkish"}),
    "makarna": TermHints({"pasta"}, {"Pasta"}, set(), set()),
    "spagetti": TermHints({"spaghetti"}, {"Pasta"}, set(), set()),
    "çorba": TermHints({"soup"}, set(), set(), set()),
    "mercimek": TermHints({"lentil"}, set(), {"lentils"}, set()),
    "nohut": TermHints({"chickpea"}, set(), {"chickpeas"}, set()),
    "fasulye": TermHints({"beans"}, set(), {"kidney_beans"}, set()),
    "patates": TermHints({"potato"}, set(), {"potatoes"}, set()),
    "patlıcan": TermHints({"aubergine", "eggplant"}, set(), {"aubergine"}, set()),
    "mantar": TermHints({"mushroom"}, set(), {"mushrooms"}, set()),
    "yumurta": TermHints({"omelette", "egg"}, {"Breakfast"}, {"eggs"}, set()),
    "peynir": TermHints({"cheese"}, set(), {"cheese"}, set()),
    "ekmek": TermHints({"bread"}, set(), set(), set()),
    "domates": TermHints({"tomato"}, set(), {"tomatoes"}, set()),
    "tatlı": TermHints({"dessert", "cake"}, {"Dessert"}, set(), set()),
    "kek": TermHints({"cake"}, {"Dessert"}, set(), set()),
    "börek": TermHints({"pie", "borek"}, set(), set(), {"Turkish"}),
    "pide": TermHints({"pide", "flatbread"}, set(), set(), {"Turkish"}),
    "lahmacun": TermHints({"lahmacun"}, set(), set(), {"Turkish"}),
    "kahvaltı": TermHints({"breakfast"}, {"Breakfast"}, set(), set()),
    "vejetaryen": TermHints({"vegetarian"}, {"Vegetarian"}, set(), set()),
    "vegan": TermHints({"vegan"}, {"Vegan"}, set(), set()),
    "deniz": TermHints({"seafood"}, {"Seafood"}, set(), set()),
    "hindi": TermHints({"turkey"}, set(), {"turkey"}, set()),
    "domuz": TermHints({"pork"}, {"Pork"}, {"pork"}, set()),
    "yoğurt": TermHints({"yogurt"}, set(), {"yogurt"}, set()),
    "ıspanak": TermHints({"spinach"}, set(), {"spinach"}, set()),
    "türk": TermHints(set(), set(), set(), {"Turkish"}),
}

# çekirdek kelimeler (token bazlı eşleşme için): "tavuklu sote" → tavuk
_TOKEN_KEYS = sorted(_MAP.keys(), key=len, reverse=True)


def resolve_query(query_tr: str) -> TermHints:
    """Türkçe sorgudan TheMealDB ipuçları çıkar (tam + token eşleşme)."""
    norm = normalize_tr(query_tr)
    hints = TermHints()
    if not norm:
        return hints
    if norm in _MAP:
        hints.merge(_MAP[norm])
    words = set(norm.split())
    for key in _TOKEN_KEYS:
        # Kısa anahtar (≤3) tam-kelime; uzun anahtar substring ("tavuklu"→"tavuk").
        # Böylece "et" yanlışlıkla "spagetti" içinde eşleşmez.
        if (key in words) if len(key) <= 3 else (key in norm):
            hints.merge(_MAP[key])
    return hints
