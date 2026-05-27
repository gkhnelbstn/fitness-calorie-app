"""Tarif şemaları (Faz 2 — adaptasyon notlarıyla)."""

from __future__ import annotations

from pydantic import BaseModel


class IngredientLine(BaseModel):
    raw_name: str
    quantity: float | None = None
    unit: str | None = None
    canonical_id: int | None = None
    optional: bool = False
    status: str = "ok"  # ok | removed | substituted
    substitute: str | None = None


class RecipeRead(BaseModel):
    id: int
    slug: str
    title_tr: str
    servings: int | None = None
    region: str | None = None
    total_kcal: float | None = None
    adaptable: bool = True
    ingredients: list[IngredientLine] = []
    steps: list[str] = []
    tags: list[str] = []
    notes: list[str] = []  # "X çıkarıldı", "X yerine Y" gibi
