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
from .services.recipe_kcal import compute_recipe_kcal
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
    # --- Protein (et/balık) ---
    {
        "slug": "tavuk-gogsu",
        "name": "Tavuk göğsü",
        "cat": "protein",
        "aliases": ["tavuk göğsü", "tavuk gogsu", "tavuk"],
        "nutr": (165, 31.0, 0.0, 3.6),
    },
    {
        "slug": "dana-eti",
        "name": "Dana eti",
        "cat": "protein",
        "aliases": ["dana eti", "dana", "kıyma", "dana kıyma"],
        "nutr": (250, 26.0, 0.0, 17.0),
    },
    {
        "slug": "hamsi",
        "name": "Hamsi",
        "cat": "protein",
        "aliases": ["hamsi"],
        "nutr": (96, 16.0, 0.0, 4.0),
    },
    {
        "slug": "levrek",
        "name": "Levrek",
        "cat": "protein",
        "aliases": ["levrek"],
        "nutr": (97, 18.0, 0.0, 2.5),
    },
    # --- Sebze ---
    {
        "slug": "domates",
        "name": "Domates",
        "cat": "sebze",
        "aliases": ["domates"],
        "nutr": (18, 0.9, 3.9, 0.2),
    },
    {
        "slug": "salatalik",
        "name": "Salatalık",
        "cat": "sebze",
        "aliases": ["salatalık", "salatalik"],
        "nutr": (15, 0.7, 3.6, 0.1),
    },
    {
        "slug": "sogan",
        "name": "Soğan",
        "cat": "sebze",
        "aliases": ["soğan", "sogan", "kuru soğan"],
        "nutr": (40, 1.1, 9.0, 0.1),
    },
    {
        "slug": "patates",
        "name": "Patates",
        "cat": "sebze",
        "aliases": ["patates"],
        "nutr": (77, 2.0, 17.0, 0.1),
    },
    {
        "slug": "havuc",
        "name": "Havuç",
        "cat": "sebze",
        "aliases": ["havuç", "havuc"],
        "nutr": (41, 0.9, 9.6, 0.2),
    },
    {
        "slug": "yesil-biber",
        "name": "Yeşil biber",
        "cat": "sebze",
        "aliases": ["yeşil biber", "yesil biber", "biber"],
        "nutr": (20, 0.9, 4.6, 0.2),
    },
    {
        "slug": "marul",
        "name": "Marul",
        "cat": "sebze",
        "aliases": ["marul"],
        "nutr": (15, 1.4, 2.9, 0.2),
    },
    {
        "slug": "sarimsak",
        "name": "Sarımsak",
        "cat": "sebze",
        "aliases": ["sarımsak", "sarimsak"],
        "nutr": (149, 6.0, 33.0, 0.5),
    },
    # --- Meyve ---
    {
        "slug": "elma",
        "name": "Elma",
        "cat": "meyve",
        "aliases": ["elma"],
        "nutr": (52, 0.3, 14.0, 0.2),
    },
    {
        "slug": "muz",
        "name": "Muz",
        "cat": "meyve",
        "aliases": ["muz"],
        "nutr": (89, 1.1, 23.0, 0.3),
    },
    {
        "slug": "portakal",
        "name": "Portakal",
        "cat": "meyve",
        "aliases": ["portakal"],
        "nutr": (47, 0.9, 12.0, 0.1),
    },
    # --- Süt ürünleri ---
    {
        "slug": "yogurt",
        "name": "Yoğurt",
        "cat": "süt",
        "aliases": ["yoğurt", "yogurt", "süzme yoğurt"],
        "nutr": (61, 3.5, 4.7, 3.3),
    },
    {
        "slug": "sut",
        "name": "Süt",
        "cat": "süt",
        "aliases": ["süt", "sut", "tam yağlı süt"],
        "nutr": (61, 3.2, 4.8, 3.3),
    },
    # --- Yağ ---
    {
        "slug": "tereyagi",
        "name": "Tereyağı",
        "cat": "yağ",
        "aliases": ["tereyağı", "tereyagi"],
        "nutr": (717, 0.9, 0.1, 81.0),
    },
    {
        "slug": "zeytinyagi",
        "name": "Zeytinyağı",
        "cat": "yağ",
        "aliases": ["zeytinyağı", "zeytinyagi", "sızma zeytinyağı"],
        "nutr": (884, 0.0, 0.0, 100.0),
    },
    # --- Tahıl / baklagil ---
    {
        "slug": "pirinc",
        "name": "Pirinç",
        "cat": "tahıl",
        "aliases": ["pirinç", "pirinc"],
        "nutr": (130, 2.7, 28.0, 0.3),
    },
    {
        "slug": "bulgur",
        "name": "Bulgur",
        "cat": "tahıl",
        "aliases": ["bulgur", "pilavlık bulgur", "köftelik bulgur"],
        "nutr": (83, 3.0, 19.0, 0.2),
    },
    {
        "slug": "makarna",
        "name": "Makarna",
        "cat": "tahıl",
        "aliases": ["makarna", "spagetti"],
        "nutr": (158, 5.8, 31.0, 0.9),
    },
    {
        "slug": "sehriye",
        "name": "Şehriye",
        "cat": "tahıl",
        "aliases": ["şehriye", "sehriye"],
        "nutr": (158, 5.0, 31.0, 1.0),
    },
    {
        "slug": "kirmizi-mercimek",
        "name": "Kırmızı mercimek",
        "cat": "baklagil",
        "aliases": ["kırmızı mercimek", "kirmizi mercimek", "mercimek"],
        "nutr": (116, 9.0, 20.0, 0.4),
    },
    {
        "slug": "nohut",
        "name": "Nohut",
        "cat": "baklagil",
        "aliases": ["nohut"],
        "nutr": (164, 9.0, 27.0, 2.6),
    },
    # --- Diğer ---
    {
        "slug": "bal",
        "name": "Bal",
        "cat": "tatlandırıcı",
        "aliases": ["bal"],
        "nutr": (304, 0.3, 82.0, 0.0),
    },
    {
        "slug": "ceviz",
        "name": "Ceviz",
        "cat": "kuruyemiş",
        "aliases": ["ceviz"],
        "nutr": (654, 15.0, 14.0, 65.0),
    },
    {
        "slug": "cay",
        "name": "Çay (demli, sade)",
        "cat": "içecek",
        "aliases": ["çay", "cay", "siyah çay"],
        "nutr": (1, 0.0, 0.3, 0.0),
    },
    {
        "slug": "tuz",
        "name": "Tuz",
        "cat": "baharat",
        "aliases": ["tuz"],
        "nutr": (0, 0.0, 0.0, 0.0),
    },
    {
        "slug": "un",
        "name": "Un (buğday)",
        "cat": "tahıl",
        "aliases": ["un", "buğday unu"],
        "nutr": (364, 10.0, 76.0, 1.0),
    },
    {
        "slug": "nane",
        "name": "Nane",
        "cat": "baharat",
        "aliases": ["nane", "kuru nane"],
        "nutr": (70, 3.7, 14.9, 0.9),
    },
    {
        "slug": "domates-salcasi",
        "name": "Domates salçası",
        "cat": "konserve",
        "aliases": ["domates salçası", "domates salcasi", "salça"],
        "nutr": (82, 4.3, 18.0, 0.5),
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
    {
        "slug": "izmir-koftesi",
        "title": "İzmir Köftesi",
        "servings": 4,
        "region": "ege",
        "ingredients": [
            ("dana eti", 500, "gram", False),
            ("patates", 3, "adet", False),
            ("domates", 2, "adet", False),
            ("soğan", 1, "adet", True),
            ("yeşil biber", 2, "adet", True),
            ("un", 2, "yemek kaşığı", True),
            ("yumurta", 1, "adet", True),
            ("tuz", None, None, True),
        ],
        "steps": ["Köfte harcını yoğur.", "Patates ve sebzelerle fırınla."],
        "tags": ["ana yemek", "protein"],
    },
    {
        "slug": "ezogelin-corbasi",
        "title": "Ezogelin Çorbası",
        "servings": 4,
        "region": "güneydoğu",
        "ingredients": [
            ("kırmızı mercimek", 1, "su bardağı", False),
            ("bulgur", 2, "yemek kaşığı", True),
            ("pirinç", 2, "yemek kaşığı", True),
            ("soğan", 1, "adet", True),
            ("domates salçası", 1, "yemek kaşığı", True),
            ("nane", None, None, True),
            ("tuz", None, None, True),
        ],
        "steps": ["Mercimek, bulgur ve pirinci kaynat.", "Salça/nane ile tatlandır."],
        "tags": ["çorba", "vejetaryen"],
    },
    {
        "slug": "kisir",
        "title": "Kısır",
        "servings": 4,
        "region": "güneydoğu",
        "ingredients": [
            ("bulgur", 2, "su bardağı", False),
            ("domates salçası", 2, "yemek kaşığı", True),
            ("soğan", 1, "adet", True),
            ("yeşil biber", 2, "adet", True),
            ("nane", None, None, True),
            ("zeytinyağı", 3, "yemek kaşığı", True),
            ("tuz", None, None, True),
        ],
        "steps": ["Bulguru sıcak suyla ıslat.", "Salça ve sebzelerle yoğur."],
        "tags": ["meze", "vejetaryen"],
    },
    {
        "slug": "omlet",
        "title": "Omlet",
        "servings": 1,
        "region": "genel",
        "ingredients": [
            ("yumurta", 2, "adet", False),
            ("tereyağı", 1, "yemek kaşığı", True),
            ("beyaz peynir", 30, "gram", True),
            ("tuz", None, None, True),
        ],
        "steps": ["Yumurtayı çırp.", "Tavada tereyağıyla pişir."],
        "tags": ["kahvaltı", "protein"],
    },
    {
        "slug": "coban-salatasi",
        "title": "Çoban Salatası",
        "servings": 2,
        "region": "genel",
        "ingredients": [
            ("domates", 2, "adet", False),
            ("salatalık", 1, "adet", False),
            ("soğan", 1, "adet", True),
            ("yeşil biber", 1, "adet", True),
            ("zeytinyağı", 2, "yemek kaşığı", True),
            ("tuz", None, None, True),
        ],
        "steps": ["Sebzeleri küp doğra.", "Zeytinyağı ve tuzla harmanla."],
        "tags": ["salata", "vejetaryen"],
    },
    {
        "slug": "haslanmis-tavuk",
        "title": "Haşlanmış Tavuk",
        "servings": 2,
        "region": "genel",
        "ingredients": [
            ("tavuk göğsü", 300, "gram", False),
            ("havuç", 1, "adet", True),
            ("tuz", None, None, True),
        ],
        "steps": ["Tavuğu havuçla 25-30 dk haşla.", "Soğumadan dilimle."],
        "tags": ["protein", "ana yemek"],
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

    # Recipe toplam kalorisini hesapla (canonical + nutrition + birim → gram).
    all_recipes = (await session.execute(select(Recipe))).scalars().all()
    for rc in all_recipes:
        if rc.total_kcal is None:
            kcal = await compute_recipe_kcal(session, rc.id)
            if kcal is not None:
                rc.total_kcal = kcal
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
