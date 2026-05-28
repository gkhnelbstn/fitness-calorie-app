"""Yemek satırı oluşturma — ParsedItem'dan DB MealLogItem'a çevir.

Tekil mantık (resolver + units + nutrition); birden çok router paylaşır.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import MealLogItem
from .meal_parser import ParsedItem
from .nutrition import resolve_nutrition
from .resolver import resolve_canonical
from .units import resolve_grams


async def build_meal_log_item(session: AsyncSession, p: ParsedItem) -> MealLogItem:
    canon = await resolve_canonical(session, p.name)
    grams = resolve_grams(p.quantity, p.unit)
    macros = None
    if canon is not None and grams is not None:
        macros = await resolve_nutrition(session, canon.id, grams)

    if canon is not None and macros is not None:
        confidence = 1.0
    elif canon is not None:
        confidence = 0.5
    else:
        confidence = 0.2

    return MealLogItem(
        canonical_id=canon.id if canon else None,
        raw_name=p.name,
        quantity=p.quantity,
        unit=p.unit,
        kcal=macros.kcal if macros else None,
        protein_g=macros.protein_g if macros else None,
        carb_g=macros.carb_g if macros else None,
        fat_g=macros.fat_g if macros else None,
        confidence=confidence,
    )
