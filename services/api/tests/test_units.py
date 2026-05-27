"""Birim → gram dönüşümü."""

from app.services.units import resolve_grams


def test_kase() -> None:
    assert resolve_grams(1, "kase") == 200


def test_su_bardagi_normalized() -> None:
    assert resolve_grams(1, "Su Bardağı") == 200


def test_bare_count_is_adet() -> None:
    assert resolve_grams(2, None) == 100


def test_unknown_unit() -> None:
    assert resolve_grams(1, "kova") is None


def test_no_quantity() -> None:
    assert resolve_grams(None, "kase") is None
