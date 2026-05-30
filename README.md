# fitness-calorie-app

Türkçe beslenme & fitness koçu — doğal dilde yemek girişi, kara liste malzeme filtresi, Türkçe/bölgesel tarif önerisi ve aktivite tabanlı enerji dengesi. **Free-first** mimari (tek kullanıcı).

Tasarım: [`docs/DESIGN.md`](docs/DESIGN.md).

**Ön yüz kararı:** Tek ön yüz = **React `apps/web`** (Claude Design çıktısı). Flutter denemesi emekliye ayrıldı (git geçmişinde). Gerekçe: tek kod tabanı = düşük bakım; tasarım hazır; Claude Code ile düz JSX düzenlemesi hızlı. Mobil gerekirse PWA.

## Monorepo yapısı

```
apps/web/              # React (UMD) + Tailwind + Babel CDN — ürün ön yüzü
services/api/          # FastAPI backend
services/worker/       # arka plan işleri / seed (sonra)
packages/contracts/    # OpenAPI/DTO/canonical modeller
packages/domain/       # iş kuralları (blacklist, ikame)
infra/docker/          # docker-compose
infra/ci/              # CI yardımcıları
db/seeds/              # seed verileri (TurKomp, free-exercise-db…)
docs/                  # DESIGN.md, ADR'ler
```

## Ön yüzü çalıştırma (apps/web)

```powershell
cd apps/web
python -m http.server 5500   # http://localhost:5500
```
⚙️ Ayarlar → "Canlı backend" aç, `baseUrl=http://localhost:8000`, `token=<API_TOKEN>` (varsayılan `dev-local-token`). Tarifler'de "Web'de ara" toggle → TheMealDB'den çok çeşit getirir. Detay: [`apps/web/README.md`](apps/web/README.md).

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

- Ön yüz tek: `apps/web` (React). Mobil gerekirse PWA; Health Connect (ileride) UI'dan bağımsız, backend'e veri basan ayrı native modül olur.
- LLM (NVIDIA) yalnızca doğal dil **normalizasyonu** yapar; kalori/makro her zaman yapılandırılmış kaynaktan gelir. Anahtar yoksa kurallı parser'a düşülür.
- `.env` repoya **girmez**. Tüm dış kaynaklar (Open Food Facts, USDA, free-exercise-db) ücretsizdir.
