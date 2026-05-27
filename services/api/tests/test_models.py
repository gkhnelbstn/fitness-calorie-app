"""DB modelleri + oturum — şema oluşur, kayıt eklenir/okunur."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app import models
from app.db import Base, get_session


@pytest.fixture
async def session():
    # İzole bellek-içi DB (dev.db'ye dokunmaz)
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as s:
        yield s
    await engine.dispose()


async def test_user_insert_and_read(session) -> None:
    session.add(models.UserProfile(name="gokhan", locale="tr"))
    await session.commit()
    res = await session.execute(select(models.UserProfile))
    user = res.scalars().first()
    assert user is not None
    assert user.name == "gokhan"
    assert user.created_at is not None  # TimestampMixin default çalışır


async def test_recipe_with_ingredient(session) -> None:
    r = models.Recipe(slug="mercimek-corbasi", title_tr="Mercimek Çorbası")
    session.add(r)
    await session.flush()
    session.add(
        models.RecipeIngredient(
            recipe_id=r.id, raw_name="kırmızı mercimek", quantity=1, unit="su bardağı"
        )
    )
    await session.commit()
    res = await session.execute(select(models.RecipeIngredient))
    ing = res.scalars().first()
    assert ing is not None
    assert ing.recipe_id == r.id


async def test_get_session_dependency() -> None:
    agen = get_session()
    sess = await agen.__anext__()
    assert sess is not None
    await agen.aclose()
