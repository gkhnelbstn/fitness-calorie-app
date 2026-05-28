"""POST /api/meals/photo — multipart upload, dosya saklama, opsiyonel raw_text."""

from pathlib import Path

from app import config


async def test_upload_with_raw_text(client, auth, monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path))
    config.get_settings.cache_clear()

    files = {"photo": ("food.jpg", b"\xff\xd8\xff fake", "image/jpeg")}
    data = {"raw_text": "1 ayran", "meal_type": "atistirma"}
    resp = await client.post("/api/meals/photo", headers=auth, files=files, data=data)
    assert resp.status_code == 201
    body = resp.json()
    assert body["photo_path"].endswith(".jpg")
    assert Path(body["photo_path"]).exists()
    assert any(i["raw_name"] == "ayran" for i in body["items"])
    assert body["meal_type"] == "atistirma"


async def test_upload_without_text_empty_items(client, auth, monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path))
    config.get_settings.cache_clear()

    files = {"photo": ("x.png", b"x", "image/png")}
    resp = await client.post("/api/meals/photo", headers=auth, files=files)
    assert resp.status_code == 201
    body = resp.json()
    assert body["items"] == []
    assert body["total_kcal"] is None
    assert body["photo_path"].endswith(".png")


async def test_upload_requires_token(client, monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path))
    config.get_settings.cache_clear()
    files = {"photo": ("x.jpg", b"x", "image/jpeg")}
    resp = await client.post("/api/meals/photo", files=files)
    assert resp.status_code == 401
