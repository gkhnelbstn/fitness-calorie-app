"""Öneri motoru endpoint'leri."""


async def test_requires_token(client) -> None:
    assert (await client.get("/api/recommendations")).status_code == 401


async def test_recommendation_without_profile(client, auth) -> None:
    r = await client.get("/api/recommendations", headers=auth)
    assert r.status_code == 200
    body = r.json()
    assert body["id"] is not None
    assert body["energy"]["target_kcal"] is None
    assert any("hesaplanamadı" in n for n in body["notes"])
    assert len(body["meal_suggestions"]) >= 1  # tarifler seed'li
    assert body["workout"]["focus"]  # koru default plan


async def test_recommendation_with_profile_and_goal(client, auth) -> None:
    await client.put(
        "/api/profile",
        headers=auth,
        json={
            "sex": "erkek",
            "weight_kg": 80,
            "height_cm": 178,
            "birth_year": 1996,
            "activity_level": "moderate",
        },
    )
    await client.put("/api/goal", headers=auth, json={"goal_type": "kilo_ver"})
    created = (
        await client.post("/api/meals", headers=auth, json={"raw_text": "1 kase pilav"})
    ).json()
    day = created["eaten_at"][:10]

    body = (await client.get(f"/api/recommendations?date={day}", headers=auth)).json()
    assert body["energy"]["bmr"] == 1767.5
    assert body["energy"]["target_kcal"] == 2240
    assert body["energy"]["intake_kcal"] > 0
    assert body["energy"]["remaining_kcal"] is not None
    assert body["energy"]["protein_target_g"] == 128.0  # 80 * 1.6
    assert body["workout"]["focus"] == "kardiyo + kuvvet"


async def test_feedback(client, auth) -> None:
    rec = (await client.get("/api/recommendations", headers=auth)).json()
    ok = await client.post(
        "/api/recommendations/feedback",
        headers=auth,
        json={"recommendation_id": rec["id"], "action": "accepted"},
    )
    assert ok.status_code == 201

    missing = await client.post(
        "/api/recommendations/feedback",
        headers=auth,
        json={"recommendation_id": 999999, "action": "rejected"},
    )
    assert missing.status_code == 404
