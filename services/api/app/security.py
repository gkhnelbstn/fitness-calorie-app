"""Basit token doğrulama (Faz 0, tek kullanıcı). Public'e geçişte OAuth2/JWT."""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status

from .config import Settings, get_settings


async def require_token(
    authorization: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    expected = f"Bearer {settings.api_token}"
    if authorization != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz veya eksik token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
