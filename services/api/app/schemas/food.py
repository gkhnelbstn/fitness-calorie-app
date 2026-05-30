"""Yiyecek porsiyon şemaları — ölçü seçimi + her ölçünün besin karşılığı."""

from __future__ import annotations

from pydantic import BaseModel


class PortionOption(BaseModel):
    measure: str  # tabak / kase / dilim / adet / yemek kaşığı …
    grams: float
    kcal: float | None = None
    protein_g: float | None = None
    carb_g: float | None = None
    fat_g: float | None = None


class FoodPortions(BaseModel):
    name: str
    canonical_id: int | None = None
    matched: bool = False  # canonical + besin bulundu mu?
    default_measure: str | None = None
    portions: list[PortionOption] = []
