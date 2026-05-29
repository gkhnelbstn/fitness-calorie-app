"""NVIDIA LLM çeviri (TR↔EN). Anahtar yoksa metni aynen döndürür.

Tarif/besin import + canlı arama sorgusu için. Sessiz fallback: hata/anahtarsız → orijinal.
"""

from __future__ import annotations

import httpx

from ..config import get_settings

_SYS_TR = (
    "Sen profesyonel bir çevirmensin. Verilen İngilizce gıda/yemek metnini "
    "doğal, kısa Türkçeye çevir. SADECE çeviriyi döndür; açıklama, tırnak veya "
    "ek metin ekleme."
)
_SYS_EN = (
    "You are a professional translator. Translate the given Turkish food/recipe "
    "text into short, natural English. Return ONLY the translation; no quotes, "
    "no explanation, no extra text."
)


class Translator:
    def __init__(self) -> None:
        s = get_settings()
        self._key = s.nvidia_api_key
        self._url = f"{s.nvidia_base_url}/chat/completions"
        self._model = s.nvidia_model
        self._cache: dict[str, str] = {}

    @property
    def enabled(self) -> bool:
        return bool(self._key.strip())

    async def _translate(self, text: str, system: str, cache_prefix: str) -> str:
        text = text.strip()
        if not text or not self.enabled:
            return text
        ck = f"{cache_prefix}:{text}"
        if ck in self._cache:
            return self._cache[ck]
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": text},
            ],
            "temperature": 0.1,
            "max_tokens": 256,
            "stream": False,
        }
        headers = {"Authorization": f"Bearer {self._key}", "Accept": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(self._url, json=payload, headers=headers)
                resp.raise_for_status()
                out = resp.json()["choices"][0]["message"]["content"].strip()
        except (httpx.HTTPError, KeyError, ValueError):
            return text
        result = out or text
        self._cache[ck] = result
        return result

    async def to_turkish(self, text: str) -> str:
        return await self._translate(text, _SYS_TR, "tr")

    async def to_english(self, text: str) -> str:
        return await self._translate(text, _SYS_EN, "en")
