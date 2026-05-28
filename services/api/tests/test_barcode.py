"""POST /api/meals/by-barcode — OpenFoodFacts mock'lu uçtan uca."""

import httpx
import respx

from app.config import get_settings

S = get_settings()


@respx.mock
async def test_barcode_creates_meal_with_scaled_macros(client, auth) -> None:
    respx.get(f"{S.off_base_url}/api/v2/product/8690000000000.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": 1,
                "product": {
                    "product_name": "Eker Ayran",
                    "nutriments": {
                        "energy-kcal_100g": 40,
                        "proteins_100g": 1.7,
                        "carbohydrates_100g": 3.0,
                        "fat_100g": 2.0,
                    },
                },
            },
        )
    )
    resp = await client.post(
        "/api/meals/by-barcode",
        headers=auth,
        json={"barcode": "8690000000000", "grams": 200, "meal_type": "atistirma"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["total_kcal"] == 80.0  # 40 kcal/100g * 200g
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["canonical_id"] is not None
    assert item["unit"] == "gram"
    assert item["protein_g"] == 3.4
    assert "[barkod 8690000000000]" in body["raw_text"]


@respx.mock
async def test_barcode_404_when_not_found(client, auth) -> None:
    respx.get(f"{S.off_base_url}/api/v2/product/000.json").mock(
        return_value=httpx.Response(200, json={"status": 0})
    )
    resp = await client.post("/api/meals/by-barcode", headers=auth, json={"barcode": "000"})
    assert resp.status_code == 404


async def test_barcode_requires_token(client) -> None:
    resp = await client.post("/api/meals/by-barcode", json={"barcode": "8690000000000"})
    assert resp.status_code == 401
