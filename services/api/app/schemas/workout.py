"""Antrenman log şemaları."""

from __future__ import annotations

from pydantic import BaseModel, Field


class WorkoutLogCreate(BaseModel):
    template_slug: str = Field(..., examples=["bench-press"])
    sets: int | None = None
    reps: str | None = None
    minutes: int = Field(default=30, ge=1)


class WorkoutLogRead(BaseModel):
    id: int
    template_slug: str
    name_tr: str
    sets: int | None = None
    reps: str | None = None
    minutes: int
    kcal: int | None = None
    done: bool = True
