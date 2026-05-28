"""USDA FoodData Central'dan besin import et → canonical + nutrition_profile.

İngilizce isimler NVIDIA LLM ile Türkçeye çevrilir (anahtar yoksa İngilizce).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..adapters.usda import UsdaAdapter
from ..models import NutritionProfile
from .resolver import get_or_create_canonical
from .sources import get_or_create_source
from .translate import Translator


async def import_usda(
    session: AsyncSession, query: str, *, page_size: int = 10, do_translate: bool = True
) -> int:
    adapter = UsdaAdapter()
    translator = Translator()
    source = await get_or_create_source(
        session,
        name="USDA FoodData Central",
        url="https://fdc.nal.usda.gov",
        license="CC0",
        license_mode="serbest",
    )
    count = 0
    for hit in await adapter.search(query, page_size=page_size):
        name_tr = await translator.to_turkish(hit.name) if do_translate else hit.name
        canon = await get_or_create_canonical(session, name_tr)
        exists = (
            await session.execute(
                select(NutritionProfile.id).where(NutritionProfile.canonical_id == canon.id)
            )
        ).first()
        if exists is None and hit.kcal_per_100g is not None:
            session.add(
                NutritionProfile(
                    canonical_id=canon.id,
                    source_id=source.id,
                    basis="per_100g",
                    kcal=hit.kcal_per_100g,
                    protein_g=hit.protein_g,
                    carb_g=hit.carb_g,
                    fat_g=hit.fat_g,
                    raw_payload=hit.raw,
                )
            )
            count += 1
    await session.commit()
    return count
