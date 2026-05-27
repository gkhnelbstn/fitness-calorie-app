"""Kara liste şemaları."""

from __future__ import annotations

from pydantic import BaseModel, Field


class BlacklistAdd(BaseModel):
    name: str = Field(..., examples=["sarımsak"])


class BlacklistItem(BaseModel):
    canonical_id: int
    slug: str
    name_tr: str
