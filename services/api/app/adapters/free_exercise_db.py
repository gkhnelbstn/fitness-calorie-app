"""free-exercise-db adapter — egzersiz kataloğu (public domain, auth yok, limit yok).

Kaynak: github.com/yuhonas/free-exercise-db (800+ hareket, JSON + görsel).
Üretimde JSON repoya gömülüp offline okunmalı; burada uzaktan çekim örneği.
"""

from __future__ import annotations

import httpx

from ..config import get_settings
from .base import ExerciseHit


class FreeExerciseDbAdapter:
    source = "free-exercise-db"

    def __init__(self) -> None:
        self._url = get_settings().free_exercise_db_url

    async def fetch_all(self) -> list[ExerciseHit]:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(self._url)
            resp.raise_for_status()
            data = resp.json()

        hits: list[ExerciseHit] = []
        for ex in data:
            muscles = ex.get("primaryMuscles") or []
            hits.append(
                ExerciseHit(
                    name=ex.get("name", ""),
                    source=self.source,
                    primary_muscle=muscles[0] if muscles else None,
                    level=ex.get("level"),
                    equipment=ex.get("equipment"),
                    raw=ex,
                )
            )
        return hits
