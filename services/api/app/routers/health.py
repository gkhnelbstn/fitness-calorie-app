"""Sağlık/liveness endpoint'i (auth gerektirmez)."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..db import get_session

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health")
async def health(session: AsyncSession = Depends(get_session)) -> dict:
    """Liveness + hafif DB ping.

    DB ping'i keepalive cron'unun Supabase'i de aktif tutması için (free tier
    ~7 gün hareketsizlikte duraklar). DB hatası servisi unhealthy yapmaz
    (Render health check restart döngüsüne girmesin) — alanda raporlanır.
    """
    settings = get_settings()
    db = "ok"
    try:
        await session.execute(text("SELECT 1"))
    except Exception:  # pragma: no cover - bağlantı kesintisi
        logger.exception("Health DB ping başarısız")
        db = "error"
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
        "llm_enabled": settings.llm_enabled,
        "db": db,
    }
