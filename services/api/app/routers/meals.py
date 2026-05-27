"""Yemek kaydı endpoint'leri (Faz 0 stub).

Faz 1'de: raw_text -> LLM/kurallı parser -> canonical resolver -> besin değeri.
Şimdilik yapılandırılmış 'items' kabul edilir; ayrıştırma henüz bağlı değil.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status

from ..schemas.meal import MealCreate, MealRead
from ..security import require_token

router = APIRouter(prefix="/api/meals", tags=["meals"], dependencies=[Depends(require_token)])


@router.post("", response_model=MealRead, status_code=status.HTTP_201_CREATED)
async def create_meal(payload: MealCreate) -> MealRead:
    if not payload.raw_text and not payload.items:
        raise HTTPException(status_code=422, detail="raw_text veya items dolu olmalı.")

    # TODO(Faz 1): raw_text -> ayrıştırma + canonical eşleştirme + besin değeri.
    total_kcal = sum((it.kcal or 0) for it in payload.items) or None
    return MealRead(
        id=0,  # stub: henüz kalıcı kayıt yok
        eaten_at=datetime.now(UTC),
        meal_type=payload.meal_type,
        raw_text=payload.raw_text,
        total_kcal=total_kcal,
        items=payload.items,
    )


@router.get("", response_model=list[MealRead])
async def list_meals(date: str | None = None) -> list[MealRead]:
    # TODO(Faz 1): DB'den tarihe göre listele.
    return []
