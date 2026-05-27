"""Yemek kaydı endpoint'leri (Faz 1 — gerçek persistence).

POST: raw_text → LLM/kurallı ayrıştırma → canonical eşleştirme → besin değeri → DB.
GET:  tarihe göre kullanıcının yemek kayıtları.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import MealLog, MealLogItem
from ..schemas.meal import MealCreate, MealItem, MealRead
from ..security import require_token
from ..services.extract import extract_items
from ..services.meal_parser import ParsedItem
from ..services.nutrition import resolve_nutrition
from ..services.resolver import resolve_canonical
from ..services.units import resolve_grams
from ..services.user import get_or_create_default_user

router = APIRouter(prefix="/api/meals", tags=["meals"], dependencies=[Depends(require_token)])


async def _build_item(session: AsyncSession, p: ParsedItem) -> MealLogItem:
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


def _to_schema_item(it: MealLogItem) -> MealItem:
    return MealItem(
        raw_name=it.raw_name,
        quantity=it.quantity,
        unit=it.unit,
        canonical_id=it.canonical_id,
        kcal=it.kcal,
        protein_g=it.protein_g,
        carb_g=it.carb_g,
        fat_g=it.fat_g,
        confidence=it.confidence,
    )


@router.post("", response_model=MealRead, status_code=status.HTTP_201_CREATED)
async def create_meal(
    payload: MealCreate, session: AsyncSession = Depends(get_session)
) -> MealRead:
    if not payload.raw_text and not payload.items:
        raise HTTPException(status_code=422, detail="raw_text veya items dolu olmalı.")

    user = await get_or_create_default_user(session)

    log = MealLog(user_id=user.id, meal_type=payload.meal_type, raw_text=payload.raw_text)
    session.add(log)
    await session.flush()

    items: list[MealLogItem] = []
    if payload.raw_text:
        for p in await extract_items(payload.raw_text):
            items.append(await _build_item(session, p))
    else:
        for i in payload.items:
            if i.kcal is not None:
                # Kullanıcı kaloriyi açıkça verdi (ör. barkod/manuel) → onurla.
                canon = await resolve_canonical(session, i.raw_name)
                items.append(
                    MealLogItem(
                        canonical_id=canon.id if canon else None,
                        raw_name=i.raw_name,
                        quantity=i.quantity,
                        unit=i.unit,
                        kcal=i.kcal,
                        protein_g=i.protein_g,
                        carb_g=i.carb_g,
                        fat_g=i.fat_g,
                        confidence=1.0,
                    )
                )
            else:
                items.append(await _build_item(session, ParsedItem(i.raw_name, i.quantity, i.unit)))

    for item in items:
        item.meal_log_id = log.id
        session.add(item)

    total = sum((it.kcal or 0) for it in items) or None
    log.total_kcal = total
    await session.commit()

    return MealRead(
        id=log.id,
        eaten_at=log.eaten_at,
        meal_type=log.meal_type,
        raw_text=log.raw_text,
        total_kcal=total,
        items=[_to_schema_item(it) for it in items],
    )


@router.get("", response_model=list[MealRead])
async def list_meals(
    date: str | None = None, session: AsyncSession = Depends(get_session)
) -> list[MealRead]:
    user = await get_or_create_default_user(session)
    stmt = select(MealLog).where(MealLog.user_id == user.id)
    if date:
        stmt = stmt.where(func.date(MealLog.eaten_at) == date)
    stmt = stmt.order_by(MealLog.eaten_at.desc())

    logs = (await session.execute(stmt)).scalars().all()
    out: list[MealRead] = []
    for log in logs:
        rows = (
            (await session.execute(select(MealLogItem).where(MealLogItem.meal_log_id == log.id)))
            .scalars()
            .all()
        )
        out.append(
            MealRead(
                id=log.id,
                eaten_at=log.eaten_at,
                meal_type=log.meal_type,
                raw_text=log.raw_text,
                total_kcal=log.total_kcal,
                items=[_to_schema_item(it) for it in rows],
            )
        )
    return out
