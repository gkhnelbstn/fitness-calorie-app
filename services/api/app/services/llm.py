"""NVIDIA LLM istemcisi — Türkçe yemek metnini {isim,miktar,birim}'e çevirir.

Demir kural: LLM yalnızca sınıflandırır/ayrıştırır. Kalori/makro ASLA LLM'den.
Anahtar yoksa veya hata olursa None döner → çağıran kurallı parser'a düşer.
"""

from __future__ import annotations

import json

import httpx

from ..config import get_settings
from .meal_parser import ParsedItem

_SYSTEM = (
    "Sen bir Türkçe beslenme asistanısın. Kullanıcının yediği yemeği anlatan metni "
    "JSON'a çevir. SADECE şu formatta geçerli JSON döndür, başka hiçbir şey yazma:\n"
    '{"items": [{"name": "yemek adı", "quantity": sayı_veya_null, "unit": "birim_veya_null"}]}\n'
    "Kalori, makro veya besin değeri ASLA üretme. Sadece isim/miktar/birim çıkar."
)


def _strip_fences(content: str) -> str:
    s = content.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[-1] if "\n" in s else s
        s = s.removeprefix("json").strip()
        if s.endswith("```"):
            s = s[:-3].strip()
    return s


def _parse_content(content: str) -> list[ParsedItem]:
    data = json.loads(_strip_fences(content))
    out: list[ParsedItem] = []
    for it in data.get("items", []):
        name = (it.get("name") or "").strip()
        if not name:
            continue
        qty = it.get("quantity")
        out.append(
            ParsedItem(
                name=name,
                quantity=float(qty) if isinstance(qty, (int, float)) else None,
                unit=(it.get("unit") or None),
            )
        )
    return out


class LlmExtractor:
    def __init__(self) -> None:
        s = get_settings()
        self._key = s.nvidia_api_key
        self._url = f"{s.nvidia_base_url}/chat/completions"
        self._model = s.nvidia_model

    async def extract(self, text: str) -> list[ParsedItem] | None:
        if not self._key.strip():
            return None
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": text},
            ],
            "temperature": 0.2,
            "max_tokens": 512,
            "stream": False,
        }
        headers = {"Authorization": f"Bearer {self._key}", "Accept": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(self._url, json=payload, headers=headers)
                resp.raise_for_status()
                content = resp.json()["choices"][0]["message"]["content"]
            return _parse_content(content)
        except (httpx.HTTPError, KeyError, ValueError, json.JSONDecodeError):
            # Sessiz fallback — çağıran kurallı parser'a düşer.
            return None
