"""Antrenman uçları — katalog, plan, log CRUD."""

from app.data import workouts as W


def test_build_plan_unit() -> None:
    plan = W.build_plan("kas_yap", "intermediate", 4, None)
    assert plan["days_per_week"] == 4
    assert len(plan["days"]) == 4
    assert plan["focus"] == "kuvvet (split)"
    # her gün kuvvet + kapanış kardiyosu
    assert plan["days"][0]["exercises"][-1]["category"] == "kardiyo"
    assert plan["weekly_minutes"] > 0


def test_build_plan_beginner_reduces_sets() -> None:
    beg = W.build_plan("koru", "beginner", 3, None)
    # squat 3 set -> beginner 2
    squat = next(x for x in beg["days"][0]["exercises"] if x["slug"] == "squat")
    assert squat["sets"] == 2


def test_burned_kcal() -> None:
    # kardiyo MET 8: round(8*3.5*70/200*30) = 294
    assert W.burned_kcal("treadmill-run", 30, 70) == 294


async def test_workouts_requires_token(client) -> None:
    assert (await client.get("/api/workouts")).status_code == 401


async def test_list_workouts_filter(client, auth) -> None:
    resp = await client.get("/api/workouts?muscle=gogus", headers=auth)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert all(e["primary_muscle"] == "gogus" for e in data)
    assert "equipment_type" in data[0]


async def test_workout_plan_endpoint(client, auth) -> None:
    resp = await client.get(
        "/api/workout-plan?goal=kilo_ver&level=intermediate&days_per_week=4", headers=auth
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["goal_type"] == "kilo_ver"
    assert len(body["days"]) == 4


async def test_workout_log_crud(client, auth) -> None:
    day = __import__("datetime").date.today().isoformat()
    created = await client.post(
        f"/api/workout-logs?date={day}",
        headers=auth,
        json={"template_slug": "bench-press", "sets": 4, "reps": "10", "minutes": 25},
    )
    assert created.status_code == 201
    log = created.json()
    assert log["name_tr"] == "Bench Press (Göğüs Presi)"
    assert log["kcal"] and log["kcal"] > 0
    lid = log["id"]

    listed = await client.get(f"/api/workout-logs?date={day}", headers=auth)
    assert any(w["id"] == lid for w in listed.json())

    d = await client.delete(f"/api/workout-logs/{lid}", headers=auth)
    assert d.status_code == 204
    assert (await client.delete(f"/api/workout-logs/{lid}", headers=auth)).status_code == 404


async def test_unknown_slug_uses_slug_as_name(client, auth) -> None:
    resp = await client.post(
        "/api/workout-logs",
        headers=auth,
        json={"template_slug": "bilinmeyen-hareket", "minutes": 20},
    )
    assert resp.status_code == 201
    assert resp.json()["name_tr"] == "bilinmeyen-hareket"
