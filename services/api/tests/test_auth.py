"""Supabase JWT doğrulama + çok-kullanıcı izolasyonu.

decode_token unit testleri pyjwt ile HS256 token üretir; izolasyon testleri
gerçek HTTP akışıyla (client fixture) iki farklı sub'ın verisinin ayrıştığını
doğrular. SUPABASE_JWT_SECRET set edilince legacy api_token akışı devre dışı.
"""

from __future__ import annotations

import time

import jwt
import pytest
from fastapi import HTTPException

from app import config
from app.auth import decode_token, get_current_user
from app.models import UserProfile
from app.services.user import get_or_create_user_by_auth

SECRET = "test-jwt-secret"


def _mint(
    sub: str = "11111111-1111-1111-1111-111111111111",
    *,
    secret: str = SECRET,
    aud: str = "authenticated",
    exp_delta: int = 3600,
    email: str | None = "u@example.com",
    extra: dict | None = None,
) -> str:
    payload: dict = {"sub": sub, "aud": aud, "exp": int(time.time()) + exp_delta}
    if email:
        payload["email"] = email
    if extra:
        payload.update(extra)
    return jwt.encode(payload, secret, algorithm="HS256")


@pytest.fixture
def supabase_env(monkeypatch):
    monkeypatch.setenv("SUPABASE_JWT_SECRET", SECRET)
    config.get_settings.cache_clear()
    yield
    config.get_settings.cache_clear()


# --------------------------------------------------------------------------- #
# decode_token unit
# --------------------------------------------------------------------------- #
def test_decode_valid_token(supabase_env) -> None:
    cu = decode_token(_mint())
    assert cu.sub == "11111111-1111-1111-1111-111111111111"
    assert cu.email == "u@example.com"


def test_decode_token_without_email(supabase_env) -> None:
    cu = decode_token(_mint(email=None))
    assert cu.email is None


def test_decode_expired_token_401(supabase_env) -> None:
    with pytest.raises(HTTPException) as e:
        decode_token(_mint(exp_delta=-120))
    assert e.value.status_code == 401


def test_decode_bad_audience_401(supabase_env) -> None:
    with pytest.raises(HTTPException) as e:
        decode_token(_mint(aud="hacker"))
    assert e.value.status_code == 401


def test_decode_bad_signature_401(supabase_env) -> None:
    with pytest.raises(HTTPException) as e:
        decode_token(_mint(secret="wrong-secret"))
    assert e.value.status_code == 401


def test_decode_missing_sub_401(supabase_env) -> None:
    token = jwt.encode(
        {"aud": "authenticated", "exp": int(time.time()) + 600}, SECRET, algorithm="HS256"
    )
    with pytest.raises(HTTPException) as e:
        decode_token(token)
    assert e.value.status_code == 401


# --------------------------------------------------------------------------- #
# get_current_user
# --------------------------------------------------------------------------- #
async def test_missing_header_401() -> None:
    with pytest.raises(HTTPException) as e:
        await get_current_user(None)
    assert e.value.status_code == 401


async def test_legacy_mode_valid_token() -> None:
    # Supabase kapalı (secret yok) → api_token kabul, legacy sub döner.
    cu = await get_current_user(f"Bearer {config.get_settings().api_token}")
    assert cu.sub == "__legacy_default__"


async def test_legacy_mode_wrong_token_401() -> None:
    with pytest.raises(HTTPException) as e:
        await get_current_user("Bearer yanlis-token")
    assert e.value.status_code == 401


async def test_supabase_mode_rejects_legacy_token(supabase_env) -> None:
    # JWT etkinken sabit api_token artık geçmez.
    with pytest.raises(HTTPException) as e:
        await get_current_user(f"Bearer {config.get_settings().api_token}")
    assert e.value.status_code == 401


# --------------------------------------------------------------------------- #
# Kullanıcı eşleme
# --------------------------------------------------------------------------- #
async def test_auth_links_existing_email_account(session) -> None:
    """Aynı email'le kayıtlı (uid'siz) hesap, Supabase girişine bağlanır — kopya açılmaz."""
    legacy = UserProfile(name="eski", email="link@x.io")
    session.add(legacy)
    await session.flush()

    sub = "cccccccc-0000-0000-0000-000000000003"
    linked = await get_or_create_user_by_auth(session, sub, "link@x.io")
    assert linked.id == legacy.id
    assert linked.supabase_uid == sub


# --------------------------------------------------------------------------- #
# HTTP akışı: kullanıcı oluşturma + izolasyon
# --------------------------------------------------------------------------- #
async def test_user_isolation_meals(client, supabase_env) -> None:
    ha = {
        "Authorization": f"Bearer {_mint('aaaaaaaa-0000-0000-0000-000000000001', email='a@x.io')}"
    }
    hb = {
        "Authorization": f"Bearer {_mint('bbbbbbbb-0000-0000-0000-000000000002', email='b@x.io')}"
    }

    meal = {"items": [{"raw_name": "elma", "quantity": 1, "unit": "adet", "kcal": 52}]}
    r = await client.post("/api/meals", json=meal, headers=ha)
    assert r.status_code == 201

    # A kendi öğününü görür, B görmez.
    a_meals = (await client.get("/api/meals", headers=ha)).json()
    b_meals = (await client.get("/api/meals", headers=hb)).json()
    assert len(a_meals) == 1
    assert b_meals == []


async def test_feedback_ownership_guard(client, supabase_env) -> None:
    ha = {
        "Authorization": f"Bearer {_mint('aaaaaaaa-0000-0000-0000-000000000001', email='a@x.io')}"
    }
    hb = {
        "Authorization": f"Bearer {_mint('bbbbbbbb-0000-0000-0000-000000000002', email='b@x.io')}"
    }

    rec = (await client.get("/api/recommendations", headers=ha)).json()
    # B, A'nın önerisine geri bildirim veremez (404 — varlık sızdırılmaz).
    resp = await client.post(
        "/api/recommendations/feedback",
        json={"recommendation_id": rec["id"], "action": "accept"},
        headers=hb,
    )
    assert resp.status_code == 404
    # A verebilir.
    ok = await client.post(
        "/api/recommendations/feedback",
        json={"recommendation_id": rec["id"], "action": "accept"},
        headers=ha,
    )
    assert ok.status_code == 201
