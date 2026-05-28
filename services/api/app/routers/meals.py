"""Yemek kaydı endpoint'leri (Faz 1 — gerçek persistence).

POST: raw_text → LLM/kurallı ayrıştırma → canonical eşleştirme → besin değeri → DB.
GET:  tarihe göre kullanıcının yemek kayıtları.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..adapters.openfoodfacts import OpenFoodFactsAdapter
from ..db import get_session
from ..models import FoodProduct, MealLog, MealLogItem, NutritionProfile
from ..schemas.meal import BarcodeMealCreate, MealCreate, MealItem, MealRead
from ..security import require_token
from ..services.extract import extract_items
from ..services.meal_parser import ParsedItem
from ..services.nutrition import resolve_nutrition
from ..services.resolver import get_or_create_canonical, resolve_canonical
from ..services.sources import get_or_create_source
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


def _scale(value: float | None, grams: float) -> float | None:
    if value is None:
        return None
    return round(value * grams / 100.0, 1)


@router.post("/by-barcode", response_model=MealRead, status_code=status.HTTP_201_CREATED)
async def create_meal_by_barcode(
    payload: BarcodeMealCreate, session: AsyncSession = Depends(get_session)
) -> MealRead:
    """Barkodu Open Food Facts'ten çek, ürün/canonical/besin profilini upsert et,
    miktar ile makro hesapla ve yemek kaydı oluştur."""
    hit = await OpenFoodFactsAdapter().by_barcode(payload.barcode)
    if hit is None:
        raise HTTPException(status_code=404, detail="Barkod bulunamadı.")

    user = await get_or_create_default_user(session)
    src = await get_or_create_source(
        session,
        name="Open Food Facts",
        url="https://world.openfoodfacts.org",
        license="ODbL",
        license_mode="atıf",
    )

    # FoodProduct upsert
    product = (
        await session.execute(select(FoodProduct).where(FoodProduct.barcode == payload.barcode))
    ).scalar_one_or_none()
    canon = await get_or_create_canonical(session, hit.name)
    if product is None:
        product = FoodProduct(
            barcode=payload.barcode,
            name=hit.name,
            canonical_id=canon.id,
            source_id=src.id,
            raw_payload=hit.raw,
        )
        session.add(product)
    elif product.canonical_id is None:
        product.canonical_id = canon.id

    # NutritionProfile upsert
    has_np = (
        await session.execute(
            select(NutritionProfile.id).where(NutritionProfile.canonical_id == canon.id)
        )
    ).first()
    if has_np is None and hit.kcal_per_100g is not None:
        session.add(
            NutritionProfile(
                canonical_id=canon.id,
                source_id=src.id,
                basis="per_100g",
                kcal=hit.kcal_per_100g,
                protein_g=hit.protein_g,
                carb_g=hit.carb_g,
                fat_g=hit.fat_g,
                raw_payload=hit.raw,
            )
        )

    grams = payload.grams
    log = MealLog(
        user_id=user.id,
        meal_type=payload.meal_type,
        raw_text=f"[barkod {payload.barcode}] {hit.name}",
    )
    session.add(log)
    await session.flush()
    item = MealLogItem(
        meal_log_id=log.id,
        canonical_id=canon.id,
        raw_name=hit.name,
        quantity=grams,
        unit="gram",
        kcal=_scale(hit.kcal_per_100g, grams),
        protein_g=_scale(hit.protein_g, grams),
        carb_g=_scale(hit.carb_g, grams),
        fat_g=_scale(hit.fat_g, grams),
        confidence=1.0,
    )
    session.add(item)
    log.total_kcal = item.kcal
    await session.commit()

    return MealRead(
        id=log.id,
        eaten_at=log.eaten_at,
        meal_type=log.meal_type,
        raw_text=log.raw_text,
        total_kcal=log.total_kcal,
        items=[_to_schema_item(item)],
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
