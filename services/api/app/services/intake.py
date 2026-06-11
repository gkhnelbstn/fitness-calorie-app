"""Günlük besin alımı toplamı (meal_log + meal_log_item)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from datetime import date as date_cls

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import MealLog, MealLogItem


def day_bounds(day: str) -> tuple[datetime, datetime]:
    """'YYYY-MM-DD' → [gün başı, ertesi gün başı) UTC aralığı.

    func.date() SQLite'a özgü (PostgreSQL'de yok); aralık karşılaştırması
    her iki dialect'te çalışır ve index kullanır.
    """
    d = date_cls.fromisoformat(day)
    start = datetime(d.year, d.month, d.day, tzinfo=UTC)
    return start, start + timedelta(days=1)


@dataclass
class Intake:
    kcal: float = 0.0
    protein_g: float = 0.0
    carb_g: float = 0.0
    fat_g: float = 0.0
    meal_count: int = 0
    item_count: int = 0


async def daily_intake(session: AsyncSession, user_id: int, day: str) -> Intake:
    start, end = day_bounds(day)
    log_ids = (
        (
            await session.execute(
                select(MealLog.id)
                .where(MealLog.user_id == user_id)
                .where(MealLog.eaten_at >= start, MealLog.eaten_at < end)
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
