"""Spoonacular adapter — tarif arama (İngilizce). Anahtar gerekir (free 150/gün).

complexSearch + bilgilendirme (fillIngredients) → malzeme + adım.
"""

from __future__ import annotations

import httpx

from ..config import get_settings


class SpoonacularAdapter:
    source = "Spoonacular"

    def __init__(self) -> None:
        s = get_settings()
        self._base = s.spoonacular_base_url
        self._key = s.spoonacular_api_key

    @property
    def enabled(self) -> bool:
        return bool(self._key.strip())

    async def search(self, query: str, number: int = 10) -> list[dict]:
        url = f"{self._base}/recipes/complexSearch"
        params: dict[str, str | int] = {
            "apiKey": self._key,
            "query": query,
            "number": number,
            "addRecipeInformation": "true",
            "fillIngredients": "true",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        return data.get("results") or []

    @staticmethod
    def extract_ingredients(recipe: dict) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        for ing in recipe.get("extendedIngredients") or []:
            name = (ing.get("nameClean") or ing.get("name") or "").strip()
            measure = (ing.get("original") or "").strip()
            if name:
                out.append((name, measure))
        return out
