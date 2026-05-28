"""Yemek planı şemaları."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PlanPreviewRequest(BaseModel):
    text: str = Field(
        ...,
        examples=["# Gün 0\n- Kahvaltı: 2 yumurta, 1 simit\n- Öğle: 1 kase pilav, 1 ayran\n"],
    )


class PlanEntryRead(BaseModel):
    day_offset: int
    meal_type: str
    raw_text: str


class PlanPreviewResponse(BaseModel):
    entries: list[PlanEntryRead]


class PlanApplyRequest(BaseModel):
    text: str
    base_date: str | None = Field(default=None, examples=["2026-05-28"])  # YYYY-MM-DD


class PlanApplyResponse(BaseModel):
    base_date: str
    created_meal_ids: list[int]
    entries: list[PlanEntryRead]
