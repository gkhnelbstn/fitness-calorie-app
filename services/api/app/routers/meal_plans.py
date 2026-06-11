"""Yemek planı endpoint'leri — markdown formatlı plan parse + apply."""

from __future__ import annotations

from datetime import UTC, datetime, time, timedelta
from datetime import date as date_cls

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import CurrentUser, get_current_profile, get_current_user
from ..db import get_session
from ..models import MealLog
from ..schemas.meal_plan import (
    PlanApplyRequest,
    PlanApplyResponse,
    PlanEntryRead,
    PlanPreviewRequest,
    PlanPreviewResponse,
)
from ..services.extract import extract_items
from ..services.meal_items import build_meal_log_item
from ..services.meal_plan import parse_plan

router = APIRouter(
    prefix="/api/meal-plans", tags=["meal-plans"], dependencies=[Depends(get_current_user)]
)


@router.post("/preview", response_model=PlanPreviewResponse)
async def preview(payload: PlanPreviewRequest) -> PlanPreviewResponse:
    entries = [
        PlanEntryRead(day_offset=e.day_offset, meal_type=e.meal_type, raw_text=e.raw_text)
        for e in parse_plan(payload.text)
    ]
    return PlanPreviewResponse(entries=entries)


@router.post("/apply", response_model=PlanApplyResponse)
async def apply(
    payload: PlanApplyRequest,
    cu: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> PlanApplyResponse:
    user = await get_current_profile(cu, session)
    parsed = parse_plan(payload.text)
    base = date_cls.fromisoformat(payload.base_date) if payload.base_date else date_cls.today()
    created_ids: list[int] = []

    for entry in parsed:
        eaten_at = datetime.combine(
            base + timedelta(days=entry.day_offset), time(12, 0), tzinfo=UTC
        )
        log = MealLog(
            user_id=user.id,
            meal_type=entry.meal_type,
            raw_text=entry.raw_text,
            eaten_at=eaten_at,
        )
        session.add(log)
        await session.flush()

        items = []
        for p in await extract_items(entry.raw_text):
            item = await build_meal_log_item(session, p)
            item.meal_log_id = log.id
            session.add(item)
            items.append(item)
        log.total_kcal = sum((it.kcal or 0) for it in items) or None
        created_ids.append(log.id)

    await session.commit()
    return PlanApplyResponse(
        base_date=base.isoformat(),
        created_meal_ids=created_ids,
        entries=[
            PlanEntryRead(day_offset=e.day_offset, meal_type=e.meal_type, raw_text=e.raw_text)
            for e in parsed
        ],
    )
