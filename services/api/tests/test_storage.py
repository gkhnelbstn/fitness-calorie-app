"""Foto depolama — lokal fallback + Supabase Storage yolu (respx mock)."""

from __future__ import annotations

import httpx
import pytest
import respx

from app import config
from app.services.storage import save_photo


@pytest.fixture
def local_env(monkeypatch, tmp_path):
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "photos"))
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    config.get_settings.cache_clear()
    yield tmp_path / "photos"
    config.get_settings.cache_clear()


@pytest.fixture
def supabase_env(monkeypatch):
    monkeypatch.setenv("SUPABASE_PROJECT_URL", "https://proj.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "service-key")
    config.get_settings.cache_clear()
    yield
    config.get_settings.cache_clear()


async def test_save_photo_local(local_env) -> None:
    path = await save_photo(b"jpegdata", ".jpg")
    assert path.startswith("/uploads/")
    fname = path.removeprefix("/uploads/")
    assert (local_env / fname).read_bytes() == b"jpegdata"


@respx.mock
async def test_save_photo_supabase(supabase_env) -> None:
    route = respx.post(
        url__regex=r"https://proj\.supabase\.co/storage/v1/object/meal-photos/.*"
    ).mock(return_value=httpx.Response(200, json={"Key": "ok"}))
    url = await save_photo(b"jpegdata", ".jpg")
    assert route.called
    assert url.startswith("https://proj.supabase.co/storage/v1/object/public/meal-photos/")
    assert url.endswith(".jpg")
    # service key yalnız Authorization header'ında, URL'de değil
    assert "service-key" not in url


@respx.mock
async def test_save_photo_supabase_error(supabase_env) -> None:
    respx.post(url__regex=r"https://proj\.supabase\.co/storage/.*").mock(
        return_value=httpx.Response(500, text="boom")
    )
    with pytest.raises(RuntimeError):
        await save_photo(b"x", ".png")
