"""Tarif endpoint'leri (Faz 2 — blacklist filtresi + adaptasyon + cook-with)."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import CurrentUser, get_current_profile, get_current_user
from ..db import get_session
from ..schemas.recipe import RecipeRead
from ..services.blacklist import blacklist_ids
from ..services.recipe_import import import_themealdb_query
from ..services.recipes import cook_with, search_recipes
from ..services.resolver import resolve_canonical

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/api/recipes", tags=["recipes"], dependencies=[Depends(get_current_user)]
)


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
    category: str | None = Query(default=None, description="Kategori filtresi (çorba, ana yemek…)"),
    exclude: list[str] = Query(default_factory=list, description="İstenmeyen malzemeler"),
    limit: int = Query(default=24, ge=1, le=100, description="Sayfa boyutu"),
    offset: int = Query(default=0, ge=0, description="Atlanacak kayıt"),
    live: bool = Query(default=False, description="Web'de ara: TheMealDB'den canlı çek + içe al"),
    cu: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[RecipeRead]:
    user = await get_current_profile(cu, session)
    # Canlı arama: q'yu EN'e çevir, TheMealDB'den çek, idempotent içe al (dedup),
    # sonra yereli (artık zenginleşmiş) sorgula. İlk sayfada (offset 0) tetiklenir.
    if live and q and q.strip() and offset == 0:
        try:
            await import_themealdb_query(session, q.strip())
        except Exception:  # canlı kaynak hatası aramayı bozmasın
            logger.warning("Canlı tarif aramada hata (q=%s)", q, exc_info=True)
    blocked = await blacklist_ids(session, user.id)
    blocked |= await _names_to_ids(session, exclude)
    return await search_recipes(session, q, blocked, category=category, limit=limit, offset=offset)


@router.get("/cook-with", response_model=list[RecipeRead])
async def cook(
    have: list[str] = Query(default_factory=list, description="Elindeki malzemeler"),
    exclude: list[str] = Query(default_factory=list, description="İstenmeyen malzemeler"),
    cu: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[RecipeRead]:
    user = await get_current_profile(cu, session)
    blocked = await blacklist_ids(session, user.id)
    blocked |= await _names_to_ids(session, exclude)
    have_ids = await _names_to_ids(session, have)
    return await cook_with(session, have_ids, blocked)
