"""Yemek endpoint'leri (Faz 1) — izole DB, kurallı parser (LLM kapalı)."""


async def test_requires_token(client) -> None:
    resp = await client.post("/api/meals", json={"raw_text": "1 ayran"})
    assert resp.status_code == 401


async def test_empty_payload_rejected(client, auth) -> None:
    resp = await client.post("/api/meals", headers=auth, json={})
    assert resp.status_code == 422


async def test_create_from_raw_text_resolves_nutrition(client, auth) -> None:
    resp = await client.post(
        "/api/meals", headers=auth, json={"raw_text": "1 kase pilav, 1 ayran", "meal_type": "ogle"}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert len(body["items"]) == 2
    assert body["total_kcal"] and body["total_kcal"] > 0
    # pilav seed'den çözülmeli → canonical + kcal dolu
    pilav = next(i for i in body["items"] if i["raw_name"] == "pilav")
    assert pilav["canonical_id"] is not None
    assert pilav["kcal"] == 260.0  # 130 * 200g/100
    assert pilav["confidence"] == 1.0


async def test_everyday_dishes_resolve_nutrition(client, auth) -> None:
    """Regresyon: sık loglanan gündelik yemekler (çorba + ekmek) kalori almalı.

    Canlı smoke testinde "1 kase mercimek çorbası, 2 dilim ekmek" 0 kcal dönüyordu
    (canonical eşleşmiyordu). Seed genişletmesinden sonra ikisi de çözülmeli.
    """
    resp = await client.post(
        "/api/meals",
        headers=auth,
        json={"raw_text": "1 kase mercimek çorbası, 2 dilim ekmek", "meal_type": "ogle"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["total_kcal"] and body["total_kcal"] > 0
    corba = next(i for i in body["items"] if "çorba" in i["raw_name"])
    ekmek = next(i for i in body["items"] if i["raw_name"] == "ekmek")
    assert corba["canonical_id"] is not None
    assert corba["kcal"] == 110.0  # 55 * 200g/100
    assert ekmek["canonical_id"] is not None
    assert ekmek["kcal"] == 159.0  # 265 * 60g/100
    assert ekmek["confidence"] == 1.0


async def test_structured_kcal_honored(client, auth) -> None:
    resp = await client.post(
        "/api/meals", headers=auth, json={"items": [{"raw_name": "ayran", "kcal": 60}]}
    )
    assert resp.status_code == 201
    assert resp.json()["total_kcal"] == 60


async def test_list_and_summary(client, auth) -> None:
    created = (
        await client.post("/api/meals", headers=auth, json={"raw_text": "1 kase pilav"})
    ).json()
    day = created["eaten_at"][:10]

    listed = await client.get(f"/api/meals?date={day}", headers=auth)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    summary = await client.get(f"/api/summary?date={day}", headers=auth)
    assert summary.status_code == 200
    s = summary.json()
    assert s["meal_count"] == 1
    assert s["intake_kcal"] > 0


async def test_summary_empty_day(client, auth) -> None:
    summary = await client.get("/api/summary?date=2000-01-01", headers=auth)
    assert summary.status_code == 200
    assert summary.json()["intake_kcal"] == 0
    assert summary.json()["meal_count"] == 0


async def test_unknown_food_low_confidence(client, auth) -> None:
    resp = await client.post(
        "/api/meals", headers=auth, json={"raw_text": "1 kase ejderha meyvesi"}
    )
    body = resp.json()
    item = body["items"][0]
    assert item["canonical_id"] is None
    assert item["confidence"] == 0.2


async def test_update_meal_replaces_items(client, auth) -> None:
    created = (
        await client.post(
            "/api/meals",
            headers=auth,
            json={"meal_type": "atistirma", "items": [{"raw_name": "ayran", "kcal": 60}]},
        )
    ).json()
    mid = created["id"]
    upd = await client.put(
        f"/api/meals/{mid}",
        headers=auth,
        json={"meal_type": "kahvalti", "items": [{"raw_name": "süt", "kcal": 120}]},
    )
    assert upd.status_code == 200
    body = upd.json()
    assert body["meal_type"] == "kahvalti"
    assert body["total_kcal"] == 120
    assert len(body["items"]) == 1
    assert body["items"][0]["raw_name"] == "süt"


async def test_delete_meal(client, auth) -> None:
    mid = (
        await client.post(
            "/api/meals", headers=auth, json={"items": [{"raw_name": "ayran", "kcal": 60}]}
        )
    ).json()["id"]
    d = await client.delete(f"/api/meals/{mid}", headers=auth)
    assert d.status_code == 204
    day = __import__("datetime").date.today().isoformat()
    listed = await client.get(f"/api/meals?date={day}", headers=auth)
    assert all(m["id"] != mid for m in listed.json())


async def test_update_missing_404(client, auth) -> None:
    assert (
        await client.put("/api/meals/999999", headers=auth, json={"meal_type": "kahvalti"})
    ).status_code == 404


async def test_delete_missing_404(client, auth) -> None:
    assert (await client.delete("/api/meals/999999", headers=auth)).status_code == 404


async def test_delete_requires_token(client) -> None:
    assert (await client.delete("/api/meals/1")).status_code == 401
