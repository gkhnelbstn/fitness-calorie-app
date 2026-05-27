"""Günlük özet — alınan kalori/makro toplamı (Faz 1).

Sağlık verisi (aktif kalori, net denge) Faz 4'te eklenecek.
"""

from __future__ import annotations

from datetime import date as date_cls

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import MealLog, MealLogItem
from ..schemas.summary import DailySummary
from ..security import require_token
from ..services.user import get_or_create_default_user

router = APIRouter(prefix="/api/summary", tags=["summary"], dependencies=[Depends(require_token)])


@router.get("", response_model=DailySummary)
async def daily_summary(
    date: str | None = None, session: AsyncSession = Depends(get_session)
) -> DailySummary:
    day = date or date_cls.today().isoformat()
    user = await get_or_create_default_user(session)

    log_ids_stmt = (
        select(MealLog.id)
        .where(MealLog.user_id == user.id)
        .where(func.date(MealLog.eaten_at) == day)
    )
    log_ids = [r for r in (await session.execute(log_ids_stmt)).scalars().all()]

    if not log_ids:
        return DailySummary(
            day=day, intake_kcal=0, protein_g=0, carb_g=0, fat_g=0, meal_count=0, item_count=0
        )

    agg = (
        await session.execute(
            select(
                func.coalesce(func.sum(MealLogItem.kcal), 0.0),
                func.coalesce(func.sum(MealLogItem.protein_g), 0.0),
                func.coalesce(func.sum(MealLogItem.carb_g), 0.0),
                func.coalesce(func.sum(MealLogItem.fat_g), 0.0),
                func.count(MealLogItem.id),
            ).where(MealLogItem.meal_log_id.in_(log_ids))
        )
    ).one()

    return DailySummary(
        day=day,
        intake_kcal=round(agg[0], 1),
        protein_g=round(agg[1], 1),
        carb_g=round(agg[2], 1),
        fat_g=round(agg[3], 1),
        meal_count=len(log_ids),
        item_count=agg[4],
    )
