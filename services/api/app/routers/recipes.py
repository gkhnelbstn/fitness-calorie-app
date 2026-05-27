"""Tarif endpoint'leri (Faz 2 — blacklist filtresi + adaptasyon + cook-with)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..schemas.recipe import RecipeRead
from ..security import require_token
from ..services.blacklist import blacklist_ids
from ..services.recipes import cook_with, search_recipes
from ..services.resolver import resolve_canonical
from ..services.user import get_or_create_default_user

router = APIRouter(prefix="/api/recipes", tags=["recipes"], dependencies=[Depends(require_token)])


async def _names_to_ids(session: AsyncSession, names: list[str]) -> set[int]:
    ids: set[int] = set()
    for n in names:
        canon = await resolve_canonical(session, n)
        if canon is not None:
            ids.add(canon.id)
    return ids


@router.get("", response_model=list[RecipeRead])
async def search(
    q: str | None = Query(default=None, description="Başlık arama"),
    exclude: list[str] = Query(default_factory=list, description="İstenmeyen malzemeler"),
    session: AsyncSession = Depends(get_session),
) -> list[RecipeRead]:
    user = await get_or_create_default_user(session)
    blocked = await blacklist_ids(session, user.id)
    blocked |= await _names_to_ids(session, exclude)
    return await search_recipes(session, q, blocked)


@router.get("/cook-with", response_model=list[RecipeRead])
async def cook(
    have: list[str] = Query(default_factory=list, description="Elindeki malzemeler"),
    exclude: list[str] = Query(default_factory=list, description="İstenmeyen malzemeler"),
    session: AsyncSession = Depends(get_session),
) -> list[RecipeRead]:
    user = await get_or_create_default_user(session)
    blocked = await blacklist_ids(session, user.id)
    blocked |= await _names_to_ids(session, exclude)
    have_ids = await _names_to_ids(session, have)
    return await cook_with(session, have_ids, blocked)
