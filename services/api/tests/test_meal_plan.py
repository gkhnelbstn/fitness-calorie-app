"""Yemek planı parser + endpoint'ler."""

from app.services.meal_plan import parse_plan

PLAN = "# Gün 0\n- Kahvaltı: 2 yumurta, 1 simit\n- Öğle: 1 kase pilav\n# Gün 1\n- Kahvaltı: omlet\n"


def test_parse_plan_unit() -> None:
    entries = parse_plan(PLAN)
    assert len(entries) == 3
    assert entries[0].day_offset == 0
    assert entries[0].meal_type == "kahvalti"
    assert entries[1].meal_type == "ogle"
    assert entries[2].day_offset == 1


def test_parse_plan_empty() -> None:
    assert parse_plan("") == []


async def test_preview(client, auth) -> None:
    resp = await client.post("/api/meal-plans/preview", headers=auth, json={"text": PLAN})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["entries"]) == 3
    assert body["entries"][0]["raw_text"] == "2 yumurta, 1 simit"


async def test_apply_creates_meals(client, auth) -> None:
    resp = await client.post(
        "/api/meal-plans/apply",
        headers=auth,
        json={"text": PLAN, "base_date": "2026-05-28"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["base_date"] == "2026-05-28"
    assert len(body["created_meal_ids"]) == 3

    day0 = await client.get("/api/meals?date=2026-05-28", headers=auth)
    assert len(day0.json()) == 2  # 0. gün iki öğün

    day1 = await client.get("/api/meals?date=2026-05-29", headers=auth)
    assert len(day1.json()) == 1


async def test_preview_requires_token(client) -> None:
    assert (await client.post("/api/meal-plans/preview", json={"text": ""})).status_code == 401
