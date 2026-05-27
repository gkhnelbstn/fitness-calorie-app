"""Kurallı Türkçe yemek ayrıştırıcı."""

from app.services.meal_parser import parse_meal_text


def test_multi_chunk() -> None:
    items = parse_meal_text("öğlen 1 kase kuru fasulye, 1 kase pilav, 1 ayran içtim")
    triples = {(i.name, i.quantity, i.unit) for i in items}
    assert ("kuru fasulye", 1.0, "kase") in triples
    assert ("pilav", 1.0, "kase") in triples
    assert any(i.name == "ayran" and i.quantity == 1.0 and i.unit is None for i in items)


def test_word_number() -> None:
    items = parse_meal_text("iki yumurta")
    assert items[0].name == "yumurta"
    assert items[0].quantity == 2.0


def test_no_quantity() -> None:
    items = parse_meal_text("simit")
    assert len(items) == 1
    assert items[0].name == "simit"
    assert items[0].quantity is None


def test_ve_separator() -> None:
    items = parse_meal_text("1 dilim ekmek ve 1 bardak süt")
    assert len(items) == 2
    assert items[0].unit == "dilim"
    assert items[1].unit == "bardak"


def test_empty_text() -> None:
    assert parse_meal_text("   ") == []
