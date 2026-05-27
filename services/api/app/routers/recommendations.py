"""Öneri endpoint'leri — günlük öneri + geri bildirim."""

from __future__ import annotations

from datetime import date as date_cls

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import Recommendation, RecommendationFeedback, UserGoal
from ..schemas.recommendation import FeedbackCreate, RecommendationRead
from ..security import require_token
from ..services.recommend import build_recommendation
from ..services.user import get_or_create_default_user

router = APIRouter(
    prefix="/api/recommendations", tags=["recommendations"], dependencies=[Depends(require_token)]
)


@router.get("", response_model=RecommendationRead)
async def get_recommendation(
    date: str | None = None, session: AsyncSession = Depends(get_session)
) -> RecommendationRead:
    day = date or date_cls.today().isoformat()
    user = await get_or_create_default_user(session)
    goal = (
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

    rec = await build_recommendation(session, user, goal, day)

    row = Recommendation(user_id=user.id, kind="daily", payload=rec.model_dump(mode="json"))
    session.add(row)
    await session.commit()
    await session.refresh(row)
    rec.id = row.id
    return rec


@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def add_feedback(
    payload: FeedbackCreate, session: AsyncSession = Depends(get_session)
) -> dict:
    rec = await session.get(Recommendation, payload.recommendation_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Öneri bulunamadı.")
    session.add(
        RecommendationFeedback(
            recommendation_id=payload.recommendation_id,
            action=payload.action,
            note=payload.note,
        )
    )
    await session.commit()
    return {"status": "ok"}
