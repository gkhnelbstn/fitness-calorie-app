"""Tarif toplam kalori hesabı — seed_all sonrası mercimek çorbası kcal dolu olmalı."""

from app.services.recipe_kcal import compute_recipe_kcal


async def test_seeded_recipe_total_kcal(client, auth) -> None:
    resp = await client.get("/api/recipes?q=mercimek", headers=auth)
    assert resp.status_code == 200
    rec = next(r for r in resp.json() if r["slug"] == "mercimek-corbasi")
    assert rec["total_kcal"] is not None
    assert rec["total_kcal"] > 0


async def test_compute_returns_none_for_unknown_recipe(seeded_session) -> None:
    assert await compute_recipe_kcal(seeded_session, 999999) is None
