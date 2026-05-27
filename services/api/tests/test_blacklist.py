"""Kara liste endpoint'leri + tarif filtresine etkisi."""


async def test_blacklist_crud(client, auth) -> None:
    # ekle
    r = await client.post("/api/blacklist", headers=auth, json={"name": "sarımsak"})
    assert r.status_code == 201
    item = r.json()
    assert item["slug"] == "sarimsak"
    cid = item["canonical_id"]

    # listele
    lst = await client.get("/api/blacklist", headers=auth)
    assert lst.status_code == 200
    assert any(i["canonical_id"] == cid for i in lst.json())

    # sil
    d = await client.delete(f"/api/blacklist/{cid}", headers=auth)
    assert d.status_code == 204
    assert (await client.get("/api/blacklist", headers=auth)).json() == []


async def test_blacklist_requires_token(client) -> None:
    assert (await client.post("/api/blacklist", json={"name": "x"})).status_code == 401


async def test_blacklist_empty_name_422(client, auth) -> None:
    r = await client.post("/api/blacklist", headers=auth, json={"name": "   "})
    assert r.status_code == 422


async def test_delete_missing_404(client, auth) -> None:
    r = await client.delete("/api/blacklist/999999", headers=auth)
    assert r.status_code == 404


async def test_blacklist_affects_recipe_search(client, auth) -> None:
    # sarımsak cacık'ta opsiyonel → cacık kalır, sarımsak çıkarılır (not düşülür)
    await client.post("/api/blacklist", headers=auth, json={"name": "sarımsak"})
    recipes = (await client.get("/api/recipes?q=cacık", headers=auth)).json()
    cacik = next(r for r in recipes if r["slug"] == "cacik")
    sar = next(i for i in cacik["ingredients"] if i["raw_name"] == "sarımsak")
    assert sar["status"] == "removed"
    assert any("sarımsak" in n for n in cacik["notes"])
