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

    async def _get(self, path: str, params: dict[str, str]) -> list[dict]:
        url = f"{self._base}/{path}"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        return data.get("meals") or []

    async def search_by_letter(self, letter: str) -> list[dict]:
        return await self._get("search.php", {"f": letter})

    async def search_by_name(self, name: str) -> list[dict]:
        return await self._get("search.php", {"s": name})

    async def filter_by(self, key: str, value: str) -> list[dict]:
        """filter.php?c|i|a — yalnız idMeal/strMeal/strMealThumb döner (detay yok)."""
        return await self._get("filter.php", {key: value})

    async def lookup(self, meal_id: str) -> dict | None:
        meals = await self._get("lookup.php", {"i": meal_id})
        return meals[0] if meals else None

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
