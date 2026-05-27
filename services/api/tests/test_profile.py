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
