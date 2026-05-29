"""Dış tarif kaynaklarını yerel DB'ye import et (TheMealDB, Spoonacular).

İngilizce kaynak → NVIDIA LLM ile Türkçeye çevrilir (anahtar yoksa İngilizce kalır).
Uyarı: bu kaynaklar uluslararası mutfak; yöresel Türk yemeği değil. Hacim katmanı.
"""

from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..adapters.spoonacular import SpoonacularAdapter
from ..adapters.themealdb import TheMealDbAdapter
from ..models import Recipe, RecipeIngredient, RecipeStepTr, RecipeTag
from .recipe_kcal import compute_recipe_kcal
from .resolver import get_or_create_canonical
from .sources import get_or_create_source
from .text import slugify_tr
from .translate import Translator


def _split_steps(instructions: str) -> list[str]:
    parts = [p.strip() for p in re.split(r"[\r\n]+", instructions) if p.strip()]
    if len(parts) <= 1:
        parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", instructions) if p.strip()]
    return parts[:30]


async def _import_recipe(
    session: AsyncSession,
    *,
    title: str,
    instructions: str,
    area: str | None,
    category: str | None,
    ingredients: list[tuple[str, str]],
    source_id: int,
    translator: Translator,
    do_translate: bool,
) -> bool:
    slug = slugify_tr(title)
    if not slug:
        return False
    exists = (await session.execute(select(Recipe).where(Recipe.slug == slug))).scalar_one_or_none()
    if exists is not None:
        return False

    title_tr = await translator.to_turkish(title) if do_translate else title
    recipe = Recipe(
        slug=slug,
        title_tr=title_tr,
        region=area or "uluslararası",
        source_id=source_id,
        license_mode="atıf",
    )
    session.add(recipe)
    await session.flush()

    for ing, measure in ingredients:
        name_tr = await translator.to_turkish(ing) if do_translate else ing
        canon = await get_or_create_canonical(session, name_tr)
        raw = f"{measure} {name_tr}".strip() if measure else name_tr
        session.add(
            RecipeIngredient(
                recipe_id=recipe.id, canonical_id=canon.id, raw_name=raw, optional=False
            )
        )

    instr = instructions or ""
    if do_translate and instr:
        instr = await translator.to_turkish(instr)
    for i, step in enumerate(_split_steps(instr), start=1):
        session.add(RecipeStepTr(recipe_id=recipe.id, step_no=i, text_tr=step))

    if category:
        tag = (await translator.to_turkish(category) if do_translate else category).lower()
        session.add(RecipeTag(recipe_id=recipe.id, tag=tag[:64]))
    return True


async def _recompute_kcal(session: AsyncSession) -> None:
    recipes = (
        (await session.execute(select(Recipe).where(Recipe.total_kcal.is_(None)))).scalars().all()
    )
    for rc in recipes:
        kcal = await compute_recipe_kcal(session, rc.id)
        if kcal is not None:
            rc.total_kcal = kcal


async def import_themealdb(
    session: AsyncSession, letters: list[str], *, do_translate: bool = True
) -> int:
    adapter = TheMealDbAdapter()
    translator = Translator()
    source = await get_or_create_source(
        session, name="TheMealDB", url="https://www.themealdb.com", license_mode="atıf"
    )
    count = 0
    for letter in letters:
        for meal in await adapter.search_by_letter(letter):
            ok = await _import_recipe(
                session,
                title=meal.get("strMeal", ""),
                instructions=meal.get("strInstructions", ""),
                area=meal.get("strArea"),
                category=meal.get("strCategory"),
                ingredients=TheMealDbAdapter.extract_ingredients(meal),
                source_id=source.id,
                translator=translator,
                do_translate=do_translate,
            )
            if ok:
                count += 1
    await _recompute_kcal(session)
    await session.commit()
    return count


async def import_themealdb_query(
    session: AsyncSession, query_tr: str, *, do_translate: bool = True
) -> int:
    """Canlı arama: Türkçe sorguyu EN'e çevir, TheMealDB'de ada göre ara, idempotent import.

    Çeviri kapalı/anahtarsızsa sorgu olduğu gibi gönderilir (İngilizce arama varsayımı).
    Döner: yeni eklenen tarif sayısı.
    """
    adapter = TheMealDbAdapter()
    translator = Translator()
    query_en = await translator.to_english(query_tr) if do_translate else query_tr
    meals = await adapter.search_by_name(query_en)
    if not meals:
        return 0
    source = await get_or_create_source(
        session, name="TheMealDB", url="https://www.themealdb.com", license_mode="atıf"
    )
    count = 0
    for meal in meals:
        ok = await _import_recipe(
            session,
            title=meal.get("strMeal", ""),
            instructions=meal.get("strInstructions", ""),
            area=meal.get("strArea"),
            category=meal.get("strCategory"),
            ingredients=TheMealDbAdapter.extract_ingredients(meal),
            source_id=source.id,
            translator=translator,
            do_translate=do_translate,
        )
        if ok:
            count += 1
    await _recompute_kcal(session)
    await session.commit()
    return count


async def import_spoonacular(
    session: AsyncSession, query: str, *, number: int = 10, do_translate: bool = True
) -> int:
    adapter = SpoonacularAdapter()
    translator = Translator()
    source = await get_or_create_source(
        session, name="Spoonacular", url="https://spoonacular.com", license_mode="atıf"
    )
    count = 0
    for recipe in await adapter.search(query, number=number):
        instr = recipe.get("instructions") or ""
        instr = re.sub(r"<[^>]+>", " ", instr)  # HTML etiketlerini temizle
        ok = await _import_recipe(
            session,
            title=recipe.get("title", ""),
            instructions=instr,
            area=None,
            category=(recipe.get("dishTypes") or [None])[0],
            ingredients=SpoonacularAdapter.extract_ingredients(recipe),
            source_id=source.id,
            translator=translator,
            do_translate=do_translate,
        )
        if ok:
            count += 1
    await _recompute_kcal(session)
    await session.commit()
    return count
