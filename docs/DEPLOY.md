# Yayına Alma Rehberi (Free Tier)

Mimari: **Vercel** (web, Vite statik) + **Fly.io** (FastAPI) + **Supabase** (Postgres + Auth + Storage) + **GA4**.

```
[Tarayıcı] ── HTTPS ──> Vercel (apps/web dist)
     │  Authorization: Bearer <Supabase JWT>
     └────────────────> Fly.io (FastAPI) ──> Supabase Postgres
                              └─ foto ────> Supabase Storage (meal-photos)
```

Tüm kod hazır ve main'de. Aşağıdaki adımlar **bir kez** elle yapılır; sonrası CD ile otomatik.

---

## 1. Supabase (önce bu — diğerleri değerlerini kullanır)

1. <https://supabase.com> → New project (region: `eu-central-1` Frankfurt önerilir).
2. **Settings → API**'den not al:
   - `Project URL` → `SUPABASE_PROJECT_URL` / `VITE_SUPABASE_URL`
   - `anon public` key → `VITE_SUPABASE_ANON_KEY` (public, frontend'e girer)
   - `service_role` key → `SUPABASE_SERVICE_KEY` (**yalnız Fly secret** — asla frontend/repo)
   - `JWT Secret` → `SUPABASE_JWT_SECRET` (**yalnız Fly secret**)
3. **Settings → Database → Connection string (URI)** → `DATABASE_URL`
   - Sürücü öneki değiştir: `postgresql://...` → `postgresql+asyncpg://...`
   - Fly için **connection pooler (Transaction)** yerine doğrudan bağlantı (5432) kullan; tek makine için yeterli.
4. **Authentication → Providers**: Email açık (default). **Google**'ı aç:
   - Google Cloud Console → OAuth consent + Web client → Authorized redirect URI:
     `https://<proj>.supabase.co/auth/v1/callback`
   - Client ID/Secret'ı Supabase Google provider'a yapıştır.
   - (Opsiyonel) **Anonymous sign-ins** aç → "Misafir olarak dene" çalışır.
5. **Authentication → URL Configuration**:
   - Site URL: `https://<vercel-domain>`
   - Redirect URLs: `http://localhost:5173`, `https://*.vercel.app`, prod domain.
6. **Storage**: `meal-photos` adında **public** bucket oluştur.

## 2. Fly.io (backend)

```sh
# flyctl kur: https://fly.io/docs/flyctl/install/
fly auth login
cd services/api
fly launch --no-deploy --copy-config --name <uygulama-adi>   # fly.toml hazır; adı güncelle
fly secrets set \
  DATABASE_URL='postgresql+asyncpg://postgres:<sifre>@db.<proj>.supabase.co:5432/postgres' \
  SUPABASE_JWT_SECRET='<jwt-secret>' \
  SUPABASE_PROJECT_URL='https://<proj>.supabase.co' \
  SUPABASE_SERVICE_KEY='<service-role-key>' \
  CORS_ORIGINS='https://<vercel-domain>' \
  API_TOKEN='<uzun-rastgele-admin-token>'
fly deploy --remote-only
# release_command migrate + seed'i otomatik koşar.
fly logs   # doğrula
```

**CD:** GitHub repo → Settings → Secrets → `FLY_API_TOKEN` = `fly tokens create deploy -x 999999h` çıktısı.
Sonraki her main merge otomatik deploy eder (cicd.yml "Deploy (Fly.io)" job).

## 3. Vercel (web)

1. <https://vercel.com> → Add New Project → GitHub repo'yu import et.
2. **Root Directory: `apps/web`** (kritik — monorepo). Framework: Vite (otomatik algılar; `vercel.json` da var).
3. Environment Variables (Production + Preview):
   - `VITE_API_BASE_URL` = `https://<fly-app>.fly.dev`
   - `VITE_SUPABASE_URL` = `https://<proj>.supabase.co`
   - `VITE_SUPABASE_ANON_KEY` = anon key
   - `VITE_GA_MEASUREMENT_ID` = `G-XXXXXXXXXX` (adım 4)
4. Deploy → çıkan domaini Supabase Redirect URLs (adım 1.5) + Fly `CORS_ORIGINS`'a ekle:
   `fly secrets set CORS_ORIGINS='https://<domain>.vercel.app'`

## 4. Google Analytics 4

1. <https://analytics.google.com> → hesap + GA4 property → Web data stream (Vercel domaini).
2. Measurement ID'yi (`G-…`) Vercel `VITE_GA_MEASUREMENT_ID`'ye koy → redeploy.
3. Consent banner ilk ziyarette çıkar; kabul sonrası DebugView'da `page_view` + `meal_added` vb. görünür.

## 5. Prod smoke testi

- [ ] `https://<fly-app>.fly.dev/docs` açılır (FastAPI).
- [ ] Vercel domaininde login (email kaydol veya Google) çalışır; sayfa yenilenince oturum kalır.
- [ ] Öğün ekle → Supabase Table Editor'da `meal_log` satırı **kendi** `user_id`'nle.
- [ ] Tarif "Öğün olarak ekle" → Günlük'te görünür.
- [ ] Foto yükle → Storage `meal-photos` bucket'ında dosya + uygulamada thumbnail.
- [ ] İkinci kullanıcıyla kaydol → ilk kullanıcının verisi görünmez (izolasyon).
- [ ] GA4 Realtime'da ziyaret.

## Bilinen serbest-katman kısıtları

- **Supabase free** ~1 hafta hareketsizlikte duraklar → Dashboard'dan "Restore". Önlem: uptime ping (ör. cron-job.org → `/docs`).
- **Fly auto-stop**: ilk istek ~1-2 sn soğuk başlatma.
- **Storage 1 GB** / **DB 500 MB** free sınırı — kişisel kullanım için bol.
