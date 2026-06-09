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

from .data.ingredients_tr import EXTRA_SEED
from .data.recipes_phase3 import EXTRA_RECIPES3
from .data.recipes_tr import EXTRA_RECIPES
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
from .services.recipe_kcal import compute_recipe_macros
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
    # --- Gündelik / hazır yemekler (sık loglanan; per_100g yaklaşık) ---
    # Doğal dille öğün girişinde en çok yazılan yemekler. Çorbalar ve hazır
    # yemekler tabak/kâse ağırlığıyla (units.py) gerçekçi kaloriye dönüşür.
    {
        "slug": "ekmek",
        "name": "Ekmek",
        "cat": "fırın",
        "aliases": ["ekmek", "beyaz ekmek", "somun ekmek"],
        "nutr": (265, 9.0, 49.0, 3.2),
    },
    {
        "slug": "pogaca",
        "name": "Poğaça",
        "cat": "fırın",
        "aliases": ["poğaça", "pogaca"],
        "nutr": (330, 7.0, 38.0, 16.0),
    },
    {
        "slug": "borek",
        "name": "Börek",
        "cat": "fırın",
        "aliases": ["börek", "borek", "su böreği", "sigara böreği", "peynirli börek"],
        "nutr": (280, 8.0, 27.0, 16.0),
    },
    {
        "slug": "mercimek-corbasi",
        "name": "Mercimek çorbası",
        "cat": "çorba",
        "aliases": ["mercimek çorbası", "mercimek corbasi"],
        "nutr": (55, 3.0, 9.0, 1.0),
    },
    {
        "slug": "ezogelin-corbasi",
        "name": "Ezogelin çorbası",
        "cat": "çorba",
        "aliases": ["ezogelin çorbası", "ezogelin corbasi", "ezogelin", "ezo gelin çorbası"],
        "nutr": (60, 3.0, 10.0, 1.2),
    },
    {
        "slug": "tavuk-corbasi",
        "name": "Tavuk çorbası",
        "cat": "çorba",
        "aliases": ["tavuk çorbası", "tavuk corbasi"],
        "nutr": (48, 4.0, 4.0, 1.8),
    },
    {
        "slug": "domates-corbasi",
        "name": "Domates çorbası",
        "cat": "çorba",
        "aliases": ["domates çorbası", "domates corbasi"],
        "nutr": (52, 1.5, 7.0, 2.2),
    },
    {
        "slug": "kofte",
        "name": "Köfte",
        "cat": "et yemeği",
        "aliases": ["köfte", "kofte", "izgara köfte", "ızgara köfte"],
        "nutr": (290, 18.0, 5.0, 22.0),
    },
    {
        "slug": "et-doner",
        "name": "Et döner",
        "cat": "et yemeği",
        "aliases": ["et döner", "döner", "doner"],
        "nutr": (215, 20.0, 3.0, 14.0),
    },
    {
        "slug": "tavuk-doner",
        "name": "Tavuk döner",
        "cat": "et yemeği",
        "aliases": ["tavuk döner", "tavuk doner"],
        "nutr": (190, 22.0, 2.0, 10.0),
    },
    {
        "slug": "durum",
        "name": "Dürüm",
        "cat": "et yemeği",
        "aliases": ["dürüm", "durum", "tavuk dürüm", "et dürüm"],
        "nutr": (230, 14.0, 28.0, 7.0),
    },
    {
        "slug": "lahmacun",
        "name": "Lahmacun",
        "cat": "hamur işi",
        "aliases": ["lahmacun"],
        "nutr": (230, 11.0, 32.0, 7.0),
    },
    {
        "slug": "pide",
        "name": "Pide",
        "cat": "hamur işi",
        "aliases": ["pide", "kıymalı pide", "kaşarlı pide"],
        "nutr": (270, 11.0, 40.0, 8.0),
    },
    {
        "slug": "hamburger",
        "name": "Hamburger",
        "cat": "fast food",
        "aliases": ["hamburger", "burger"],
        "nutr": (250, 12.0, 28.0, 11.0),
    },
    {
        "slug": "pizza",
        "name": "Pizza",
        "cat": "fast food",
        "aliases": ["pizza"],
        "nutr": (266, 11.0, 33.0, 10.0),
    },
    {
        "slug": "patates-kizartmasi",
        "name": "Patates kızartması",
        "cat": "fast food",
        "aliases": ["patates kızartması", "patates kizartmasi", "kızartma", "parmak patates"],
        "nutr": (312, 3.4, 41.0, 15.0),
    },
    {
        "slug": "sucuk",
        "name": "Sucuk",
        "cat": "şarküteri",
        "aliases": ["sucuk"],
        "nutr": (430, 22.0, 2.0, 38.0),
    },
    {
        "slug": "menemen",
        "name": "Menemen",
        "cat": "kahvaltı",
        "aliases": ["menemen"],
        "nutr": (130, 7.0, 5.0, 9.0),
    },
    {
        "slug": "omlet",
        "name": "Omlet",
        "cat": "kahvaltı",
        "aliases": ["omlet", "omlett"],
        "nutr": (155, 11.0, 1.5, 12.0),
    },
    {
        "slug": "kasar-peyniri",
        "name": "Kaşar peyniri",
        "cat": "süt",
        "aliases": ["kaşar", "kaşar peyniri", "kasar", "kasar peyniri"],
        "nutr": (350, 25.0, 2.0, 27.0),
    },
    {
        "slug": "zeytin",
        "name": "Zeytin",
        "cat": "kahvaltı",
        "aliases": ["zeytin", "siyah zeytin", "yeşil zeytin"],
        "nutr": (130, 1.0, 6.0, 11.0),
    },
    {
        "slug": "cacik",
        "name": "Cacık",
        "cat": "meze",
        "aliases": ["cacık", "cacik"],
        "nutr": (50, 2.5, 4.0, 2.5),
    },
    {
        "slug": "mevsim-salata",
        "name": "Mevsim salata",
        "cat": "salata",
        "aliases": ["salata", "mevsim salata", "çoban salata", "çoban salatası", "mevsim salatası"],
        "nutr": (35, 1.2, 5.0, 1.5),
    },
    {
        "slug": "yulaf-ezmesi",
        "name": "Yulaf ezmesi",
        "cat": "tahıl",
        "aliases": ["yulaf", "yulaf ezmesi"],
        "nutr": (380, 13.0, 67.0, 7.0),
    },
    {
        "slug": "kahve",
        "name": "Kahve",
        "cat": "içecek",
        "aliases": ["kahve", "türk kahvesi", "turk kahvesi", "filtre kahve", "sade kahve"],
        "nutr": (2, 0.1, 0.3, 0.0),
    },
    {
        "slug": "baklava",
        "name": "Baklava",
        "cat": "tatlı",
        "aliases": ["baklava"],
        "nutr": (430, 6.0, 50.0, 24.0),
    },
    {
        "slug": "sutlac",
        "name": "Sütlaç",
        "cat": "tatlı",
        "aliases": ["sütlaç", "sutlac"],
        "nutr": (130, 3.5, 22.0, 3.0),
    },
    {
        "slug": "cikolata",
        "name": "Çikolata",
        "cat": "tatlı",
        "aliases": ["çikolata", "cikolata"],
        "nutr": (535, 7.0, 59.0, 30.0),
    },
    {
        "slug": "kola",
        "name": "Kola",
        "cat": "içecek",
        "aliases": ["kola", "gazlı içecek", "gazoz"],
        "nutr": (42, 0.0, 10.6, 0.0),
    },
]

# Küratör ek malzemeler (app/data/ingredients_tr.py)
SEED.extend(EXTRA_SEED)


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
    # --- Geniş Türkçe set ---
    {
        "slug": "yayla-corbasi",
        "title": "Yayla Çorbası",
        "servings": 4,
        "region": "iç anadolu",
        "ingredients": [
            ("yoğurt", 1, "su bardağı", False),
            ("pirinç", 3, "yemek kaşığı", False),
            ("un", 1, "yemek kaşığı", True),
            ("yumurta", 1, "adet", True),
            ("nane", None, None, True),
            ("tuz", None, None, True),
        ],
        "steps": [
            "Pirinci haşla.",
            "Yoğurt-un-yumurta terbiyesini ekle.",
            "Nane yağıyla servis et.",
        ],
        "tags": ["çorba", "vejetaryen"],
    },
    {
        "slug": "tarhana-corbasi",
        "title": "Tarhana Çorbası",
        "servings": 4,
        "region": "ege",
        "ingredients": [
            ("tarhana", 4, "yemek kaşığı", False),
            ("domates salçası", 1, "yemek kaşığı", True),
            ("tereyağı", 1, "yemek kaşığı", True),
            ("tuz", None, None, True),
        ],
        "steps": ["Tarhanayı suyla aç.", "Salça ve yağ ekleyip kaynat."],
        "tags": ["çorba"],
    },
    {
        "slug": "domates-corbasi",
        "title": "Domates Çorbası",
        "servings": 4,
        "region": "genel",
        "ingredients": [
            ("domates", 4, "adet", False),
            ("un", 2, "yemek kaşığı", True),
            ("tereyağı", 1, "yemek kaşığı", True),
            ("beyaz peynir", 30, "gram", True),
            ("tuz", None, None, True),
        ],
        "steps": ["Unu yağda kavur.", "Rendelenmiş domatesi ekle, kaynat.", "Peynirle servis et."],
        "tags": ["çorba", "vejetaryen"],
    },
    {
        "slug": "menemen-sucuklu",
        "title": "Sucuklu Menemen",
        "servings": 2,
        "region": "genel",
        "ingredients": [
            ("yumurta", 3, "adet", False),
            ("domates", 2, "adet", False),
            ("sucuk", 60, "gram", True),
            ("yeşil biber", 2, "adet", True),
            ("tuz", None, None, True),
        ],
        "steps": ["Sucuğu kavur.", "Biber-domates ekle.", "Yumurtayı kır, karıştır."],
        "tags": ["kahvaltı", "protein"],
    },
    {
        "slug": "sigara-boregi",
        "title": "Sigara Böreği",
        "servings": 4,
        "region": "genel",
        "ingredients": [
            ("yufka", 4, "adet", False),
            ("beyaz peynir", 200, "gram", False),
            ("maydanoz", None, None, True),
            ("ayçiçek yağı", 1, "su bardağı", True),
        ],
        "steps": ["Peynir-maydanozu yufkaya sar.", "Kızgın yağda kızart."],
        "tags": ["meze", "kızartma"],
    },
    {
        "slug": "zeytinyagli-fasulye",
        "title": "Zeytinyağlı Taze Fasulye",
        "servings": 4,
        "region": "ege",
        "ingredients": [
            ("taze fasulye", 500, "gram", False),
            ("soğan", 1, "adet", True),
            ("domates", 1, "adet", True),
            ("zeytinyağı", 4, "yemek kaşığı", True),
            ("tuz", None, None, True),
        ],
        "steps": [
            "Soğanı kavur.",
            "Fasulye ve domatesi ekle.",
            "Kısık ateşte pişir, soğuk servis et.",
        ],
        "tags": ["zeytinyağlı", "vejetaryen"],
    },
    {
        "slug": "imam-bayildi",
        "title": "İmam Bayıldı",
        "servings": 4,
        "region": "marmara",
        "ingredients": [
            ("patlıcan", 4, "adet", False),
            ("soğan", 2, "adet", False),
            ("domates", 2, "adet", True),
            ("sarımsak", 2, "diş", True),
            ("zeytinyağı", 5, "yemek kaşığı", True),
        ],
        "steps": [
            "Patlıcanları közle/soy.",
            "Soğan-domates iç harcı hazırla.",
            "Doldurup fırınla.",
        ],
        "tags": ["zeytinyağlı", "vejetaryen"],
    },
    {
        "slug": "karniyarik",
        "title": "Karnıyarık",
        "servings": 4,
        "region": "genel",
        "ingredients": [
            ("patlıcan", 4, "adet", False),
            ("dana eti", 250, "gram", False),
            ("soğan", 1, "adet", True),
            ("domates", 2, "adet", True),
            ("yeşil biber", 4, "adet", True),
        ],
        "steps": ["Patlıcanları kızart.", "Kıymalı harç yap.", "Doldurup fırınla."],
        "tags": ["ana yemek", "protein"],
    },
    {
        "slug": "etli-nohut",
        "title": "Etli Nohut",
        "servings": 4,
        "region": "genel",
        "ingredients": [
            ("nohut", 2, "su bardağı", False),
            ("dana eti", 250, "gram", False),
            ("soğan", 1, "adet", True),
            ("domates salçası", 1, "yemek kaşığı", True),
        ],
        "steps": ["Nohutu haşla.", "Eti soğanla kavur.", "Salça ve nohutla pişir."],
        "tags": ["ana yemek", "protein"],
    },
    {
        "slug": "kuru-fasulye-pilav",
        "title": "Kuru Fasulye & Pilav",
        "servings": 4,
        "region": "genel",
        "ingredients": [
            ("kuru fasulye", 2, "su bardağı", False),
            ("pirinç", 1, "su bardağı", False),
            ("soğan", 1, "adet", True),
            ("domates salçası", 1, "yemek kaşığı", True),
        ],
        "steps": ["Fasulyeyi pişir.", "Pilavı demle.", "Birlikte servis et."],
        "tags": ["ana yemek"],
    },
    {
        "slug": "mantı",
        "title": "Mantı",
        "servings": 4,
        "region": "iç anadolu",
        "ingredients": [
            ("un", 3, "su bardağı", False),
            ("dana eti", 200, "gram", False),
            ("soğan", 1, "adet", True),
            ("yoğurt", 2, "su bardağı", True),
            ("sarımsak", 2, "diş", True),
        ],
        "steps": ["Hamuru aç, kıymayla doldur.", "Haşla.", "Sarımsaklı yoğurt ve sosla servis et."],
        "tags": ["hamur işi", "ana yemek"],
    },
    {
        "slug": "lahmacun",
        "title": "Lahmacun",
        "servings": 4,
        "region": "güneydoğu",
        "ingredients": [
            ("un", 3, "su bardağı", False),
            ("dana eti", 200, "gram", False),
            ("domates", 2, "adet", True),
            ("soğan", 1, "adet", True),
            ("maydanoz", None, None, True),
        ],
        "steps": ["Hamuru aç.", "Kıymalı harcı yay.", "Yüksek ısıda pişir."],
        "tags": ["hamur işi"],
    },
    {
        "slug": "pide-kiymali",
        "title": "Kıymalı Pide",
        "servings": 4,
        "region": "karadeniz",
        "ingredients": [
            ("un", 3, "su bardağı", False),
            ("dana eti", 200, "gram", False),
            ("soğan", 1, "adet", True),
            ("yumurta", 1, "adet", True),
        ],
        "steps": ["Hamuru kayık şekli ver.", "Kıymalı harcı koy.", "Fırınla."],
        "tags": ["hamur işi"],
    },
    {
        "slug": "pilav-ustu-tavuk",
        "title": "Pilav Üstü Tavuk",
        "servings": 2,
        "region": "genel",
        "ingredients": [
            ("pirinç", 1, "su bardağı", False),
            ("tavuk göğsü", 200, "gram", False),
            ("tereyağı", 1, "yemek kaşığı", True),
        ],
        "steps": ["Pilavı demle.", "Tavuğu haşla/doğra.", "Pilav üstüne koy."],
        "tags": ["ana yemek", "protein"],
    },
    {
        "slug": "izgara-kofte",
        "title": "Izgara Köfte",
        "servings": 4,
        "region": "genel",
        "ingredients": [
            ("dana eti", 500, "gram", False),
            ("soğan", 1, "adet", True),
            ("ekmek içi", 1, "dilim", True),
            ("tuz", None, None, True),
            ("yumurta", 1, "adet", True),
        ],
        "steps": ["Harcı yoğur, dinlendir.", "Şekillendir.", "Izgarada pişir."],
        "tags": ["protein", "ızgara"],
    },
    {
        "slug": "tavuk-sote",
        "title": "Tavuk Sote",
        "servings": 3,
        "region": "genel",
        "ingredients": [
            ("tavuk göğsü", 400, "gram", False),
            ("yeşil biber", 2, "adet", True),
            ("domates", 2, "adet", True),
            ("soğan", 1, "adet", True),
            ("zeytinyağı", 2, "yemek kaşığı", True),
        ],
        "steps": ["Tavuğu kavur.", "Sebzeleri ekle.", "Suyunu çekene dek pişir."],
        "tags": ["ana yemek", "protein"],
    },
    {
        "slug": "firinda-somon",
        "title": "Fırında Somon",
        "servings": 2,
        "region": "genel",
        "ingredients": [
            ("somon", 300, "gram", False),
            ("limon", 1, "adet", True),
            ("zeytinyağı", 2, "yemek kaşığı", True),
            ("tuz", None, None, True),
        ],
        "steps": ["Somonu baharatla.", "Limon-yağ gezdir.", "Fırında 18-20 dk pişir."],
        "tags": ["protein", "balık"],
    },
    {
        "slug": "mercimek-corbasi-klasik",
        "title": "Süzme Mercimek Çorbası",
        "servings": 4,
        "region": "genel",
        "ingredients": [
            ("kırmızı mercimek", 1, "su bardağı", False),
            ("patates", 1, "adet", True),
            ("havuç", 1, "adet", True),
            ("soğan", 1, "adet", True),
            ("tereyağı", 1, "yemek kaşığı", True),
        ],
        "steps": ["Sebze+mercimeği haşla.", "Blenderdan geçir.", "Tereyağı-pul biberle servis."],
        "tags": ["çorba", "vejetaryen"],
    },
    {
        "slug": "yogurtlu-makarna",
        "title": "Yoğurtlu Makarna",
        "servings": 3,
        "region": "genel",
        "ingredients": [
            ("makarna", 250, "gram", False),
            ("yoğurt", 2, "su bardağı", False),
            ("sarımsak", 1, "diş", True),
            ("tereyağı", 1, "yemek kaşığı", True),
        ],
        "steps": ["Makarnayı haşla.", "Sarımsaklı yoğurt ve kızgın yağla karıştır."],
        "tags": ["hamur işi", "vejetaryen"],
    },
    {
        "slug": "menemensiz-omlet-peynirli",
        "title": "Peynirli Omlet",
        "servings": 1,
        "region": "genel",
        "ingredients": [
            ("yumurta", 3, "adet", False),
            ("beyaz peynir", 40, "gram", True),
            ("tereyağı", 1, "yemek kaşığı", True),
        ],
        "steps": ["Yumurtayı çırp.", "Peynirle tavada pişir."],
        "tags": ["kahvaltı", "protein"],
    },
    {
        "slug": "havuc-tarator",
        "title": "Havuç Tarator",
        "servings": 4,
        "region": "genel",
        "ingredients": [
            ("havuç", 3, "adet", False),
            ("yoğurt", 1, "su bardağı", False),
            ("sarımsak", 1, "diş", True),
            ("zeytinyağı", 1, "yemek kaşığı", True),
        ],
        "steps": ["Havucu rendele, yağda soteleyip soğut.", "Sarımsaklı yoğurtla karıştır."],
        "tags": ["meze", "vejetaryen"],
    },
    {
        "slug": "patates-salatasi",
        "title": "Patates Salatası",
        "servings": 4,
        "region": "genel",
        "ingredients": [
            ("patates", 4, "adet", False),
            ("soğan", 1, "adet", True),
            ("maydanoz", None, None, True),
            ("zeytinyağı", 3, "yemek kaşığı", True),
            ("limon", 1, "adet", True),
        ],
        "steps": ["Patatesi haşla, küp doğra.", "Soğan-maydanoz-sos ile karıştır."],
        "tags": ["salata", "vejetaryen"],
    },
    {
        "slug": "yulafli-kahvalti-kasesi",
        "title": "Yulaflı Kahvaltı Kâsesi",
        "servings": 1,
        "region": "genel",
        "ingredients": [
            ("yulaf", 50, "gram", False),
            ("süt", 200, "ml", False),
            ("muz", 1, "adet", True),
            ("ceviz", 20, "gram", True),
            ("bal", 1, "yemek kaşığı", True),
        ],
        "steps": ["Yulafı sütle ısıt.", "Muz, ceviz, bal ile servis et."],
        "tags": ["kahvaltı", "vejetaryen"],
    },
    {
        "slug": "menemen-peynirli",
        "title": "Peynirli Menemen",
        "servings": 2,
        "region": "genel",
        "ingredients": [
            ("yumurta", 3, "adet", False),
            ("domates", 2, "adet", False),
            ("beyaz peynir", 50, "gram", True),
            ("yeşil biber", 2, "adet", True),
        ],
        "steps": ["Biber-domatesi pişir.", "Yumurta ve peyniri ekle."],
        "tags": ["kahvaltı", "protein"],
    },
    {
        "slug": "nohut-salatasi",
        "title": "Nohut Salatası",
        "servings": 4,
        "region": "genel",
        "ingredients": [
            ("nohut", 2, "su bardağı", False),
            ("soğan", 1, "adet", True),
            ("domates", 1, "adet", True),
            ("maydanoz", None, None, True),
            ("zeytinyağı", 3, "yemek kaşığı", True),
            ("limon", 1, "adet", True),
        ],
        "steps": ["Haşlanmış nohutu sebzelerle karıştır.", "Limon-yağ sosuyla servis et."],
        "tags": ["salata", "vejetaryen"],
    },
    {
        "slug": "tavuklu-bulgur-pilavi",
        "title": "Tavuklu Bulgur Pilavı",
        "servings": 4,
        "region": "genel",
        "ingredients": [
            ("bulgur", 2, "su bardağı", False),
            ("tavuk göğsü", 250, "gram", False),
            ("domates salçası", 1, "yemek kaşığı", True),
            ("soğan", 1, "adet", True),
        ],
        "steps": ["Tavuk-soğanı kavur.", "Bulgur+salça+su ile pişir."],
        "tags": ["ana yemek", "protein"],
    },
    {
        "slug": "sebzeli-omlet",
        "title": "Sebzeli Omlet",
        "servings": 1,
        "region": "genel",
        "ingredients": [
            ("yumurta", 3, "adet", False),
            ("yeşil biber", 1, "adet", True),
            ("domates", 1, "adet", True),
            ("soğan", 1, "adet", True),
            ("zeytinyağı", 1, "yemek kaşığı", True),
        ],
        "steps": ["Sebzeleri sotele.", "Yumurtayı ekleyip pişir."],
        "tags": ["kahvaltı", "protein", "vejetaryen"],
    },
    {
        "slug": "firinda-tavuk-but",
        "title": "Fırında Tavuk Baget",
        "servings": 4,
        "region": "genel",
        "ingredients": [
            ("tavuk göğsü", 600, "gram", False),
            ("patates", 3, "adet", True),
            ("zeytinyağı", 3, "yemek kaşığı", True),
            ("sarımsak", 2, "diş", True),
        ],
        "steps": ["Tavuğu baharatla marine et.", "Patatesle tepsiye diz.", "200°C 40 dk fırınla."],
        "tags": ["ana yemek", "protein"],
    },
]


async def seed_recipes(session: AsyncSession) -> int:
    """Çekirdek tarifleri ekler (idempotent). Eklenen tarif sayısını döner."""
    added = 0
    for row in RECIPES + EXTRA_RECIPES + EXTRA_RECIPES3:
        exists = (
            await session.execute(select(Recipe).where(Recipe.slug == row["slug"]))
        ).scalar_one_or_none()
        if exists is not None:
            continue
        tags = row.get("tags", [])
        recipe = Recipe(
            slug=row["slug"],
            title_tr=row["title"],
            servings=row["servings"],
            region=row["region"],
            category=row.get("category") or (tags[0] if tags else None),
            cook_minutes=row.get("cook_minutes"),
            difficulty=row.get("difficulty"),
            image_url=row.get("image_url"),
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

    # Recipe toplam besin değerlerini hesapla (canonical + nutrition + birim → gram).
    all_recipes = (await session.execute(select(Recipe))).scalars().all()
    for rc in all_recipes:
        if rc.total_kcal is None:
            macros = await compute_recipe_macros(session, rc.id)
            if macros is not None:
                rc.total_kcal = macros["kcal"]
                rc.total_protein_g = macros["protein_g"]
                rc.total_carb_g = macros["carb_g"]
                rc.total_fat_g = macros["fat_g"]
                rc.total_fiber_g = macros["fiber_g"]
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
