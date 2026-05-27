"""Tarif endpoint'leri (Faz 0 stub).

Faz 2'de: yerel katalog + blacklist hard filter + ikame kural motoru.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ..schemas.recipe import RecipeRead
from ..security import require_token

router = APIRouter(prefix="/api/recipes", tags=["recipes"], dependencies=[Depends(require_token)])


@router.get("", response_model=list[RecipeRead])
async def search_recipes(
    q: str | None = Query(default=None, description="Arama metni"),
    exclude: list[str] = Query(default_factory=list, description="İstenmeyen malzemeler"),
) -> list[RecipeRead]:
    # TODO(Faz 2): yerel DB araması + blacklist filtresi + ikame motoru.
    return []
