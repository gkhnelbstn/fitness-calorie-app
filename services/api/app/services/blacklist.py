"""Kara liste — kullanıcının istemediği malzemeler (canonical)."""

from __future__ import annotations

from typing import Any, cast

from sqlalchemy import delete, select
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import IngredientBlacklist, IngredientCanonical
from .resolver import get_or_create_canonical


async def add_blacklist(
    session: AsyncSession, user_id: int, name: str
) -> IngredientCanonical | None:
    if not name.strip():
        return None
    canon = await get_or_create_canonical(session, name)
    exists = (
        await session.execute(
            select(IngredientBlacklist.id).where(
                IngredientBlacklist.user_id == user_id,
                IngredientBlacklist.canonical_id == canon.id,
            )
        )
    ).first()
    if exists is None:
        session.add(IngredientBlacklist(user_id=user_id, canonical_id=canon.id))
        await session.commit()
    return canon


async def list_blacklist(session: AsyncSession, user_id: int) -> list[IngredientCanonical]:
    rows = (
        (
            await session.execute(
                select(IngredientCanonical)
                .join(
                    IngredientBlacklist, IngredientBlacklist.canonical_id == IngredientCanonical.id
                )
                .where(IngredientBlacklist.user_id == user_id)
                .order_by(IngredientCanonical.name_tr)
            )
        )
        .scalars()
        .all()
    )
    return list(rows)


async def remove_blacklist(session: AsyncSession, user_id: int, canonical_id: int) -> bool:
    result = await session.execute(
        delete(IngredientBlacklist).where(
            IngredientBlacklist.user_id == user_id,
            IngredientBlacklist.canonical_id == canonical_id,
        )
    )
    await session.commit()
    return cast("CursorResult[Any]", result).rowcount > 0


async def blacklist_ids(session: AsyncSession, user_id: int) -> set[int]:
    rows = (
        (
            await session.execute(
                select(IngredientBlacklist.canonical_id).where(
                    IngredientBlacklist.user_id == user_id
                )
            )
        )
        .scalars()
        .all()
    )
    return set(rows)
