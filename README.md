# fitness-calorie-app

Türkçe beslenme & fitness koçu — doğal dilde yemek girişi, kara liste malzeme filtresi, Türkçe/bölgesel tarif önerisi ve aktivite tabanlı enerji dengesi. **Free-first** mimari (tek kullanıcı).

Tasarım: [`docs/DESIGN.md`](docs/DESIGN.md). Mevcut durum: **Faz 0 — backend iskeleti**.

## Monorepo yapısı

```
apps/client_flutter/   # Flutter web+mobil (Faz 4)
services/api/          # FastAPI backend (aktif)
services/worker/       # arka plan işleri / seed (sonra)
packages/contracts/    # OpenAPI/DTO/canonical modeller
packages/domain/       # iş kuralları (blacklist, ikame)
infra/docker/          # docker-compose
infra/ci/              # CI yardımcıları
db/seeds/              # seed verileri (TurKomp, free-exercise-db…)
docs/                  # DESIGN.md, ADR'ler
```

Bağımlılık yönetimi: [**uv**](https://docs.astral.sh/uv/). Kurulu değilse:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Backend'i çalıştırma (Windows / PowerShell)

```powershell
cd services/api
Copy-Item .env.example .env        # gerekirse anahtarları doldur
uv sync                            # .venv kur + bağımlılıklar (uv.lock)
uv run alembic upgrade head        # SQLite şemasını kur
uv run uvicorn app.main:app --reload   # http://127.0.0.1:8000/docs
```

Hızlı kontrol:
```powershell
curl http://127.0.0.1:8000/health
```

## Kalite & güvenlik (CI ile aynı)

```powershell
cd services/api
uv run ruff check .              # lint
uv run ruff format --check .     # format
uv run mypy                      # tip kontrolü
uv run pytest -q --cov-fail-under=90   # unit+smoke+coverage (≥%90)
uv run bandit -c pyproject.toml -r app # SAST
uv run pip-audit                 # bağımlılık zafiyeti
```

CI/CD: [`.github/workflows/cicd.yml`](.github/workflows/cicd.yml) — lint+type, test+coverage, security (bandit/pip-audit/gitleaks), Docker build. Push/PR `main`'de çalışır.

## Notlar

- Health Connect cihaz-üstü Android API'sidir; backend onu çağırmaz (bkz. DESIGN §2.1). Mobil + sağlık verisi Faz 4.
- LLM (NVIDIA) yalnızca doğal dil **normalizasyonu** yapar; kalori/makro her zaman yapılandırılmış kaynaktan gelir. Anahtar yoksa kurallı parser'a düşülür.
- `.env` repoya **girmez**. Tüm dış kaynaklar (Open Food Facts, USDA, free-exercise-db) ücretsizdir.
