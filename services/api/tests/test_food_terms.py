"""TR→EN yemek sözlüğü + sorgu çözümleme."""

from app.data.food_terms import resolve_query


def test_tavuk_full() -> None:
    h = resolve_query("tavuk")
    assert "chicken" in h.names
    assert "Chicken" in h.categories
    assert "chicken_breast" in h.ingredients


def test_token_match_inflected() -> None:
    h = resolve_query("tavuklu sote")  # 'tavuk' substring
    assert "chicken" in h.names


def test_short_key_no_false_substring() -> None:
    # 'et' kısa anahtar tam-kelime → 'spagetti' içinde beef'e eşleşmez
    h = resolve_query("spagetti")
    assert "beef" not in h.names
    assert "spaghetti" in h.names  # 'spagetti' kendi kaydı


def test_kofte_turkish_area() -> None:
    h = resolve_query("köfte")
    assert "kofta" in h.names or "meatball" in h.names
    assert "Turkish" in h.areas


def test_unknown_empty() -> None:
    assert not resolve_query("zzzbilinmeyen").any()
