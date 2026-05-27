"""Profil + hedef endpoint'leri."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import UserGoal
from ..schemas.profile import GoalRead, GoalUpdate, ProfileRead, ProfileUpdate
from ..security import require_token
from ..services.user import get_or_create_default_user

router = APIRouter(prefix="/api", tags=["profile"], dependencies=[Depends(require_token)])


def _profile_read(user) -> ProfileRead:
    return ProfileRead(
        id=user.id,
        name=user.name,
        sex=user.sex,
        birth_year=user.birth_year,
        height_cm=user.height_cm,
        weight_kg=user.weight_kg,
        activity_level=user.activity_level,
        locale=user.locale,
    )


@router.get("/profile", response_model=ProfileRead)
async def get_profile(session: AsyncSession = Depends(get_session)) -> ProfileRead:
    user = await get_or_create_default_user(session)
    return _profile_read(user)


@router.put("/profile", response_model=ProfileRead)
async def update_profile(
    payload: ProfileUpdate, session: AsyncSession = Depends(get_session)
) -> ProfileRead:
    user = await get_or_create_default_user(session)
    for field, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(user, field, value)
    await session.commit()
    await session.refresh(user)
    return _profile_read(user)


async def _active_goal(session: AsyncSession, user_id: int) -> UserGoal | None:
    return (
        (
            await session.execute(
                select(UserGoal)
                .where(UserGoal.user_id == user_id, UserGoal.active.is_(True))
                .order_by(UserGoal.id.desc())
            )
        )
        .scalars()
        .first()
    )


@router.get("/goal", response_model=GoalRead)
async def get_goal(session: AsyncSession = Depends(get_session)) -> GoalRead:
    user = await get_or_create_default_user(session)
    goal = await _active_goal(session, user.id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Aktif hedef yok.")
    return GoalRead(
        id=goal.id,
        goal_type=goal.goal_type,
        target_kcal=goal.target_kcal,
        target_protein_g=goal.target_protein_g,
        active=goal.active,
    )


@router.put("/goal", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
async def set_goal(payload: GoalUpdate, session: AsyncSession = Depends(get_session)) -> GoalRead:
    user = await get_or_create_default_user(session)
    # Önceki aktif hedefleri pasifleştir
    await session.execute(update(UserGoal).where(UserGoal.user_id == user.id).values(active=False))
    goal = UserGoal(
        user_id=user.id,
        goal_type=payload.goal_type,
        target_kcal=payload.target_kcal,
        target_protein_g=payload.target_protein_g,
        active=True,
    )
    session.add(goal)
    await session.commit()
    await session.refresh(goal)
    return GoalRead(
        id=goal.id,
        goal_type=goal.goal_type,
        target_kcal=goal.target_kcal,
        target_protein_g=goal.target_protein_g,
        active=goal.active,
    )
