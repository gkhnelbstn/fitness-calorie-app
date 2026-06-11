"""Antrenman endpoint'leri — katalog, plan, günlük log (frontend Antrenman ekranı)."""

from __future__ import annotations

from datetime import date as date_cls
from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, select
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import CurrentUser, get_current_profile, get_current_user
from ..data import workouts as W
from ..db import get_session
from ..models import UserGoal, WorkoutLog
from ..schemas.workout import WorkoutLogCreate, WorkoutLogRead

router = APIRouter(prefix="/api", tags=["workouts"], dependencies=[Depends(get_current_user)])


@router.get("/workouts")
async def list_workouts(
    muscle: str | None = None,
    level: str | None = None,
    equipment: str | None = None,
    equipment_type: str | None = None,
    q: str | None = None,
) -> list[dict[str, Any]]:
    return W.filter_exercises(
        muscle=muscle, level=level, equipment=equipment, equipment_type=equipment_type, q=q
    )


@router.get("/workout-plan")
async def workout_plan(
    goal: str | None = None,
    level: str | None = None,
    days_per_week: int | None = None,
    training_days: list[str] = Query(default_factory=list),
    cu: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    user = await get_current_profile(cu, session)
    if goal is None:
        g = (
            (
                await session.execute(
                    select(UserGoal)
                    .where(UserGoal.user_id == user.id, UserGoal.active.is_(True))
                    .order_by(UserGoal.id.desc())
                )
            )
            .scalars()
            .first()
        )
        goal = g.goal_type if g else "koru"
    if level is None:
        level = "beginner" if user.activity_level == "sedentary" else "intermediate"
    return W.build_plan(goal, level, days_per_week or 4, training_days or None)


def _to_read(w: WorkoutLog) -> WorkoutLogRead:
    return WorkoutLogRead(
        id=w.id,
        template_slug=w.template_slug,
        name_tr=w.name_tr,
        sets=w.sets,
        reps=w.reps,
        minutes=w.minutes,
        kcal=w.kcal,
        done=w.done,
    )


@router.get("/workout-logs", response_model=list[WorkoutLogRead])
async def list_logs(
    date: str | None = None,
    cu: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[WorkoutLogRead]:
    day = date or date_cls.today().isoformat()
    user = await get_current_profile(cu, session)
    rows = (
        (
            await session.execute(
                select(WorkoutLog)
                .where(WorkoutLog.user_id == user.id, WorkoutLog.day == day)
                .order_by(WorkoutLog.id)
            )
        )
        .scalars()
        .all()
    )
    return [_to_read(w) for w in rows]


@router.post("/workout-logs", response_model=WorkoutLogRead, status_code=status.HTTP_201_CREATED)
async def add_log(
    payload: WorkoutLogCreate,
    date: str | None = None,
    cu: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> WorkoutLogRead:
    day = date or date_cls.today().isoformat()
    user = await get_current_profile(cu, session)
    catalog = {e["slug"]: e for e in W.EXERCISES}
    ex = catalog.get(payload.template_slug)
    name_tr = ex["name_tr"] if ex else payload.template_slug
    kcal = W.burned_kcal(payload.template_slug, payload.minutes, user.weight_kg or 70)
    log = WorkoutLog(
        user_id=user.id,
        day=day,
        template_slug=payload.template_slug,
        name_tr=name_tr,
        sets=payload.sets,
        reps=payload.reps,
        minutes=payload.minutes,
        kcal=kcal,
        done=True,
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return _to_read(log)


@router.delete("/workout-logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_log(
    log_id: int,
    cu: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    user = await get_current_profile(cu, session)
    result = await session.execute(
        delete(WorkoutLog).where(WorkoutLog.id == log_id, WorkoutLog.user_id == user.id)
    )
    await session.commit()
    if cast("CursorResult[Any]", result).rowcount == 0:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı.")
