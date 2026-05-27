"""Async SQLAlchemy motoru, oturum ve Base."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=settings.debug, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    """Tüm ORM modellerinin ortak temeli."""


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — istek başına bir oturum."""
    async with SessionLocal() as session:
        yield session
