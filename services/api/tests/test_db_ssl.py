from app.db import _engine_kwargs, _postgres_requires_ssl


def test_local_postgres_does_not_force_ssl() -> None:
    url = "postgresql+asyncpg://fit:fit@localhost:5432/fit"

    assert _postgres_requires_ssl(url) is False
    assert _engine_kwargs(url) == {}


def test_supabase_postgres_forces_ssl() -> None:
    url = "postgresql+asyncpg://postgres:pw@db.example.supabase.co:5432/postgres"

    assert _postgres_requires_ssl(url) is True
    assert _engine_kwargs(url) == {"connect_args": {"ssl": "require"}, "pool_pre_ping": True}


def test_explicit_sslmode_overrides_host_default() -> None:
    assert (
        _postgres_requires_ssl("postgresql+asyncpg://fit:fit@localhost:5432/fit?sslmode=require")
        is True
    )
    assert (
        _postgres_requires_ssl(
            "postgresql+asyncpg://u:p@db.example.supabase.co:5432/db?sslmode=disable"
        )
        is False
    )
