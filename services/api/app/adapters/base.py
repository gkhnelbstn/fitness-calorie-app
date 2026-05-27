"""Adapter ortak temeli."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FoodHit:
    """Bir besin/ürün araması için normalize edilmiş asgari sonuç."""

    name: str
    source: str
    kcal_per_100g: float | None = None
    protein_g: float | None = None
    carb_g: float | None = None
    fat_g: float | None = None
    barcode: str | None = None
    raw: dict | None = None


@dataclass
class ExerciseHit:
    name: str
    source: str
    primary_muscle: str | None = None
    level: str | None = None
    equipment: str | None = None
    raw: dict | None = None
