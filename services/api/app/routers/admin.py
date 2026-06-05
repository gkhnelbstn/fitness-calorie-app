"""Admin import endpoint'leri — dış kaynaklardan tarif/besin yükleme.

Token korumalı. Dış API'lere çıkar; lokal/manuel kullanım içindir.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..adapters.spoonacular import SpoonacularAdapter
from ..db import get_session
from ..security import require_token
from ..services.food_import import import_usda
from ..services.recipe_import import import_spoonacular, import_themealdb
from ..services.wger_import import import_wger_turkish

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_token)])


@router.post("/import/themealdb")
async def import_tmdb(
    letters: str = Query(default="a", description="Çekilecek baş harfler, ör: abc"),
    translate: bool = Query(default=True),
    session: AsyncSession = Depends(get_session),
) -> dict:
    uniq = list(dict.fromkeys(c for c in letters.lower() if c.isalpha()))
    if not uniq:
        raise HTTPException(status_code=422, detail="Geçerli harf yok.")
    n = await import_themealdb(session, uniq, do_translate=translate)
    return {"imported": n, "letters": uniq}


@router.post("/import/usda")
async def import_usda_ep(
    query: str = Query(..., description="Aranacak besin, ör: rice"),
    translate: bool = Query(default=True),
    session: AsyncSession = Depends(get_session),
) -> dict:
    n = await import_usda(session, query, do_translate=translate)
    return {"imported": n, "query": query}


@router.post("/import/spoonacular")
async def import_spoon_ep(
    query: str = Query(..., description="Tarif arama, ör: soup"),
    number: int = Query(default=10, ge=1, le=100),
    translate: bool = Query(default=True),
    session: AsyncSession = Depends(get_session),
) -> dict:
    if not SpoonacularAdapter().enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Spoonacular anahtarı yok (.env: SPOONACULAR_API_KEY).",
        )
    n = await import_spoonacular(session, query, number=number, do_translate=translate)
    return {"imported": n, "query": query}


@router.post("/import/wger-tr")
async def import_wger_tr_ep(
    limit: int = Query(default=200, ge=1, le=2500, description="Çekilecek Türkçe besin sayısı"),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """wger Türkçe besinleri (language=16, OFF kaynaklı) içe al → canonical + nutrition."""
    n = await import_wger_turkish(session, limit=limit)
    return {"imported": n, "source": "wger", "limit": limit}
