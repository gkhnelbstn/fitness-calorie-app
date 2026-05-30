"""Profil + hedef endpoint'leri."""


async def test_requires_token(client) -> None:
    assert (await client.get("/api/profile")).status_code == 401


async def test_profile_update_and_get(client, auth) -> None:
    r = await client.put(
        "/api/profile",
        headers=auth,
        json={"sex": "erkek", "weight_kg": 80, "height_cm": 178, "birth_year": 1996},
    )
    assert r.status_code == 200
    assert r.json()["weight_kg"] == 80
    g = await client.get("/api/profile", headers=auth)
    assert g.json()["sex"] == "erkek"


async def test_goal_404_when_none(client, auth) -> None:
    assert (await client.get("/api/goal", headers=auth)).status_code == 404


async def test_goal_set_and_replace(client, auth) -> None:
    r = await client.put("/api/goal", headers=auth, json={"goal_type": "koru"})
    assert r.status_code == 201
    assert r.json()["active"] is True

    await client.put("/api/goal", headers=auth, json={"goal_type": "kas_yap"})
    active = await client.get("/api/goal", headers=auth)
    assert active.json()["goal_type"] == "kas_yap"


async def test_goal_plan_requires_token(client) -> None:
    assert (await client.get("/api/goal/plan")).status_code == 401


async def test_goal_plan_null_when_empty(client, auth) -> None:
    r = await client.get("/api/goal/plan", headers=auth)
    assert r.status_code == 200
    assert r.json() is None


async def test_goal_plan_put_then_partial_merge(client, auth) -> None:
    r = await client.put(
        "/api/goal/plan",
        headers=auth,
        json={"start_weight": 80, "target_weight": 72, "weeks": 16, "pace": 0.5},
    )
    assert r.status_code == 200
    assert r.json()["target_weight"] == 72

    # Kısmi PUT mevcut alanları korur, yenileri ekler.
    r2 = await client.put(
        "/api/goal/plan",
        headers=auth,
        json={"training_days": ["Pzt", "Per"], "days_per_week": 2},
    )
    body = r2.json()
    assert body["training_days"] == ["Pzt", "Per"]
    assert body["days_per_week"] == 2
    assert body["start_weight"] == 80  # önceki alan korundu

    g = await client.get("/api/goal/plan", headers=auth)
    assert g.json()["weeks"] == 16
