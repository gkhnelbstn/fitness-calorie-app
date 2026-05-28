"""Tarif toplam kalorisini hesapla (canonical + nutrition + birim→gram)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import NutritionProfile, RecipeIngredient
from .units import resolve_grams


async def compute_recipe_kcal(session: AsyncSession, recipe_id: int) -> float | None:
    """Tarifin tüm malzemelerinin (opsiyonel dahil) toplam kalorisi.

    Eksik canonical/quantity/unit/nutrition kaydı OLAN satırlar atlanır.
    Hiçbir satır hesaba katılamazsa None döner.
    """
    rows = (
        (
            await session.execute(
                select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe_id)
            )
        )
        .scalars()
        .all()
    )

    total = 0.0
    counted = False
    for r in rows:
        if r.canonical_id is None or r.quantity is None or r.unit is None:
            continue
        grams = resolve_grams(r.quantity, r.unit)
        if grams is None:
            continue
        np_row = (
            (
                await session.execute(
                    select(NutritionProfile).where(
                        NutritionProfile.canonical_id == r.canonical_id,
                        NutritionProfile.basis == "per_100g",
                    )
                )
            )
            .scalars()
            .first()
        )
        if np_row is None or np_row.kcal is None:
            continue
        total += np_row.kcal * grams / 100.0
        counted = True

    return round(total, 1) if counted else None
