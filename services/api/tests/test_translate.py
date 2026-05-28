"""Çeviri servisi — anahtarsız identity + respx-mock'lu çeviri + cache."""

import httpx
import respx

from app.services.translate import Translator


async def test_identity_without_key() -> None:
    t = Translator()
    t._key = ""
    assert await t.to_turkish("Tomato Soup") == "Tomato Soup"


async def test_empty_text() -> None:
    t = Translator()
    t._key = "x"
    assert await t.to_turkish("   ") == ""


@respx.mock
async def test_translate_and_cache() -> None:
    t = Translator()
    t._key = "test-key"
    route = respx.post(t._url).mock(
        return_value=httpx.Response(
            200,
            json={"choices": [{"message": {"content": "Domates Çorbası"}}]},
        )
    )
    first = await t.to_turkish("Tomato Soup")
    second = await t.to_turkish("Tomato Soup")
    assert first == "Domates Çorbası"
    assert second == "Domates Çorbası"
    assert route.call_count == 1  # ikinci çağrı cache'ten


@respx.mock
async def test_translate_error_fallback() -> None:
    t = Translator()
    t._key = "test-key"
    respx.post(t._url).mock(return_value=httpx.Response(500))
    assert await t.to_turkish("Rice") == "Rice"
