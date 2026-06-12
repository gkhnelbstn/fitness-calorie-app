"""Kullanıcı çözümleme — legacy varsayılan kullanıcı + Supabase auth eşlemesi."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
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


async def get_or_create_user_by_auth(
    session: AsyncSession, sub: str, email: str | None
) -> UserProfile:
    """Supabase kullanıcı UUID'sini (sub) lokal UserProfile'a eşle; yoksa oluştur."""
    user = (
        await session.execute(select(UserProfile).where(UserProfile.supabase_uid == sub))
    ).scalar_one_or_none()
    if user is not None:
        return user

    # Anonim (misafir) kullanıcıların email'i boş string gelir; "" benzersizlik
    # kısıtını ihlal eder (ikinci misafir → 500) ve yanlış hesaba bağlanmaya yol
    # açar. Boş email'i NULL'a indir: NULL'lar unique kısıtını ihlal etmez.
    email = email or None
    name = (email or "").split("@")[0] or "Misafir"
    user = UserProfile(name=name, email=email, supabase_uid=sub, locale="tr")
    try:
        # SAVEPOINT: çakışmada yalnız bu insert geri alınır, request transaction'ı yaşar.
        async with session.begin_nested():
            session.add(user)
    except IntegrityError:
        # Yarış (aynı sub iki istekte) VEYA email zaten kayıtlı (hesap bağlama).
        user = (
            await session.execute(select(UserProfile).where(UserProfile.supabase_uid == sub))
        ).scalar_one_or_none()
        if user is None and email:
            user = (
                await session.execute(select(UserProfile).where(UserProfile.email == email))
            ).scalar_one_or_none()
            if user is not None and user.supabase_uid is None:
                user.supabase_uid = sub  # mevcut email hesabını Supabase kimliğine bağla
                await session.flush()
        if user is None:
            raise
    return user
