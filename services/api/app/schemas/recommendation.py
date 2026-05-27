"""Öneri motoru şemaları."""

from __future__ import annotations

from pydantic import BaseModel

from .recipe import RecipeRead


class EnergyInfo(BaseModel):
    bmr: float | None = None
    tdee: float | None = None
    target_kcal: int | None = None
    intake_kcal: float = 0.0
    remaining_kcal: float | None = None
    protein_target_g: float | None = None
    protein_intake_g: float = 0.0
    protein_remaining_g: float | None = None


class WorkoutSuggestion(BaseModel):
    focus: str
    weekly_minutes: int
    days: list[str]
    note: str


class RecommendationRead(BaseModel):
    id: int | None = None
    day: str
    energy: EnergyInfo
    meal_suggestions: list[RecipeRead] = []
    workout: WorkoutSuggestion
    notes: list[str] = []


class FeedbackCreate(BaseModel):
    recommendation_id: int
    action: str  # accepted | rejected | edited
    note: str | None = None
