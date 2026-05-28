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

    # Yüklenen yemek fotoğrafları için dizin (gitignore'da).
    upload_dir: str = "./data/photos"

    # TheMealDB: ücretsiz, test key "1" (geliştirme). Tarif hacmi (İngilizce).
    themealdb_base_url: str = "https://www.themealdb.com/api/json/v1/1"

    # Spoonacular: free 150 istek/gün. Anahtar gerekir; boşsa import endpoint 400 döner.
    spoonacular_api_key: str = ""
    spoonacular_base_url: str = "https://api.spoonacular.com"

    @property
    def spoonacular_enabled(self) -> bool:
        return bool(self.spoonacular_api_key.strip())

    @property
    def llm_enabled(self) -> bool:
        return bool(self.nvidia_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()
