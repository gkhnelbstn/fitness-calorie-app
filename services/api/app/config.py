"""Uygulama ayarları. Tüm gizli anahtarlar .env'den okunur (repoya girmez)."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "fitness-calorie-app"
    environment: str = "dev"
    debug: bool = True

    # Veritabanı — MVP'de SQLite (async), büyüyünce PostgreSQL.
    database_url: str = "sqlite+aiosqlite:///./dev.db"

    # --- Ücretsiz dış kaynaklar ---
    # Open Food Facts: anahtar gerektirmez, ama özel User-Agent ister.
    off_user_agent: str = "fitness-calorie-app/0.1 (kisisel; iletisim: ornek@ornek.com)"
    off_base_url: str = "https://world.openfoodfacts.org"

    # USDA FoodData Central: ücretsiz anahtar; DEMO_KEY ile sınırlı test edilebilir.
    usda_api_key: str = "DEMO_KEY"
    usda_base_url: str = "https://api.nal.usda.gov/fdc/v1"

    # free-exercise-db: public domain JSON (auth yok). Repoya gömülü kopya da olabilir.
    free_exercise_db_url: str = (
        "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json"
    )

    # NVIDIA build.nvidia.com — LLM normalize (opsiyonel). Boşsa kurallı parser'a düşülür.
    nvidia_api_key: str = ""
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_model: str = "meta/llama-3.3-70b-instruct"

    # Tek kullanıcı için basit API token (Faz 0). Public'e geçişte OAuth2/JWT.
    api_token: str = "dev-local-token"

    # --- Supabase Auth (çok kullanıcı, JWT) ---
    # Boşsa JWT doğrulama devre dışı → legacy api_token akışı (dev/test).
    supabase_jwt_secret: str = ""
    supabase_jwt_alg: str = "HS256"  # asimetrik projede RS256/ES256 + JWKS
    supabase_jwt_audience: str = "authenticated"
    supabase_jwks_url: str = ""  # ör. https://<proj>.supabase.co/auth/v1/.well-known/jwks.json

    # --- Supabase Storage (öğün fotoğrafları; Fly diski ephemeral) ---
    # service_key boşsa yerel upload_dir kullanılır (dev/test).
    supabase_project_url: str = ""  # https://<proj>.supabase.co
    supabase_service_key: str = ""  # service_role key — YALNIZ backend secret'ı
    supabase_storage_bucket: str = "meal-photos"

    # CORS: virgülle ayrılmış izinli origin listesi (prod'da Vercel domaini).
    cors_origins: str = ""

    # Yüklenen yemek fotoğrafları için dizin (gitignore'da).
    upload_dir: str = "./data/photos"

    # TheMealDB: ücretsiz, test key "1" (geliştirme). Tarif hacmi (İngilizce).
    themealdb_base_url: str = "https://www.themealdb.com/api/json/v1/1"

    # Spoonacular: free 150 istek/gün. Anahtar gerekir; boşsa import endpoint 400 döner.
    spoonacular_api_key: str = ""
    spoonacular_base_url: str = "https://api.spoonacular.com"

    # wger: açık REST API (auth yok). language=16 → Türkçe besin (OFF kaynaklı, ~2300).
    wger_base_url: str = "https://wger.de"

    @property
    def spoonacular_enabled(self) -> bool:
        return bool(self.spoonacular_api_key.strip())

    @property
    def llm_enabled(self) -> bool:
        return bool(self.nvidia_api_key.strip())

    @property
    def supabase_auth_enabled(self) -> bool:
        return bool(self.supabase_jwt_secret.strip() or self.supabase_jwks_url.strip())

    @property
    def cors_origin_list(self) -> list[str]:
        extra = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        # 5173 = vite dev, 4173 = vite preview (lokal prod-bundle testi)
        return [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:4173",
            "http://127.0.0.1:4173",
            *extra,
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
