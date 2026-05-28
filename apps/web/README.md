# apps/web — Claude Design web ön yüzü

React (UMD) + Tailwind (Play CDN) + Babel-standalone ile **build gerektirmeyen** tek sayfa uygulama. Claude Design (claude.ai/design) çıktısı; backend sözleşmemize (`docs/backend-contract.md`) göre tasarlandı.

## Çalıştırma (lokal)

Babel `src=` ile JSX yüklediği için **HTTP sunucu** gerekir (file:// olmaz):

```powershell
cd apps/web
python -m http.server 5500
```

Tarayıcıda: http://localhost:5500

## Mock vs canlı backend

- **Varsayılan: mock** (localStorage). Backend olmadan tüm ekranlar dolu görünür.
- **Canlı backend'e bağlamak:** uygulamada üst bardaki ⚙️ **Ayarlar** → "Canlı backend" aç, `baseUrl=http://localhost:8000`, `token=<API_TOKEN>` (services/api/.env). Backend açık + CORS zaten localhost'a açık.

Backend'i ayağa kaldır:
```powershell
cd services/api
uv run uvicorn app.main:app --reload --port 8000
```

## Yapı
- `index.html` — fontlar, Tailwind config, CSS değişkenleri (açık/koyu tema), script yükleme sırası.
- `src/` — `app.jsx` (kabuk/nav/routing), `mock.jsx` (mock + canlı fetch dağıtıcısı), `ui.jsx`, `icons.jsx`, `screens-*.jsx`, `modals.jsx`, `auth.jsx`, `ai.jsx`, `muscle-map.jsx`.
- `tweaks-panel.jsx` — tasarım ayar paneli (accent/yüzey tonu/makro stili).
- `docs/backend-contract.md` — frontend'in uyduğu API sözleşmesi.

## Not
Bu ön yüz `apps/client_flutter` (Flutter) ile birlikte yaşar. Hangisinin ana ön yüz olacağı ileride netleşecek. Build adımı yok; üretimde Tailwind/Babel CDN yerine derlenmiş sürüm önerilir.
