"""Enerji hesabı — BMR (Mifflin-St Jeor), TDEE, hedef kalori bandı.

Tıbbi tavsiye değildir; yaklaşık değerler.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

ACTIVITY_FACTORS: dict[str, float] = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}
DEFAULT_ACTIVITY = "moderate"

GOAL_DELTA: dict[str, int] = {
    "kilo_ver": -500,
    "koru": 0,
    "kas_yap": 300,
}

_MALE = {"erkek", "male", "m", "e"}


@dataclass
class EnergyResult:
    bmr: float
    tdee: float
    target_kcal: int
    target_low: int
    target_high: int


def _age(birth_year: int) -> int:
    return max(0, date.today().year - birth_year)


def bmr_mifflin(sex: str, weight_kg: float, height_cm: float, age: int) -> float:
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    base += 5 if (sex or "").strip().lower() in _MALE else -161
    return round(base, 1)


def compute_energy(
    *,
    sex: str | None,
    weight_kg: float | None,
    height_cm: float | None,
    birth_year: int | None,
    activity_level: str | None,
    goal_type: str | None,
) -> EnergyResult | None:
    """Profil eksikse None döner."""
    if sex is None or weight_kg is None or height_cm is None or birth_year is None:
        return None

    bmr = bmr_mifflin(sex, weight_kg, height_cm, _age(birth_year))
    factor = ACTIVITY_FACTORS.get(
        (activity_level or DEFAULT_ACTIVITY), ACTIVITY_FACTORS[DEFAULT_ACTIVITY]
    )
    tdee = round(bmr * factor, 1)
    target = int(round(tdee + GOAL_DELTA.get(goal_type or "koru", 0)))
    return EnergyResult(
        bmr=bmr,
        tdee=tdee,
        target_kcal=target,
        target_low=target - 100,
        target_high=target + 100,
    )
