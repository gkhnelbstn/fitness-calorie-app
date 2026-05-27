"""Tek kullanıcı (Faz 0/1) — varsayılan kullanıcıyı getir/oluştur."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import UserProfile

DEFAULT_USER_NAME = "Gökhan"


async def get_or_create_default_user(session: AsyncSession) -> UserProfile:
    user = (
        await session.execute(select(UserProfile).order_by(UserProfile.id).limit(1))
    ).scalar_one_or_none()
    if user is None:
        user = UserProfile(name=DEFAULT_USER_NAME, locale="tr")
        session.add(user)
        await session.flush()
    return user
