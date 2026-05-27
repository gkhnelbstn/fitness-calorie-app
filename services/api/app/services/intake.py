"""Günlük besin alımı toplamı (meal_log + meal_log_item)."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import MealLog, MealLogItem


@dataclass
class Intake:
    kcal: float = 0.0
    protein_g: float = 0.0
    carb_g: float = 0.0
    fat_g: float = 0.0
    meal_count: int = 0
    item_count: int = 0


async def daily_intake(session: AsyncSession, user_id: int, day: str) -> Intake:
    log_ids = (
        (
            await session.execute(
                select(MealLog.id)
                .where(MealLog.user_id == user_id)
                .where(func.date(MealLog.eaten_at) == day)
            )
        )
        .scalars()
        .all()
    )

    if not log_ids:
        return Intake()

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

    return Intake(
        kcal=round(agg[0], 1),
        protein_g=round(agg[1], 1),
        carb_g=round(agg[2], 1),
        fat_g=round(agg[3], 1),
        meal_count=len(log_ids),
        item_count=agg[4],
    )
