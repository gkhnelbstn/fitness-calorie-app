"""Ücretsiz adapter'lar — ağ respx ile mock'lanır, parse doğrulanır."""

import httpx
import respx

from app.adapters.free_exercise_db import FreeExerciseDbAdapter
from app.adapters.openfoodfacts import OpenFoodFactsAdapter
from app.adapters.usda import UsdaAdapter
from app.config import get_settings

S = get_settings()


@respx.mock
async def test_off_by_barcode_parses() -> None:
    respx.get(f"{S.off_base_url}/api/v2/product/8690000000000.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": 1,
                "product": {
                    "product_name": "Ayran",
                    "nutriments": {
                        "energy-kcal_100g": 40,
                        "proteins_100g": 3.2,
                        "carbohydrates_100g": 4.0,
                        "fat_100g": 1.5,
                    },
                },
            },
        )
    )
    hit = await OpenFoodFactsAdapter().by_barcode("8690000000000")
    assert hit is not None
    assert hit.name == "Ayran"
    assert hit.kcal_per_100g == 40
    assert hit.source == "OpenFoodFacts"


@respx.mock
async def test_off_not_found_returns_none() -> None:
    respx.get(f"{S.off_base_url}/api/v2/product/000.json").mock(
        return_value=httpx.Response(200, json={"status": 0})
    )
    assert await OpenFoodFactsAdapter().by_barcode("000") is None


@respx.mock
async def test_usda_search_parses() -> None:
    respx.get(f"{S.usda_base_url}/foods/search").mock(
        return_value=httpx.Response(
            200,
            json={
                "foods": [
                    {
                        "description": "Rice, white, cooked",
                        "foodNutrients": [
                            {"nutrientName": "Energy", "value": 130},
                            {"nutrientName": "Protein", "value": 2.7},
                        ],
                    }
                ]
            },
        )
    )
    hits = await UsdaAdapter().search("rice")
    assert len(hits) == 1
    assert hits[0].kcal_per_100g == 130
    assert hits[0].protein_g == 2.7


@respx.mock
async def test_free_exercise_db_parses() -> None:
    respx.get(S.free_exercise_db_url).mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "name": "Squat",
                    "primaryMuscles": ["quadriceps"],
                    "level": "beginner",
                    "equipment": "body only",
                }
            ],
        )
    )
    hits = await FreeExerciseDbAdapter().fetch_all()
    assert len(hits) == 1
    assert hits[0].name == "Squat"
    assert hits[0].primary_muscle == "quadriceps"
