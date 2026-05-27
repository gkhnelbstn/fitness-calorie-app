"""Sağlık/liveness endpoint'i (auth gerektirmez)."""

from __future__ import annotations

from fastapi import APIRouter

from ..config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
        "llm_enabled": settings.llm_enabled,
    }
