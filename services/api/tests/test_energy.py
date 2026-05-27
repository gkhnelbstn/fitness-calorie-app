"""Enerji hesabı (BMR/TDEE/hedef) — saf birim."""

from app.services.energy import bmr_mifflin, compute_energy


def test_bmr_male() -> None:
    # 10*80 + 6.25*178 - 5*30 + 5
    assert bmr_mifflin("erkek", 80, 178, 30) == 1767.5


def test_bmr_female_offset() -> None:
    male = bmr_mifflin("erkek", 70, 170, 30)
    female = bmr_mifflin("kadın", 70, 170, 30)
    assert male - female == 166  # +5 - (-161)


def test_compute_none_when_incomplete() -> None:
    assert (
        compute_energy(
            sex=None,
            weight_kg=80,
            height_cm=178,
            birth_year=1996,
            activity_level="moderate",
            goal_type="koru",
        )
        is None
    )


def test_compute_full_kilo_ver() -> None:
    res = compute_energy(
        sex="erkek",
        weight_kg=80,
        height_cm=178,
        birth_year=1996,
        activity_level="moderate",
        goal_type="kilo_ver",
    )
    assert res is not None
    assert res.bmr == 1767.5
    assert res.target_kcal == 2240  # round(1767.5*1.55) - 500
    assert res.target_low == 2140
    assert res.target_high == 2340


def test_compute_default_activity() -> None:
    res = compute_energy(
        sex="erkek",
        weight_kg=80,
        height_cm=178,
        birth_year=1996,
        activity_level=None,
        goal_type="koru",
    )
    assert res is not None  # None activity → moderate
