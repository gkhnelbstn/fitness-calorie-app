"""Yiyecek porsiyon endpoint'i — ölçü seçimi + besin karşılığı."""


async def test_requires_token(client) -> None:
    assert (await client.get("/api/foods/portions?name=pilav")).status_code == 401


async def test_portions_known_food(client, auth) -> None:
    r = await client.get("/api/foods/portions?name=pilav", headers=auth)
    assert r.status_code == 200
    body = r.json()
    assert body["matched"] is True
    assert body["canonical_id"] is not None
    assert body["default_measure"]
    assert len(body["portions"]) >= 1
    # her ölçü gram + kcal taşır (pilav seed'de besinli)
    p = body["portions"][0]
    assert p["grams"] > 0
    assert p["kcal"] and p["kcal"] > 0


async def test_portions_soup_measures(client, auth) -> None:
    # çorba kategorisi → kase önce gelir
    r = await client.get("/api/foods/portions?name=mercimek çorbası", headers=auth)
    body = r.json()
    measures = [p["measure"] for p in body["portions"]]
    assert "kase" in measures
    assert body["matched"] is True


async def test_portions_unknown_food(client, auth) -> None:
    r = await client.get("/api/foods/portions?name=zzz bilinmeyen", headers=auth)
    body = r.json()
    assert body["matched"] is False
    # eşleşme yok ama yine de ölçü listesi + gram döner (kcal null)
    assert len(body["portions"]) >= 1
    assert all(p["kcal"] is None for p in body["portions"])
