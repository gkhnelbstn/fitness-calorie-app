"""Tarif şemaları (Faz 0 stub)."""

from __future__ import annotations

from pydantic import BaseModel


class RecipeIngredientRead(BaseModel):
    raw_name: str
    quantity: float | None = None
    unit: str | None = None
    optional: bool = False


class RecipeRead(BaseModel):
    id: int
    slug: str
    title_tr: str
    servings: int | None = None
    total_kcal: float | None = None
    region: str | None = None
    ingredients: list[RecipeIngredientRead] = []
    steps: list[str] = []
