"""Besin değeri çözümleme — yerel nutrition_profile (per_100g) → makro.

Faz 1: yalnızca yerel DB (TurKomp/seed). USDA/OFF fallback Faz 1.5/sonra.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import NutritionProfile


@dataclass
class Macros:
    kcal: float | None = None
    protein_g: float | None = None
    carb_g: float | None = None
    fat_g: float | None = None


def _scale(value: float | None, grams: float) -> float | None:
    if value is None:
        return None
    return round(value * grams / 100.0, 1)


async def resolve_nutrition(
    session: AsyncSession, canonical_id: int, grams: float
) -> Macros | None:
    profile = (
        (
            await session.execute(
                select(NutritionProfile).where(
                    NutritionProfile.canonical_id == canonical_id,
                    NutritionProfile.basis == "per_100g",
                )
            )
        )
        .scalars()
        .first()
    )
    if profile is None:
        return None
    return Macros(
        kcal=_scale(profile.kcal, grams),
        protein_g=_scale(profile.protein_g, grams),
        carb_g=_scale(profile.carb_g, grams),
        fat_g=_scale(profile.fat_g, grams),
    )
