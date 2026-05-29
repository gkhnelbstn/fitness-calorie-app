"""Admin import endpoint'leri (TheMealDB / USDA / Spoonacular) — respx-mock'lu.

NVIDIA anahtarı testlerde kapalı → translate=false ile İngilizce kalır, ağ yok.
"""

import httpx
import respx

from app import config
from app.config import get_settings

S = get_settings()


async def test_admin_requires_token(client) -> None:
    assert (await client.post("/api/admin/import/usda?query=rice")).status_code == 401


@respx.mock
async def test_import_themealdb(client, auth) -> None:
    respx.get(f"{S.themealdb_base_url}/search.php").mock(
        return_value=httpx.Response(
            200,
            json={
                "meals": [
                    {
                        "strMeal": "Pancakes",
                        "strInstructions": "Mix batter.\nCook on pan.",
                        "strArea": "American",
                        "strCategory": "Dessert",
                        "strIngredient1": "Flour",
                        "strMeasure1": "1 cup",
                        "strIngredient2": "Egg",
                        "strMeasure2": "2",
                        "strIngredient3": "",
                        "strMeasure3": "",
                    }
                ]
            },
        )
    )
    resp = await client.post("/api/admin/import/themealdb?letters=p&translate=false", headers=auth)
    assert resp.status_code == 200
    assert resp.json()["imported"] == 1

    found = await client.get("/api/recipes?q=pancakes", headers=auth)
    slugs = {r["slug"] for r in found.json()}
    assert "pancakes" in slugs


@respx.mock
async def test_import_themealdb_idempotent(client, auth) -> None:
    route = respx.get(f"{S.themealdb_base_url}/search.php").mock(
        return_value=httpx.Response(
            200,
            json={
                "meals": [
                    {
                        "strMeal": "Zzztest Yemek",
                        "strInstructions": "Bake.",
                        "strArea": "Turkish",
                        "strCategory": "Main",
                        "strIngredient1": "Dough",
                        "strMeasure1": "1",
                    }
                ]
            },
        )
    )
    first = await client.post("/api/admin/import/themealdb?letters=l&translate=false", headers=auth)
    second = await client.post(
        "/api/admin/import/themealdb?letters=l&translate=false", headers=auth
    )
    assert first.json()["imported"] == 1
    assert second.json()["imported"] == 0  # zaten var
    assert route.called


async def test_import_themealdb_bad_letters(client, auth) -> None:
    resp = await client.post("/api/admin/import/themealdb?letters=123", headers=auth)
    assert resp.status_code == 422


@respx.mock
async def test_import_usda(client, auth) -> None:
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
    resp = await client.post("/api/admin/import/usda?query=rice&translate=false", headers=auth)
    assert resp.status_code == 200
    assert resp.json()["imported"] == 1


@respx.mock
async def test_live_recipe_search(client, auth) -> None:
    # /api/recipes?live=true → TheMealDB search.php?s=... → idempotent import → yerel sonuç
    respx.get(f"{S.themealdb_base_url}/search.php").mock(
        return_value=httpx.Response(
            200,
            json={
                "meals": [
                    {
                        "strMeal": "Shakshuka",
                        "strInstructions": "Cook.",
                        "strArea": "Egyptian",
                        "strCategory": "Breakfast",
                        "strIngredient1": "Egg",
                        "strMeasure1": "3",
                    }
                ]
            },
        )
    )
    # NVIDIA kapalı → translate identity → q 'shakshuka' EN olarak gider, başlık EN kalır
    resp = await client.get("/api/recipes?q=shakshuka&live=true", headers=auth)
    assert resp.status_code == 200
    slugs = {r["slug"] for r in resp.json()}
    assert "shakshuka" in slugs


@respx.mock
async def test_live_search_no_match_graceful(client, auth) -> None:
    respx.get(f"{S.themealdb_base_url}/search.php").mock(
        return_value=httpx.Response(200, json={"meals": None})
    )
    resp = await client.get("/api/recipes?q=bilinmeyenxyz&live=true", headers=auth)
    assert resp.status_code == 200  # sonuç yok ama hata vermez


async def test_import_spoonacular_no_key(client, auth) -> None:
    resp = await client.post("/api/admin/import/spoonacular?query=soup", headers=auth)
    assert resp.status_code == 400


@respx.mock
async def test_import_spoonacular_with_key(client, auth, monkeypatch) -> None:
    monkeypatch.setenv("SPOONACULAR_API_KEY", "test-key")
    config.get_settings.cache_clear()
    respx.get("https://api.spoonacular.com/recipes/complexSearch").mock(
        return_value=httpx.Response(
            200,
            json={
                "results": [
                    {
                        "title": "Tomato Soup",
                        "instructions": "<p>Boil tomatoes.</p>",
                        "dishTypes": ["soup"],
                        "extendedIngredients": [{"name": "tomato", "original": "2 tomatoes"}],
                    }
                ]
            },
        )
    )
    resp = await client.post(
        "/api/admin/import/spoonacular?query=soup&translate=false", headers=auth
    )
    assert resp.status_code == 200
    assert resp.json()["imported"] == 1
