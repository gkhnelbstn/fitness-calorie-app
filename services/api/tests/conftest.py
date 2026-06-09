"""Test fixture'ları — izole DB, dependency override, seed, LLM kapatma.

Seed hızı: `seed_all` ağır (yüzlerce tarif + per-tarif besin hesabı). Test başına
çalıştırmak yerine oturum başına BİR kez seed'li bir şablon DB kuruyoruz; seed'e
ihtiyaç duyan her test bu dosyanın hızlı bir kopyasını alıyor (tam izolasyon korunur,
seed yalnız 1 kez koşar). Boş DB bekleyen unit testler `engine`/`session` ile devam eder.
"""

from __future__ import annotations

import asyncio
import os
import shutil

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app import config
from app.db import Base, enable_sqlite_fk, get_session
from app.main import app
from app.seeds import seed_all


@pytest.fixture(autouse=True, scope="session")
def _disable_real_llm():
    """Testlerde gerçek NVIDIA çağrısı olmasın → kurallı parser'a düşsün.

    Açık LLM testi kendi _key'ini set edip respx ile mock'lar.
    """
    os.environ["NVIDIA_API_KEY"] = ""
    config.get_settings.cache_clear()
    yield
    config.get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _reset_settings_cache():
    """Her testten sonra ayar önbelleğini temizle (env override izolasyonu)."""
    yield
    config.get_settings.cache_clear()


@pytest.fixture(scope="session")
def _seed_template(tmp_path_factory):
    """Oturum başına bir kez seed'li şablon sqlite dosyası kur; testler kopyalar."""
    db_path = tmp_path_factory.mktemp("seed_tpl") / "template.db"

    async def _build() -> None:
        eng = create_async_engine(f"sqlite+aiosqlite:///{db_path.as_posix()}")
        enable_sqlite_fk(eng)
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with async_sessionmaker(eng, expire_on_commit=False)() as s:
            await seed_all(s)
        await eng.dispose()

    asyncio.run(_build())
    return db_path


# --------------------------------------------------------------------------- #
# Boş (seed'siz) DB — model/birim gibi unit testler için
# --------------------------------------------------------------------------- #
@pytest_asyncio.fixture
async def engine(tmp_path):
    eng = create_async_engine(f"sqlite+aiosqlite:///{tmp_path.as_posix()}/t.db")
    enable_sqlite_fk(eng)  # FK cascade'i zorla (prod ile aynı davranış)
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


# --------------------------------------------------------------------------- #
# Seed'li DB — şablonun hızlı kopyası (her test kendi kopyası, izole)
# --------------------------------------------------------------------------- #
@pytest_asyncio.fixture
async def seeded_engine(tmp_path, _seed_template):
    db = tmp_path / "seeded.db"
    shutil.copyfile(_seed_template, db)
    eng = create_async_engine(f"sqlite+aiosqlite:///{db.as_posix()}")
    enable_sqlite_fk(eng)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def seeded_maker(seeded_engine):
    return async_sessionmaker(seeded_engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def seeded_session(seeded_maker):
    async with seeded_maker() as s:
        yield s


@pytest_asyncio.fixture
async def client(seeded_maker):
    async def _override():
        async with seeded_maker() as s:
            yield s

    app.dependency_overrides[get_session] = _override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth():
    return {"Authorization": f"Bearer {config.get_settings().api_token}"}
