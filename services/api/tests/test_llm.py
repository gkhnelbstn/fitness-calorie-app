"""NVIDIA LLM istemcisi — respx ile mock, parse + fallback davranışı."""

import httpx
import respx

from app.services.extract import extract_items
from app.services.llm import LlmExtractor, _parse_content, _strip_fences


def test_strip_fences_plain() -> None:
    assert _strip_fences('{"items": []}') == '{"items": []}'


def test_strip_fences_codeblock() -> None:
    fenced = '```json\n{"items": []}\n```'
    assert _strip_fences(fenced) == '{"items": []}'


def test_parse_content() -> None:
    content = (
        '{"items": [{"name": "simit", "quantity": 1, "unit": "adet"},'
        ' {"name": "", "quantity": null, "unit": null}]}'
    )
    items = _parse_content(content)
    assert len(items) == 1  # boş isim atlanır
    assert items[0].name == "simit"
    assert items[0].quantity == 1.0


def test_extract_returns_none_without_key() -> None:
    ext = LlmExtractor()
    ext._key = ""
    # event loop gerektirmesin diye senkron kontrol: boş key → None döner

    import asyncio

    assert asyncio.run(ext.extract("1 ayran")) is None


@respx.mock
async def test_extract_with_mocked_nvidia() -> None:
    ext = LlmExtractor()
    ext._key = "test-key"
    respx.post(ext._url).mock(
        return_value=httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": (
                                '{"items": [{"name": "pilav", "quantity": 1, "unit": "kase"}]}'
                            )
                        }
                    }
                ]
            },
        )
    )
    items = await ext.extract("1 kase pilav")
    assert items is not None
    assert items[0].name == "pilav"
    assert items[0].unit == "kase"


@respx.mock
async def test_extract_http_error_returns_none() -> None:
    ext = LlmExtractor()
    ext._key = "test-key"
    respx.post(ext._url).mock(return_value=httpx.Response(500))
    assert await ext.extract("1 ayran") is None


async def test_extract_items_falls_back_to_rules() -> None:
    # _disable_real_llm autouse fixture key'i boşalttı → kurallı parser çalışır.
    items = await extract_items("1 kase pilav")
    assert items[0].name == "pilav"
    assert items[0].unit == "kase"
