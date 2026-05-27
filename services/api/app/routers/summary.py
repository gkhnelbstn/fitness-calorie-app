"""Günlük özet — alınan kalori/makro toplamı (Faz 1, intake servisini kullanır).

Sağlık verisi (aktif kalori, net denge) Faz 4'te eklenecek.
"""

from __future__ import annotations

from datetime import date as date_cls

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..schemas.summary import DailySummary
from ..security import require_token
from ..services.intake import daily_intake
from ..services.user import get_or_create_default_user

router = APIRouter(prefix="/api/summary", tags=["summary"], dependencies=[Depends(require_token)])


@router.get("", response_model=DailySummary)
async def daily_summary(
    date: str | None = None, session: AsyncSession = Depends(get_session)
) -> DailySummary:
    day = date or date_cls.today().isoformat()
    user = await get_or_create_default_user(session)
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
