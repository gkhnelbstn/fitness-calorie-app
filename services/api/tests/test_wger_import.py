"""wger Türkçe besin import — respx-mock'lu (ağ yok)."""

import httpx
import respx

from app.config import get_settings

S = get_settings()

_PAGE = {
    "next": None,
    "results": [
        {
            "name": "Bazlama",
            "energy": 270,
            "protein": 8,
            "carbohydrates": 53,
            "fat": 2,
            "code": None,
        },
        {
            "name": "Köy Peyniri",
            "energy": 280,
            "protein": 18,
            "carbohydrates": 2,
            "fat": 22,
            "code": "8690",
        },
        # enerji yok → atlanır
        {"name": "Bozuk Kayıt", "energy": None, "protein": 1},
    ],
}


async def test_requires_token(client) -> None:
    assert (await client.post("/api/admin/import/wger-tr")).status_code == 401


@respx.mock
async def test_import_wger_tr_and_loggable(client, auth) -> None:
    respx.get(url__startswith=f"{S.wger_base_url}/api/v2/ingredient/").mock(
        return_value=httpx.Response(200, json=_PAGE)
    )
    r = await client.post("/api/admin/import/wger-tr?limit=50", headers=auth)
    assert r.status_code == 200
    assert r.json()["imported"] == 2  # enerjisiz kayıt atlandı

    # Idempotent: ikinci çağrı yeni nutrition eklemez.
    r2 = await client.post("/api/admin/import/wger-tr?limit=50", headers=auth)
    assert r2.json()["imported"] == 0

    # İçe alınan besin öğün loglamada çözülür (canonical + per_100g nutrition).
    meal = (
        await client.post(
            "/api/meals",
            headers=auth,
            json={"items": [{"raw_name": "Bazlama", "quantity": 100, "unit": "gram"}]},
        )
    ).json()
    item = meal["items"][0]
    assert item["canonical_id"] is not None
    assert item["kcal"] == 270.0  # 270/100g * 100g
