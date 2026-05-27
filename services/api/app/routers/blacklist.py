"""Kara liste endpoint'leri."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..schemas.blacklist import BlacklistAdd, BlacklistItem
from ..security import require_token
from ..services import blacklist as bl
from ..services.user import get_or_create_default_user

router = APIRouter(
    prefix="/api/blacklist", tags=["blacklist"], dependencies=[Depends(require_token)]
)


@router.post("", response_model=BlacklistItem, status_code=status.HTTP_201_CREATED)
async def add_item(
    payload: BlacklistAdd, session: AsyncSession = Depends(get_session)
) -> BlacklistItem:
    user = await get_or_create_default_user(session)
    canon = await bl.add_blacklist(session, user.id, payload.name)
    if canon is None:
        raise HTTPException(status_code=422, detail="Geçersiz malzeme adı.")
    return BlacklistItem(canonical_id=canon.id, slug=canon.slug, name_tr=canon.name_tr)


@router.get("", response_model=list[BlacklistItem])
async def list_items(session: AsyncSession = Depends(get_session)) -> list[BlacklistItem]:
    user = await get_or_create_default_user(session)
    rows = await bl.list_blacklist(session, user.id)
    return [BlacklistItem(canonical_id=c.id, slug=c.slug, name_tr=c.name_tr) for c in rows]


@router.delete("/{canonical_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item(canonical_id: int, session: AsyncSession = Depends(get_session)) -> None:
    user = await get_or_create_default_user(session)
    removed = await bl.remove_blacklist(session, user.id, canonical_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Kara listede yok.")
