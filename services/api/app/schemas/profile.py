"""Profil + hedef şemaları."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProfileUpdate(BaseModel):
    name: str | None = None
    sex: str | None = Field(default=None, examples=["erkek"])
    birth_year: int | None = Field(default=None, examples=[1995])
    height_cm: float | None = Field(default=None, examples=[178])
    weight_kg: float | None = Field(default=None, examples=[80])
    activity_level: str | None = Field(default=None, examples=["moderate"])


class ProfileRead(BaseModel):
    id: int
    name: str
    sex: str | None = None
    birth_year: int | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    activity_level: str | None = None
    locale: str = "tr"


class GoalUpdate(BaseModel):
    goal_type: str = Field(..., examples=["kilo_ver"])  # kilo_ver | koru | kas_yap
    target_kcal: int | None = None
    target_protein_g: float | None = None


class GoalRead(BaseModel):
    id: int
    goal_type: str
    target_kcal: int | None = None
    target_protein_g: float | None = None
    active: bool = True


class GoalPlanUpdate(BaseModel):
    """Hedef sihirbazı + antrenman planı tercihleri (UserPreference'ta saklanır).

    Tüm alanlar opsiyonel: PUT kısmi gelir ve mevcut planla birleştirilir.
    """

    start_weight: float | None = None
    target_weight: float | None = None
    weeks: int | None = None
    pace: float | None = None
    days_per_week: int | None = None
    training_days: list[str] | None = None
