"""İkame kural tablosu (saf birim)."""

from app.services.substitution import substitute_for


def test_known_substitute() -> None:
    assert substitute_for("tereyagi") == "zeytinyagi"


def test_unknown_substitute() -> None:
    assert substitute_for("ejderha") is None
