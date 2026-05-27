"""Test fixture'ları — izole DB, dependency override, seed, LLM kapatma."""

from __future__ import annotations

import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app import config
from app.db import Base, get_session
from app.main import app
from app.seeds import seed_basic


@pytest.fixture(autouse=True, scope="session")
def _disable_real_llm():
    """Testlerde gerçek NVIDIA çağrısı olmasın → kurallı parser'a düşsün.

    Açık LLM testi kendi _key'ini set edip respx ile mock'lar.
    """
    os.environ["NVIDIA_API_KEY"] = ""
    config.get_settings.cache_clear()
    yield
    config.get_settings.cache_clear()


@pytest_asyncio.fixture
async def engine(tmp_path):
    eng = create_async_engine(f"sqlite+aiosqlite:///{tmp_path.as_posix()}/t.db")
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def maker(engine):
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def session(maker):
    async with maker() as s:
        yield s


@pytest_asyncio.fixture
async def seeded_session(session):
    await seed_basic(session)
    return session


@pytest_asyncio.fixture
async def client(maker):
    async def _override():
        async with maker() as s:
            yield s

    async with maker() as s:
        await seed_basic(s)

    app.dependency_overrides[get_session] = _override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth():
    return {"Authorization": f"Bearer {config.get_settings().api_token}"}
