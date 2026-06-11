"""Günlük özet — alınan kalori/makro toplamı (Faz 1, intake servisini kullanır).

Sağlık verisi (aktif kalori, net denge) Faz 4'te eklenecek.
"""

from __future__ import annotations

from datetime import date as date_cls

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import CurrentUser, get_current_profile, get_current_user
from ..db import get_session
from ..schemas.summary import DailySummary
from ..services.intake import daily_intake

router = APIRouter(
    prefix="/api/summary", tags=["summary"], dependencies=[Depends(get_current_user)]
)


@router.get("", response_model=DailySummary)
async def daily_summary(
    date: str | None = None,
    cu: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> DailySummary:
    day = date or date_cls.today().isoformat()
    user = await get_current_profile(cu, session)
    intake = await daily_intake(session, user.id, day)
    return DailySummary(
        day=day,
        intake_kcal=intake.kcal,
        protein_g=intake.protein_g,
        carb_g=intake.carb_g,
        fat_g=intake.fat_g,
        meal_count=intake.meal_count,
        item_count=intake.item_count,
    )
