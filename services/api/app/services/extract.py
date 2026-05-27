"""Yemek metni → ParsedItem listesi. Önce LLM, olmazsa kurallı parser."""

from __future__ import annotations

from .llm import LlmExtractor
from .meal_parser import ParsedItem, parse_meal_text


async def extract_items(text: str) -> list[ParsedItem]:
    items = await LlmExtractor().extract(text)
    if not items:  # None (kapalı/hata) veya boş → kurallı fallback
        items = parse_meal_text(text)
    return items
