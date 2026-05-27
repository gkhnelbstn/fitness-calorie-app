"""Günlük özet şeması."""

from __future__ import annotations

from pydantic import BaseModel


class DailySummary(BaseModel):
    day: str  # YYYY-MM-DD
    intake_kcal: float
    protein_g: float
    carb_g: float
    fat_g: float
    meal_count: int
    item_count: int
    # Sağlık verisi (Faz 4) gelince doldurulacak:
    active_kcal: float | None = None
    net_kcal: float | None = None  # intake - active
