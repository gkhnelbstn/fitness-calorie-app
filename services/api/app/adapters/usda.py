"""USDA FoodData Central adapter — jenerik besin değeri (ücretsiz, CC0).

Ücretsiz anahtar: api.data.gov; DEMO_KEY ile sınırlı test. 1000 istek/saat/IP.
"""

from __future__ import annotations

import httpx

from ..config import get_settings
from .base import FoodHit

_NUTRIENT_MAP = {
    "Energy": "kcal_per_100g",
    "Protein": "protein_g",
    "Carbohydrate, by difference": "carb_g",
    "Total lipid (fat)": "fat_g",
}


class UsdaAdapter:
    source = "USDA FoodData Central"

    def __init__(self) -> None:
        s = get_settings()
        self._base = s.usda_base_url
        self._key = s.usda_api_key

    async def search(self, query: str, page_size: int = 5) -> list[FoodHit]:
        url = f"{self._base}/foods/search"
        params = {"api_key": self._key, "query": query, "pageSize": page_size}
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        hits: list[FoodHit] = []
        for food in data.get("foods", []):
            values: dict[str, float | None] = {}
            for nut in food.get("foodNutrients", []):
                key = _NUTRIENT_MAP.get(nut.get("nutrientName", ""))
                if key:
                    values[key] = nut.get("value")
            hits.append(
                FoodHit(
                    name=food.get("description", query),
                    source=self.source,
                    kcal_per_100g=values.get("kcal_per_100g"),
                    protein_g=values.get("protein_g"),
                    carb_g=values.get("carb_g"),
                    fat_g=values.get("fat_g"),
                    raw=food,
                )
            )
        return hits
