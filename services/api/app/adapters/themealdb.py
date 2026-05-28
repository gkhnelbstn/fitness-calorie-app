"""TheMealDB adapter — ücretsiz tarif kaynağı (İngilizce). Test key '1'.

Harf bazlı arama: /search.php?f=a  → meals[] (strMeal, strInstructions,
strArea, strCategory, strIngredient1..20, strMeasure1..20).
"""

from __future__ import annotations

import httpx

from ..config import get_settings


class TheMealDbAdapter:
    source = "TheMealDB"

    def __init__(self) -> None:
        self._base = get_settings().themealdb_base_url

    async def search_by_letter(self, letter: str) -> list[dict]:
        url = f"{self._base}/search.php"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, params={"f": letter})
            resp.raise_for_status()
            data = resp.json()
        return data.get("meals") or []

    @staticmethod
    def extract_ingredients(meal: dict) -> list[tuple[str, str]]:
        """(ingredient, measure) listesi — boş olanlar atlanır."""
        out: list[tuple[str, str]] = []
        for i in range(1, 21):
            ing = (meal.get(f"strIngredient{i}") or "").strip()
            meas = (meal.get(f"strMeasure{i}") or "").strip()
            if ing:
                out.append((ing, meas))
        return out
