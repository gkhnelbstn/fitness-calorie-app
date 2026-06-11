"""Yiyecek porsiyon endpoint'i — bir yiyecek için seçilebilir ölçüler + besin.

Kullanıcı doğal-dil yerine "1 tabak / 2 kaşık" gibi seçim yapabilsin; her ölçünün
kalori/makro karşılığı yerel besin profilinden hesaplanır.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..data.portions import measure_grams, measures_for
from ..db import get_session
from ..schemas.food import FoodPortions, PortionOption
from ..services.nutrition import resolve_nutrition
from ..services.resolver import resolve_canonical

router = APIRouter(prefix="/api/foods", tags=["foods"], dependencies=[Depends(get_current_user)])


@router.get("/portions", response_model=FoodPortions)
async def food_portions(
    name: str = Query(..., min_length=1, description="Yiyecek adı (ör. pilav, çorba)"),
    session: AsyncSession = Depends(get_session),
) -> FoodPortions:
    canon = await resolve_canonical(session, name)
    slug = canon.slug if canon else None
    category = canon.category if canon else None
    measures = measures_for(slug, category)

    options: list[PortionOption] = []
    for m in measures:
        grams = measure_grams(m)
        if grams is None:
            continue
        macros = await resolve_nutrition(session, canon.id, grams) if canon else None
        options.append(
            PortionOption(
                measure=m,
                grams=grams,
                kcal=macros.kcal if macros else None,
                protein_g=macros.protein_g if macros else None,
                carb_g=macros.carb_g if macros else None,
                fat_g=macros.fat_g if macros else None,
            )
        )

    return FoodPortions(
        name=name,
        canonical_id=canon.id if canon else None,
        matched=canon is not None,
        default_measure=measures[0] if measures else None,
        portions=options,
    )
