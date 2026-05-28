"""İngilizce → Türkçe çeviri (NVIDIA LLM). Anahtar yoksa metni aynen döndürür.

Tarif/besin import'unda kullanılır. Sessiz fallback: hata/anahtarsız → orijinal.
"""

from __future__ import annotations

import httpx

from ..config import get_settings

_SYSTEM = (
    "Sen profesyonel bir çevirmensin. Verilen İngilizce gıda/yemek metnini "
    "doğal, kısa Türkçeye çevir. SADECE çeviriyi döndür; açıklama, tırnak veya "
    "ek metin ekleme."
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

    async def to_turkish(self, text: str) -> str:
        text = text.strip()
        if not text or not self.enabled:
            return text
        if text in self._cache:
            return self._cache[text]
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": _SYSTEM},
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
        self._cache[text] = result
        return result
