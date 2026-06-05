"""wger Türkçe besinlerini içe aktar → IngredientCanonical + NutritionProfile.

İsimler zaten Türkçe (çeviri yok). Idempotent: var olan canonical/nutrition'a dokunmaz.
Öğün loglama besin kapsamını büyütür (resolver tam-eşleşme ile bu adlara erişir).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..adapters.wger import WgerAdapter
from ..models import NutritionProfile
from .resolver import get_or_create_canonical
from .sources import get_or_create_source


async def import_wger_turkish(session: AsyncSession, *, limit: int = 200) -> int:
    """wger Türkçe besinleri → canonical + nutrition. Yeni nutrition sayısını döner."""
    adapter = WgerAdapter()
    source = await get_or_create_source(
        session,
        name="wger",
        url="https://wger.de",
        license="OFF/ODbL",
        license_mode="atıf",
    )
    count = 0
    for hit in await adapter.turkish_ingredients(limit=limit):
        canon = await get_or_create_canonical(session, hit["name"])
        exists = (
            await session.execute(
                select(NutritionProfile.id).where(NutritionProfile.canonical_id == canon.id)
            )
        ).first()
        if exists is None:
            session.add(
                NutritionProfile(
                    canonical_id=canon.id,
                    source_id=source.id,
                    basis="per_100g",
                    kcal=hit["kcal"],
                    protein_g=hit["protein_g"],
                    carb_g=hit["carb_g"],
                    fat_g=hit["fat_g"],
                    raw_payload={"code": hit.get("code")},
                )
            )
            count += 1
    await session.commit()
    return count
