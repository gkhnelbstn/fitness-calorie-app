"""Sıradaki öğün için içerik-tabanlı tarif sıralama (tercih + kalori farkında).

Araştırma tasarımı (content-based, tek kullanıcı, ML yok, determinist):
  Score = wc·CalFit + wp·ProteinFit + wa·Affinity
- CalFit: tarifin kalorisinin kalan/öğün-hedefine yakınlığı.
- ProteinFit: protein açığı varsa protein-etiketli tariflere kredi (RecipeRead makro
  taşımadığından etiket-proxy).
- Affinity: kullanıcının geçmişte sık+yakın yediği malzemelerle (canonical) örtüşme.
  Tercih edilen yemekler/türevleri ödüllendirilir → tekrar serbest (ceza yok).

Tercih ağırlığı: frekans × üstel zaman sönümü  w = exp(-λ · gün).  (λ = ln2 / yarı_ömür)
LLM kullanılmaz; sıralama denetlenebilir/deterministiktir.
"""

from __future__ import annotations

import math
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import MealLog, MealLogItem
from ..schemas.recipe import RecipeRead

HALF_LIFE_DAYS = 21.0
_LAMBDA = math.log(2) / HALF_LIFE_DAYS
W_CAL, W_PROTEIN, W_AFFINITY = 0.40, 0.25, 0.35


async def build_preference(session: AsyncSession, user_id: int) -> dict[int, float]:
    """canonical_id → tercih ağırlığı (frekans × üstel zaman sönümü)."""
    rows = (
        await session.execute(
            select(MealLogItem.canonical_id, MealLog.eaten_at)
            .join(MealLog, MealLogItem.meal_log_id == MealLog.id)
            .where(MealLog.user_id == user_id, MealLogItem.canonical_id.is_not(None))
        )
    ).all()
    now = datetime.now(UTC)
    pref: dict[int, float] = {}
    for canonical_id, eaten_at in rows:
        if canonical_id is None or eaten_at is None:
            continue
        ea = eaten_at if eaten_at.tzinfo else eaten_at.replace(tzinfo=UTC)
        days = max(0.0, (now - ea).total_seconds() / 86400.0)
        pref[canonical_id] = pref.get(canonical_id, 0.0) + math.exp(-_LAMBDA * days)
    return pref


def _cal_fit(recipe_kcal: float | None, meal_target: float | None) -> float:
    if recipe_kcal is None or not meal_target or meal_target <= 0:
        return 0.5  # bilgi yoksa nötr
    return max(0.0, 1.0 - abs(meal_target - recipe_kcal) / meal_target)


def _protein_fit(tags: list[str], protein_remaining: float | None) -> float:
    if protein_remaining is None or protein_remaining <= 0:
        return 0.5  # açık yok → nötr
    return 1.0 if "protein" in tags else 0.4


def _affinity(recipe: RecipeRead, pref: dict[int, float], pref_total: float) -> float:
    if pref_total <= 0:
        return 0.0
    s = sum(pref.get(i.canonical_id, 0.0) for i in recipe.ingredients if i.canonical_id is not None)
    return min(1.0, s / pref_total)


def score_recipes(
    recipes: list[RecipeRead],
    pref: dict[int, float],
    *,
    meal_target: float | None,
    protein_remaining: float | None,
) -> list[tuple[RecipeRead, float]]:
    """Tarifleri skora göre azalan sırala. (recipe, score) döner."""
    pref_total = sum(pref.values())
    scored: list[tuple[RecipeRead, float]] = []
    for r in recipes:
        score = (
            W_CAL * _cal_fit(r.total_kcal, meal_target)
            + W_PROTEIN * _protein_fit(r.tags, protein_remaining)
            + W_AFFINITY * _affinity(r, pref, pref_total)
        )
        scored.append((r, round(score, 4)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored
