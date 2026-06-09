"""Tarif toplam besin değerlerini hesapla (canonical + nutrition + birim→gram)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import NutritionProfile, RecipeIngredient
from .units import resolve_grams


async def compute_recipe_macros(session: AsyncSession, recipe_id: int) -> dict[str, float] | None:
    """Tarifin tüm malzemelerinin (opsiyonel dahil) toplam besin değerleri.

    Döner: {"kcal", "protein_g", "carb_g", "fat_g", "fiber_g"} (yuvarlanmış).
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

    totals = {"kcal": 0.0, "protein_g": 0.0, "carb_g": 0.0, "fat_g": 0.0, "fiber_g": 0.0}
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
        factor = grams / 100.0
        totals["kcal"] += np_row.kcal * factor
        totals["protein_g"] += (np_row.protein_g or 0.0) * factor
        totals["carb_g"] += (np_row.carb_g or 0.0) * factor
        totals["fat_g"] += (np_row.fat_g or 0.0) * factor
        totals["fiber_g"] += (np_row.fiber_g or 0.0) * factor
        counted = True

    if not counted:
        return None
    return {k: round(v, 1) for k, v in totals.items()}


async def compute_recipe_kcal(session: AsyncSession, recipe_id: int) -> float | None:
    """Geriye dönük uyumluluk: yalnız toplam kaloriyi döndürür."""
    macros = await compute_recipe_macros(session, recipe_id)
    return macros["kcal"] if macros else None
