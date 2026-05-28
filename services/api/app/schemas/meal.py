"""Yemek kaydı şemaları."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class MealItem(BaseModel):
    raw_name: str = Field(..., examples=["kuru fasulye"])
    quantity: float | None = Field(default=None, examples=[1])
    unit: str | None = Field(default=None, examples=["kase"])
    canonical_id: int | None = None
    kcal: float | None = None
    protein_g: float | None = None
    carb_g: float | None = None
    fat_g: float | None = None
    confidence: float | None = None


class MealCreate(BaseModel):
    """Doğal dil veya yapılandırılmış giriş. En az biri dolu olmalı."""

    raw_text: str | None = Field(
        default=None,
        examples=["öğlen 1 kase kuru fasulye, 1 kase pilav, 1 ayran"],
    )
    meal_type: str | None = Field(default=None, examples=["ogle"])
    items: list[MealItem] = Field(default_factory=list)


class BarcodeMealCreate(BaseModel):
    """Barkod ile yemek ekleme (Open Food Facts ile besin değeri çekilir)."""

    barcode: str = Field(..., examples=["8690000000000"])
    grams: float = Field(default=100, ge=1, examples=[200])
    meal_type: str | None = Field(default=None, examples=["kahvalti"])


class MealRead(BaseModel):
    id: int
    eaten_at: datetime
    meal_type: str | None
    raw_text: str | None
    total_kcal: float | None
    items: list[MealItem]
    photo_path: str | None = None
