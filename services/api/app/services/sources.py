"""Kaynak (source_attribution) get-or-create — lisans/atıf takibi için."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import SourceAttribution


async def get_or_create_source(
    session: AsyncSession,
    *,
    name: str,
    url: str | None = None,
    license: str | None = None,
    license_mode: str | None = None,
) -> SourceAttribution:
    src = (
        await session.execute(select(SourceAttribution).where(SourceAttribution.name == name))
    ).scalar_one_or_none()
    if src is not None:
        return src
    src = SourceAttribution(name=name, url=url, license=license, license_mode=license_mode)
    session.add(src)
    await session.flush()
    return src
