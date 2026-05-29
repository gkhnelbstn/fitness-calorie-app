"""Kurallı öneri motoru — enerji dengesi + öğün önerisi + antrenman.

Deterministik ve şeffaf. Profil/hedef eksikse not düşer, çökmek yerine kısmi öneri verir.
Tıbbi tavsiye değildir.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import UserGoal, UserProfile
from ..schemas.recommendation import EnergyInfo, RecommendationRead, WorkoutSuggestion
from .blacklist import blacklist_ids
from .energy import compute_energy
from .intake import daily_intake
from .meal_reco import build_preference, score_recipes
from .recipes import search_recipes

# goal_type → (odak, haftalık dakika, gün planı)
WORKOUT_BY_GOAL: dict[str, tuple[str, int, list[str]]] = {
    "kilo_ver": (
        "kardiyo + kuvvet",
        200,
        [
            "Pzt: 40 dk tempolu yürüyüş",
            "Çar: tam vücut kuvvet",
            "Cum: 40 dk kardiyo",
            "Cmt: kuvvet",
        ],
    ),
    "kas_yap": (
        "kuvvet (split)",
        180,
        ["Pzt: itiş", "Sal: çekiş", "Per: bacak", "Cmt: tam vücut"],
    ),
    "koru": (
        "karışık",
        150,
        ["Pzt: 30 dk kardiyo", "Çar: kuvvet", "Cum: 30 dk kardiyo"],
    ),
}
WHO_NOTE = "Haftada en az 150 dk orta veya 75 dk yüksek şiddet + 2 gün kuvvet (WHO)."
DEFAULT_PROTEIN_PER_KG = 1.6


async def build_recommendation(
    session: AsyncSession, user: UserProfile, goal: UserGoal | None, day: str
) -> RecommendationRead:
    intake = await daily_intake(session, user.id, day)
    notes: list[str] = []

    energy = compute_energy(
        sex=user.sex,
        weight_kg=user.weight_kg,
        height_cm=user.height_cm,
        birth_year=user.birth_year,
        activity_level=user.activity_level,
        goal_type=goal.goal_type if goal else None,
    )

    target_kcal = (goal.target_kcal if goal and goal.target_kcal else None) or (
        energy.target_kcal if energy else None
    )
    remaining = round(target_kcal - intake.kcal, 1) if target_kcal is not None else None
    if target_kcal is None:
        notes.append(
            "Kalori hedefi hesaplanamadı; /api/profile (cinsiyet/kilo/boy/doğum yılı) "
            "ve /api/goal doldur."
        )

    protein_target = goal.target_protein_g if goal else None
    if protein_target is None and user.weight_kg:
        protein_target = round(user.weight_kg * DEFAULT_PROTEIN_PER_KG, 1)
    protein_remaining = (
        round(protein_target - intake.protein_g, 1) if protein_target is not None else None
    )

    # Öğün önerileri — içerik-tabanlı skor (kalori-uyum + protein + tercih affinity).
    blocked = await blacklist_ids(session, user.id)
    recipes = await search_recipes(session, None, blocked)
    if remaining is not None and remaining > 0:
        meal_target: float | None = remaining
    elif target_kcal is not None:
        meal_target = target_kcal / 3.0
    else:
        meal_target = None
    pref = await build_preference(session, user.id)
    scored = score_recipes(
        recipes, pref, meal_target=meal_target, protein_remaining=protein_remaining
    )
    meal_suggestions = [r for r, _ in scored[:3]]
    if pref:
        notes.append("Öneriler geçmiş tercihlerine ve kalan kalorine göre sıralandı.")
    if protein_remaining is not None and protein_remaining > 20:
        notes.append("Protein açığı yüksek; protein ağırlıklı öğünler öne alındı.")

    # Antrenman
    gt = goal.goal_type if goal else "koru"
    focus, weekly, days = WORKOUT_BY_GOAL.get(gt, WORKOUT_BY_GOAL["koru"])
    workout = WorkoutSuggestion(focus=focus, weekly_minutes=weekly, days=days, note=WHO_NOTE)

    if remaining is not None:
        if remaining > 0:
            notes.append(f"Bugün ~{remaining:.0f} kcal daha alabilirsin.")
        elif remaining < 0:
            notes.append(f"Hedefi ~{abs(remaining):.0f} kcal aştın.")
    if protein_remaining is not None and protein_remaining > 0:
        notes.append(f"~{protein_remaining:.0f} g protein açığın var.")

    energy_info = EnergyInfo(
        bmr=energy.bmr if energy else None,
        tdee=energy.tdee if energy else None,
        target_kcal=target_kcal,
        intake_kcal=intake.kcal,
        remaining_kcal=remaining,
        protein_target_g=protein_target,
        protein_intake_g=intake.protein_g,
        protein_remaining_g=protein_remaining,
    )
    return RecommendationRead(
        day=day,
        energy=energy_info,
        meal_suggestions=meal_suggestions,
        workout=workout,
        notes=notes,
    )
