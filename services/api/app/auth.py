"""Supabase JWT doğrulama + kullanıcı çözümleme.

Prod: Supabase Auth'un verdiği JWT'yi lokal olarak doğrular (HS256 proje
secret'ı veya asimetrik projede JWKS). Ek servis çağrısı yok.

Dev/test: SUPABASE_JWT_SECRET/JWKS boşsa legacy `api_token` akışına düşer ve
varsayılan tek kullanıcıyı döndürür — mevcut yerel kurulum ve test paketi
değişmeden çalışır.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .config import get_settings
from .db import get_session
from .models import UserProfile
from .services.user import get_or_create_default_user, get_or_create_user_by_auth

_LEGACY_SUB = "__legacy_default__"


@dataclass
class CurrentUser:
    sub: str
    email: str | None = None


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


@lru_cache
def _jwk_client(jwks_url: str) -> jwt.PyJWKClient:
    return jwt.PyJWKClient(jwks_url)


def decode_token(token: str) -> CurrentUser:
    """Supabase JWT'yi doğrula; sub (UUID) + email çıkar. Hatalar → 401."""
    settings = get_settings()
    alg = settings.supabase_jwt_alg
    try:
        if alg == "HS256":
            key: object = settings.supabase_jwt_secret
        else:
            if not settings.supabase_jwks_url:
                raise _unauthorized("JWKS yapılandırılmamış.")
            key = _jwk_client(settings.supabase_jwks_url).get_signing_key_from_jwt(token).key
        payload = jwt.decode(
            token,
            key,  # type: ignore[arg-type]
            algorithms=[alg],
            audience=settings.supabase_jwt_audience,
            options={"require": ["exp", "sub"]},
            leeway=30,
        )
    except jwt.ExpiredSignatureError as e:
        raise _unauthorized("Token süresi dolmuş.") from e
    except jwt.InvalidAudienceError as e:
        raise _unauthorized("Geçersiz audience.") from e
    except jwt.PyJWTError as e:
        raise _unauthorized("Geçersiz token.") from e
    return CurrentUser(sub=str(payload["sub"]), email=payload.get("email"))


async def get_current_user(authorization: str | None = Header(default=None)) -> CurrentUser:
    settings = get_settings()
    if authorization is None or not authorization.startswith("Bearer "):
        raise _unauthorized("Geçersiz veya eksik token.")
    token = authorization.removeprefix("Bearer ").strip()

    if not settings.supabase_auth_enabled:
        # Legacy tek-kullanıcı akışı (dev/test): sabit api_token.
        if token != settings.api_token:
            raise _unauthorized("Geçersiz veya eksik token.")
        return CurrentUser(sub=_LEGACY_SUB)

    return decode_token(token)


async def get_current_profile(
    cu: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserProfile:
    if cu.sub == _LEGACY_SUB:
        return await get_or_create_default_user(session)
    return await get_or_create_user_by_auth(session, cu.sub, cu.email)
