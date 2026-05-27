"""Canonical malzeme çözümleyici — Türkçe ad/alias → IngredientCanonical."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import IngredientAliasTr, IngredientCanonical
from .text import normalize_tr


async def resolve_canonical(session: AsyncSession, name: str) -> IngredientCanonical | None:
    norm = normalize_tr(name)
    if not norm:
        return None

    # 1) Alias tam eşleşme
    alias = (
        await session.execute(select(IngredientAliasTr).where(IngredientAliasTr.alias == norm))
    ).scalar_one_or_none()
    if alias is not None:
        return await session.get(IngredientCanonical, alias.canonical_id)

    # 2) Canonical adı (normalize) eşleşme
    canon = (
        await session.execute(
            select(IngredientCanonical).where(func.lower(IngredientCanonical.name_tr) == norm)
        )
    ).scalar_one_or_none()
    return canon
