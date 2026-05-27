"""Canonical resolver + besin çözümleme (seed'li izole DB)."""

from app.services.nutrition import resolve_nutrition
from app.services.resolver import resolve_canonical


async def test_alias_match(seeded_session) -> None:
    canon = await resolve_canonical(seeded_session, "fasulye")
    assert canon is not None
    assert canon.slug == "kuru-fasulye"


async def test_name_match_case_insensitive(seeded_session) -> None:
    canon = await resolve_canonical(seeded_session, "Ayran")
    assert canon is not None
    assert canon.slug == "ayran"


async def test_unknown_returns_none(seeded_session) -> None:
    assert await resolve_canonical(seeded_session, "ejderha meyvesi") is None


async def test_empty_returns_none(seeded_session) -> None:
    assert await resolve_canonical(seeded_session, "   ") is None


async def test_nutrition_scaled(seeded_session) -> None:
    canon = await resolve_canonical(seeded_session, "ayran")
    assert canon is not None
    macros = await resolve_nutrition(seeded_session, canon.id, 200)  # 1 bardak
    assert macros is not None
    assert macros.kcal == 80.0  # 40 kcal/100g * 200g


async def test_nutrition_missing_profile(seeded_session) -> None:
    assert await resolve_nutrition(seeded_session, 999999, 100) is None
