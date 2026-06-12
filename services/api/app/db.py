"""Async SQLAlchemy motoru, oturum ve Base."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings

settings = get_settings()


def enable_sqlite_fk(async_engine: AsyncEngine) -> None:
    """SQLite'ta her bağlantıda foreign key zorlamasını aç.

    SQLite varsayılan olarak FK'leri ZORLAMAZ; pragma olmadan ondelete=CASCADE
    çalışmaz → silinen üst kaydın çocukları (ör. MealLogItem) yetim kalır ve
    SQLite id'yi tekrar kullanınca yeni kayda yapışır. Bu pragma onu engeller.
    """

    @event.listens_for(async_engine.sync_engine, "connect")
    def _set_pragma(dbapi_conn: Any, _rec: Any) -> None:  # pragma: no cover (event)
        if "sqlite" in type(dbapi_conn).__module__:
            cur = dbapi_conn.cursor()
            cur.execute("PRAGMA foreign_keys=ON")
            cur.close()


def _engine_kwargs(url: str) -> dict[str, Any]:
    """Postgres (asyncpg) için Supabase SSL.

    Supabase SSL zorunlu kılar; asyncpg `ssl` connect-arg ister (URL'de sslmode
    asyncpg'de çalışmaz). Session pooler kullanılır → prepared statement güvenli.
    """
    if url.startswith("postgresql+asyncpg"):
        return {"connect_args": {"ssl": "require"}, "pool_pre_ping": True}
    return {}


engine = create_async_engine(
    settings.database_url, echo=settings.debug, future=True, **_engine_kwargs(settings.database_url)
)
if engine.dialect.name == "sqlite":
    enable_sqlite_fk(engine)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    """Tüm ORM modellerinin ortak temeli."""


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — istek başına bir oturum."""
    async with SessionLocal() as session:
        yield session
