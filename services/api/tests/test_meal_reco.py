"""Öneri v2 — içerik-tabanlı skor + tercih (exp-decay) birim/uçtan."""

from app.schemas.recipe import IngredientLine, RecipeRead
from app.services.meal_reco import score_recipes


def _r(slug, kcal, tags, canon_ids):
    return RecipeRead(
        id=hash(slug) % 100000,
        slug=slug,
        title_tr=slug,
        total_kcal=kcal,
        tags=tags,
        ingredients=[IngredientLine(raw_name=str(c), canonical_id=c) for c in canon_ids],
        steps=[],
    )


def test_calfit_prefers_close_kcal() -> None:
    recipes = [_r("uzak", 1200, [], []), _r("yakin", 520, [], [])]
    scored = score_recipes(recipes, {}, meal_target=500, protein_remaining=None)
    assert scored[0][0].slug == "yakin"  # 500'e yakın kazanır


def test_affinity_boosts_preferred_ingredients() -> None:
    recipes = [_r("tercihli", 500, [], [1, 2]), _r("notr", 500, [], [99])]
    pref = {1: 5.0, 2: 3.0}  # kullanıcı 1 ve 2'yi sık yemiş
    scored = score_recipes(recipes, pref, meal_target=500, protein_remaining=None)
    assert scored[0][0].slug == "tercihli"


def test_protein_tag_boost_when_gap() -> None:
    recipes = [_r("proteinli", 500, ["protein"], []), _r("sade", 500, [], [])]
    scored = score_recipes(recipes, {}, meal_target=500, protein_remaining=40)
    assert scored[0][0].slug == "proteinli"


def test_cold_start_no_pref_ranks_by_nutrition() -> None:
    recipes = [_r("a", 800, [], []), _r("b", 500, [], [])]
    scored = score_recipes(recipes, {}, meal_target=500, protein_remaining=None)
    assert scored[0][0].slug == "b"  # affinity 0 → kalori uyumu belirler


async def test_recommendation_orders_by_preference(client, auth) -> None:
    # Profil+hedef + birkaç pilav kaydı → pirinç tercihi oluşsun
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
    await client.put("/api/goal", headers=auth, json={"goal_type": "koru"})
    for _ in range(3):
        await client.post("/api/meals", headers=auth, json={"raw_text": "1 kase pilav"})
    body = (await client.get("/api/recommendations", headers=auth)).json()
    assert len(body["meal_suggestions"]) >= 1
    assert any("tercih" in n.lower() for n in body["notes"])
