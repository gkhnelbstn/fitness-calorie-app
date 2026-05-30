"""Tarif arama + hard filter + adaptasyon + cook-with."""


async def _slugs(resp) -> set[str]:
    return {r["slug"] for r in resp.json()}


async def test_search_all(client, auth) -> None:
    # Tüm sayfayı al (geniş limit). Çekirdek + geniş set seed'li.
    resp = await client.get("/api/recipes?limit=100", headers=auth)
    assert resp.status_code == 200
    slugs = await _slugs(resp)
    assert {
        "menemen",
        "cacik",
        "mercimek-corbasi",
        "lahmacun",
        "imam-bayildi",
        "firinda-somon",
    } <= slugs
    assert len(slugs) >= 40


async def test_pagination(client, auth) -> None:
    page1 = (await client.get("/api/recipes?limit=10&offset=0", headers=auth)).json()
    page2 = (await client.get("/api/recipes?limit=10&offset=10", headers=auth)).json()
    assert len(page1) == 10
    assert len(page2) == 10
    s1 = {r["slug"] for r in page1}
    s2 = {r["slug"] for r in page2}
    assert not (s1 & s2)  # sayfalar çakışmaz


async def test_recipe_exposes_new_fields(client, auth) -> None:
    """Recipe model alanları (category/cook_minutes/difficulty/image_url/macros_per_serving)
    response'ta bulunmalı; category seed'de ilk tag'den türetilir."""
    resp = await client.get("/api/recipes?q=mercimek", headers=auth)
    merc = next(r for r in resp.json() if r["slug"] == "mercimek-corbasi")
    for key in ("category", "cook_minutes", "difficulty", "image_url", "macros_per_serving"):
        assert key in merc
    assert merc["category"] == "çorba"  # tags[0]
    # total_kcal + servings varsa porsiyon başı kcal türetilir
    if merc["total_kcal"] and merc["servings"]:
        assert merc["macros_per_serving"]["kcal"] > 0


async def test_category_filter(client, auth) -> None:
    resp = await client.get("/api/recipes?category=çorba&limit=100", headers=auth)
    assert resp.status_code == 200
    recipes = resp.json()
    assert recipes  # en az bir çorba
    assert all(r["category"] == "çorba" for r in recipes)
    slugs = {r["slug"] for r in recipes}
    assert "mercimek-corbasi" in slugs
    assert "menemen" not in slugs  # kahvaltı kategorisinde


async def test_search_query_filter(client, auth) -> None:
    resp = await client.get("/api/recipes?q=menemen", headers=auth)
    slugs = await _slugs(resp)
    assert "menemen" in slugs
    assert all("menemen" in s for s in slugs)  # hepsi menemen varyantı


async def test_exclude_nonoptional_removes_recipe(client, auth) -> None:
    # yumurta menemen + haşlanmış yumurta'da zorunlu → ikisi de elenir
    resp = await client.get("/api/recipes?exclude=yumurta", headers=auth)
    slugs = await _slugs(resp)
    assert "menemen" not in slugs
    assert "haslanmis-yumurta" not in slugs
    assert "cacik" in slugs


async def test_exclude_optional_keeps_with_note(client, auth) -> None:
    # soğan mercimek çorbasında opsiyonel → tarif kalır, soğan çıkarılır
    resp = await client.get("/api/recipes?exclude=soğan&q=mercimek", headers=auth)
    recipes = resp.json()
    merc = next(r for r in recipes if r["slug"] == "mercimek-corbasi")
    sogan = next(i for i in merc["ingredients"] if i["raw_name"] == "soğan")
    assert sogan["status"] == "removed"


async def test_exclude_nonoptional_substituted(client, auth) -> None:
    # pirinç pilavda zorunlu, ikamesi şehriye → substitute
    resp = await client.get("/api/recipes?exclude=pirinç&q=pilav", headers=auth)
    recipes = resp.json()
    pilav = next(r for r in recipes if r["slug"] == "pirinc-pilavi-tarif")
    pirinc = next(i for i in pilav["ingredients"] if i["raw_name"] == "pirinç")
    assert pirinc["status"] == "substituted"
    assert pirinc["substitute"].casefold() == "şehriye"


async def test_exclude_nonoptional_no_sub_blocks(client, auth) -> None:
    # domates menemen'de zorunlu, ikamesi yok → menemen elenir
    resp = await client.get("/api/recipes?exclude=domates", headers=auth)
    assert "menemen" not in await _slugs(resp)


async def test_cook_with(client, auth) -> None:
    resp = await client.get("/api/recipes/cook-with?have=yumurta", headers=auth)
    slugs = await _slugs(resp)
    # haşlanmış yumurta yalnız yumurta gerektirir (tuz opsiyonel)
    assert "haslanmis-yumurta" in slugs
    # menemen domates de ister → gelmez
    assert "menemen" not in slugs


async def test_cook_with_excludes_blacklisted(client, auth) -> None:
    resp = await client.get("/api/recipes/cook-with?have=yumurta&exclude=yumurta", headers=auth)
    assert "haslanmis-yumurta" not in await _slugs(resp)
