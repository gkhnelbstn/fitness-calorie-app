#!/usr/bin/env sh
# Prod başlatma (Render): migrate + idempotent seed + uvicorn.
# Render free'de pre-deploy yok; her boot'ta çalışır (migrate no-op, seed skip-fast).
# $PORT Render tarafından verilir; yoksa 8000 (lokal).
set -e
uv run --no-dev alembic upgrade head
uv run --no-dev python -m app.seeds
exec uv run --no-dev uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
