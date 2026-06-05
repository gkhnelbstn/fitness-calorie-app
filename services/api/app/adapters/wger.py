"""wger adapter — açık REST API (auth yok).

ingredient?language=16 → Türkçe besin (Open Food Facts kaynaklı, ~2300 kayıt,
per_100g enerji/makro). Sayfalı (next URL ile). Toplu seed için kullanılır.
"""

from __future__ import annotations

import httpx

from ..config import get_settings

# wger Türkçe dil id'si (api/v2/language).
TURKISH_LANGUAGE_ID = 16


def _to_float(value: object) -> float | None:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


class WgerAdapter:
    source = "wger"

    def __init__(self) -> None:
        self._base = get_settings().wger_base_url.rstrip("/")

    async def turkish_ingredients(self, *, limit: int = 200) -> list[dict]:
        """Türkçe besinleri sayfalayarak çek. Her kayıt: name + per_100g makro.

        Döner: [{name, kcal, protein_g, carb_g, fat_g, code}] (limit'e kadar).
        """
        out: list[dict] = []
        url: str | None = (
            f"{self._base}/api/v2/ingredient/?language={TURKISH_LANGUAGE_ID}&format=json&limit=100"
        )
        async with httpx.AsyncClient(timeout=20) as client:
            while url and len(out) < limit:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                for it in data.get("results", []):
                    name = (it.get("name") or "").strip()
                    kcal = _to_float(it.get("energy"))
                    if not name or kcal is None:
                        continue
                    out.append(
                        {
                            "name": name,
                            "kcal": kcal,
                            "protein_g": _to_float(it.get("protein")),
                            "carb_g": _to_float(it.get("carbohydrates")),
                            "fat_g": _to_float(it.get("fat")),
                            "code": it.get("code"),
                        }
                    )
                url = data.get("next")
        return out[:limit]
