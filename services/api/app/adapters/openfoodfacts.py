"""Open Food Facts adapter — barkod/paketli ürün (ücretsiz, ODbL).

Not: özel User-Agent zorunlu; okuma limiti ~15/dk. Toplu çekme yapma.
"""

from __future__ import annotations

import httpx

from ..config import get_settings
from .base import FoodHit


class OpenFoodFactsAdapter:
    source = "OpenFoodFacts"

    def __init__(self) -> None:
        s = get_settings()
        self._base = s.off_base_url
        self._headers = {"User-Agent": s.off_user_agent}

    async def by_barcode(self, barcode: str) -> FoodHit | None:
        url = f"{self._base}/api/v2/product/{barcode}.json"
        async with httpx.AsyncClient(timeout=10, headers=self._headers) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
        if data.get("status") != 1:
            return None
        p = data.get("product", {})
        n = p.get("nutriments", {})
        return FoodHit(
            name=p.get("product_name") or barcode,
            source=self.source,
            kcal_per_100g=n.get("energy-kcal_100g"),
            protein_g=n.get("proteins_100g"),
            carb_g=n.get("carbohydrates_100g"),
            fat_g=n.get("fat_100g"),
            barcode=barcode,
            raw=p,
        )
