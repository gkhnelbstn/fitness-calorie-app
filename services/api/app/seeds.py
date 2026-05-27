"""Başlangıç Türkçe besin tohumu (seed). Offline demo + test için.

Kaynak placeholder: TurKomp (TÜBİTAK) + manuel. Gerçek değerler ileride
TurKomp'tan seçili çekilip doğrulanacak; buradakiler yaklaşık per_100g.

Idempotent: tekrar çalıştırınca kayıt çoğaltmaz.
CLI: `uv run python -m app.seeds`
"""

from __future__ import annotations

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    IngredientAliasTr,
    IngredientCanonical,
    NutritionProfile,
    Recipe,
    RecipeIngredient,
    RecipeStepTr,
    RecipeTag,
    SourceAttribution,
)
from .services.resolver import get_or_create_canonical
from .services.text import normalize_tr

# (slug, ad, kategori, aliasler, per_100g: kcal/protein/carb/fat)
SEED: list[dict] = [
    {
        "slug": "simit",
        "name": "Simit",
        "cat": "fırın",
        "aliases": ["simit", "gevrek"],
        "nutr": (330, 9.0, 60.0, 5.0),
    },
    {
        "slug": "beyaz-peynir",
        "name": "Beyaz peynir",
        "cat": "süt",
        "aliases": ["beyaz peynir", "peynir"],
        "nutr": (260, 17.0, 2.0, 21.0),
    },
    {
        "slug": "ayran",
        "name": "Ayran",
        "cat": "içecek",
        "aliases": ["ayran"],
        "nutr": (40, 1.7, 3.0, 2.0),
    },
    {
        "slug": "yumurta",
        "name": "Yumurta",
        "cat": "protein",
        "aliases": ["yumurta", "haşlanmış yumurta", "haslanmis yumurta"],
        "nutr": (155, 13.0, 1.1, 11.0),
    },
    {
        "slug": "pirinc-pilavi",
        "name": "Pirinç pilavı",
        "cat": "tahıl",
        "aliases": ["pilav", "pirinç pilavı", "pirinc pilavi"],
        "nutr": (130, 2.7, 28.0, 0.3),
    },
    {
        "slug": "kuru-fasulye",
        "name": "Kuru fasulye",
        "cat": "baklagil",
        "aliases": ["kuru fasulye", "fasulye"],
        "nutr": (120, 7.0, 20.0, 1.0),
    },
    {
        "slug": "tam-bugday-ekmegi",
        "name": "Tam buğday ekmeği",
        "cat": "fırın",
        "aliases": ["tam buğday ekmeği", "tam bugday ekmegi"],
        "nutr": (250, 9.0, 43.0, 3.0),
    },
]


async def _get_source(session: AsyncSession) -> SourceAttribution:
    src = (
        await session.execute(select(SourceAttribution).where(SourceAttribution.name == "TurKomp"))
    ).scalar_one_or_none()
    if src is None:
        src = SourceAttribution(
            name="TurKomp",
            url="https://turkomp.tarimorman.gov.tr",
            license="atıf-gerekli",
            license_mode="seçili-çek",
        )
        session.add(src)
        await session.flush()
    return src


async def seed_basic(session: AsyncSession) -> int:
    """Çekirdek malzemeleri ekler (idempotent). Eklenen yeni canonical sayısını döner."""
    src = await _get_source(session)
    added = 0
    for row in SEED:
        canon = (
            await session.execute(
                select(IngredientCanonical).where(IngredientCanonical.slug == row["slug"])
            )
        ).scalar_one_or_none()
        if canon is None:
            canon = IngredientCanonical(slug=row["slug"], name_tr=row["name"], category=row["cat"])
            session.add(canon)
            await session.flush()
            added += 1

        # Besin profili (yoksa)
        has_profile = (
            await session.execute(
                select(NutritionProfile.id).where(NutritionProfile.canonical_id == canon.id)
            )
        ).first()
        if has_profile is None:
            kcal, protein, carb, fat = row["nutr"]
            session.add(
                NutritionProfile(
                    canonical_id=canon.id,
                    source_id=src.id,
                    basis="per_100g",
                    kcal=kcal,
                    protein_g=protein,
                    carb_g=carb,
                    fat_g=fat,
                )
            )

        # Aliasler (normalize, yoksa)
        for raw_alias in row["aliases"]:
            alias = normalize_tr(raw_alias)
            exists = (
                await session.execute(
                    select(IngredientAliasTr.id).where(IngredientAliasTr.alias == alias)
                )
            ).first()
            if exists is None:
                session.add(IngredientAliasTr(canonical_id=canon.id, alias=alias))

    await session.commit()
    return added


# Tarif: (slug, başlık, porsiyon, bölge, malzemeler[(ad,miktar,birim,optional)], adımlar, etiketler)
RECIPES: list[dict] = [
    {
        "slug": "mercimek-corbasi",
        "title": "Mercimek Çorbası",
        "servings": 4,
        "region": "genel",
        "ingredients": [
            ("kırmızı mercimek", 1, "su bardağı", False),
            ("soğan", 1, "adet", True),
            ("havuç", 1, "adet", True),
            ("un", 1, "yemek kaşığı", True),
            ("tuz", None, None, True),
        ],
        "steps": ["Sebzeleri doğra.", "Mercimek ve suyla kaynat.", "Blenderdan geçir, baharatla."],
        "tags": ["çorba", "vejetaryen"],
    },
    {
        "slug": "menemen",
        "title": "Menemen",
        "servings": 2,
        "region": "genel",
        "ingredients": [
            ("yumurta", 3, "adet", False),
            ("domates", 2, "adet", False),
            ("yeşil biber", 2, "adet", True),
            ("soğan", 1, "adet", True),
            ("tereyağı", 1, "yemek kaşığı", True),
        ],
        "steps": ["Biber ve domatesi kavur.", "Yumurtayı kır, karıştır."],
        "tags": ["kahvaltı"],
    },
    {
        "slug": "cacik",
        "title": "Cacık",
        "servings": 4,
        "region": "genel",
        "ingredients": [
            ("yoğurt", 2, "su bardağı", False),
            ("salatalık", 1, "adet", False),
            ("sarımsak", 1, "diş", True),
            ("nane", None, None, True),
        ],
        "steps": ["Salatalığı rendele.", "Yoğurt, su ve sarımsakla karıştır."],
        "tags": ["meze", "vejetaryen"],
    },
    {
        "slug": "kuru-fasulye-yemegi",
        "title": "Kuru Fasulye Yemeği",
        "servings": 4,
        "region": "genel",
        "ingredients": [
            ("kuru fasulye", 2, "su bardağı", False),
            ("soğan", 1, "adet", True),
            ("domates salçası", 1, "yemek kaşığı", True),
            ("zeytinyağı", 2, "yemek kaşığı", True),
        ],
        "steps": ["Fasulyeyi haşla.", "Soğan ve salçayla pişir."],
        "tags": ["ana yemek"],
    },
    {
        "slug": "pirinc-pilavi-tarif",
        "title": "Pirinç Pilavı",
        "servings": 4,
        "region": "genel",
        "ingredients": [
            ("pirinç", 1, "su bardağı", False),
            ("tereyağı", 1, "yemek kaşığı", True),
            ("şehriye", 2, "yemek kaşığı", True),
            ("tuz", None, None, True),
        ],
        "steps": ["Şehriyeyi kavur.", "Pirinç ve suyla pişir."],
        "tags": ["garnitür"],
    },
    {
        "slug": "haslanmis-yumurta",
        "title": "Haşlanmış Yumurta",
        "servings": 1,
        "region": "genel",
        "ingredients": [
            ("yumurta", 2, "adet", False),
            ("tuz", None, None, True),
        ],
        "steps": ["Yumurtayı 8-10 dk haşla."],
        "tags": ["kahvaltı", "protein"],
    },
]


async def seed_recipes(session: AsyncSession) -> int:
    """Çekirdek tarifleri ekler (idempotent). Eklenen tarif sayısını döner."""
    added = 0
    for row in RECIPES:
        exists = (
            await session.execute(select(Recipe).where(Recipe.slug == row["slug"]))
        ).scalar_one_or_none()
        if exists is not None:
            continue
        recipe = Recipe(
            slug=row["slug"],
            title_tr=row["title"],
            servings=row["servings"],
            region=row["region"],
            is_adaptable=True,
        )
        session.add(recipe)
        await session.flush()
        for name, qty, unit, optional in row["ingredients"]:
            canon = await get_or_create_canonical(session, name)
            session.add(
                RecipeIngredient(
                    recipe_id=recipe.id,
                    canonical_id=canon.id,
                    raw_name=name,
                    quantity=qty,
                    unit=unit,
                    optional=optional,
                )
            )
        for i, text in enumerate(row["steps"], start=1):
            session.add(RecipeStepTr(recipe_id=recipe.id, step_no=i, text_tr=text))
        for tag in row["tags"]:
            session.add(RecipeTag(recipe_id=recipe.id, tag=tag))
        added += 1
    await session.commit()
    return added


async def seed_all(session: AsyncSession) -> tuple[int, int]:
    ingredients = await seed_basic(session)
    recipes = await seed_recipes(session)
    return ingredients, recipes


async def _run() -> None:
    from .db import SessionLocal

    async with SessionLocal() as session:
        ing, rec = await seed_all(session)
        print(f"Seed tamam. Yeni canonical: {ing}, yeni tarif: {rec}")


if __name__ == "__main__":
    asyncio.run(_run())
