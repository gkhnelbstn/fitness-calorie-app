"""Yemek endpoint'i — token zorunluluğu ve temel doğrulama."""

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app

client = TestClient(app)
AUTH = {"Authorization": f"Bearer {get_settings().api_token}"}


def test_meals_requires_token() -> None:
    resp = client.post("/api/meals", json={"raw_text": "1 ayran"})
    assert resp.status_code == 401


def test_meals_create_stub() -> None:
    resp = client.post(
        "/api/meals",
        headers=AUTH,
        json={"meal_type": "ogle", "items": [{"raw_name": "ayran", "kcal": 60}]},
    )
    assert resp.status_code == 201
    assert resp.json()["total_kcal"] == 60


def test_meals_empty_payload_rejected() -> None:
    resp = client.post("/api/meals", headers=AUTH, json={})
    assert resp.status_code == 422
