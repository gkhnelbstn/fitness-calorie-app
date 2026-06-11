"""PostgreSQL uyumluluk smoke testleri.

Yalnız CI'daki Postgres service job'unda koşar (PG_TEST_URL set edilir);
lokalde/normal suite'te atlanır. Amaç: SQLite'a özgü SQL (func.date gibi)
regresyonlarını gerçek Postgres'te yakalamak.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db import Base
from app.models import MealLog, MealLogItem, UserProfile
from app.services.intake import daily_intake

PG_URL = os.environ.get("PG_TEST_URL", "")

pytestmark = pytest.mark.skipif(not PG_URL, reason="PG_TEST_URL yok (yalnız CI Postgres job)")


async def test_pg_daily_intake_date_filter() -> None:
    """Tarih filtresi (eski func.date) Postgres'te çalışmalı."""
    eng = create_async_engine(PG_URL)
    try:
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        maker = async_sessionmaker(eng, expire_on_commit=False)
        async with maker() as s:
            user = UserProfile(name="pg-smoke")
            s.add(user)
            await s.flush()
            now = datetime.now(UTC)
            log = MealLog(user_id=user.id, eaten_at=now, raw_text="pg smoke")
            s.add(log)
            await s.flush()
            s.add(MealLogItem(meal_log_id=log.id, raw_name="elma", kcal=52.0))
            await s.commit()

            intake = await daily_intake(s, user.id, now.date().isoformat())
            assert intake.meal_count == 1
            assert intake.kcal == 52.0

            # başka gün → boş
            empty = await daily_intake(s, user.id, "2000-01-01")
            assert empty.meal_count == 0
    finally:
        await eng.dispose()
