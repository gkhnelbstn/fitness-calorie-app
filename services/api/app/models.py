"""ORM modelleri — ürün omurgası (çekirdek tablolar).

İlke: ham kaynak payload'ı (raw_payload JSON) sakla + ayrıca normalize et.
Lisans takibi için tarif/besin kayıtları source_attribution'a bağlanır.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


# --------------------------------------------------------------------------- #
# Kullanıcı
# --------------------------------------------------------------------------- #
class UserProfile(TimestampMixin, Base):
    __tablename__ = "user_profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    sex: Mapped[str | None] = mapped_column(String(16), nullable=True)
    birth_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    activity_level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    locale: Mapped[str] = mapped_column(String(8), default="tr")


class UserGoal(TimestampMixin, Base):
    __tablename__ = "user_goal"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_profile.id", ondelete="CASCADE"))
    goal_type: Mapped[str] = mapped_column(String(32))  # kilo_ver / koru / kas_yap
    target_kcal: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_protein_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class UserPreference(TimestampMixin, Base):
    __tablename__ = "user_preference"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_profile.id", ondelete="CASCADE"))
    key: Mapped[str] = mapped_column(String(64))
    value: Mapped[dict | list | str | int | float | bool | None] = mapped_column(JSON)

    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_user_pref"),)


# --------------------------------------------------------------------------- #
# Malzeme / besin omurgası
# --------------------------------------------------------------------------- #
class IngredientCanonical(TimestampMixin, Base):
    """Tekilleştirilmiş malzeme. Tüm varyasyonlar buraya işaret eder."""

    __tablename__ = "ingredient_canonical"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(96), unique=True)  # ör. "sumak"
    name_tr: Mapped[str] = mapped_column(String(160))
    name_en: Mapped[str | None] = mapped_column(String(160), nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)


class IngredientAliasTr(Base):
    """Türkçe eş anlamlı/varyant → canonical eşlemesi."""

    __tablename__ = "ingredient_alias_tr"

    id: Mapped[int] = mapped_column(primary_key=True)
    canonical_id: Mapped[int] = mapped_column(
        ForeignKey("ingredient_canonical.id", ondelete="CASCADE")
    )
    alias: Mapped[str] = mapped_column(String(160), index=True)

    __table_args__ = (UniqueConstraint("alias", name="uq_alias"),)


class IngredientBlacklist(TimestampMixin, Base):
    """Kullanıcının istemediği malzemeler (kara liste)."""

    __tablename__ = "ingredient_blacklist"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_profile.id", ondelete="CASCADE"))
    canonical_id: Mapped[int] = mapped_column(
        ForeignKey("ingredient_canonical.id", ondelete="CASCADE")
    )
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (UniqueConstraint("user_id", "canonical_id", name="uq_blacklist"),)


class NutritionProfile(TimestampMixin, Base):
    """Bir malzeme/ürün için 100g başına besin değerleri + kaynak."""

    __tablename__ = "nutrition_profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    canonical_id: Mapped[int | None] = mapped_column(
        ForeignKey("ingredient_canonical.id", ondelete="SET NULL"), nullable=True
    )
    source_id: Mapped[int | None] = mapped_column(
        ForeignKey("source_attribution.id", ondelete="SET NULL"), nullable=True
    )
    basis: Mapped[str] = mapped_column(String(16), default="per_100g")
    kcal: Mapped[float | None] = mapped_column(Float, nullable=True)
    protein_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    carb_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    fat_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    fiber_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class FoodProduct(TimestampMixin, Base):
    """Paketli/barkodlu ürün (örn. Open Food Facts)."""

    __tablename__ = "food_product"

    id: Mapped[int] = mapped_column(primary_key=True)
    barcode: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    brand: Mapped[str | None] = mapped_column(String(160), nullable=True)
    canonical_id: Mapped[int | None] = mapped_column(
        ForeignKey("ingredient_canonical.id", ondelete="SET NULL"), nullable=True
    )
    source_id: Mapped[int | None] = mapped_column(
        ForeignKey("source_attribution.id", ondelete="SET NULL"), nullable=True
    )
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)


# --------------------------------------------------------------------------- #
# Tarif
# --------------------------------------------------------------------------- #
class Recipe(TimestampMixin, Base):
    __tablename__ = "recipe"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True)
    title_tr: Mapped[str] = mapped_column(String(255))
    servings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_kcal: Mapped[float | None] = mapped_column(Float, nullable=True)
    region: Mapped[str | None] = mapped_column(String(96), nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    cook_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(16), nullable=True)  # kolay/orta/zor
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_adaptable: Mapped[bool] = mapped_column(Boolean, default=True)
    needs_refresh: Mapped[bool] = mapped_column(Boolean, default=False)
    license_mode: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source_id: Mapped[int | None] = mapped_column(
        ForeignKey("source_attribution.id", ondelete="SET NULL"), nullable=True
    )
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredient"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id", ondelete="CASCADE"))
    canonical_id: Mapped[int | None] = mapped_column(
        ForeignKey("ingredient_canonical.id", ondelete="SET NULL"), nullable=True
    )
    raw_name: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    optional: Mapped[bool] = mapped_column(Boolean, default=False)  # çıkarılabilir mi?


class RecipeStepTr(Base):
    __tablename__ = "recipe_step_tr"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id", ondelete="CASCADE"))
    step_no: Mapped[int] = mapped_column(Integer)
    text_tr: Mapped[str] = mapped_column(Text)


class RecipeTag(Base):
    __tablename__ = "recipe_tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id", ondelete="CASCADE"))
    tag: Mapped[str] = mapped_column(String(64), index=True)

    __table_args__ = (UniqueConstraint("recipe_id", "tag", name="uq_recipe_tag"),)


# --------------------------------------------------------------------------- #
# Yemek günlüğü
# --------------------------------------------------------------------------- #
class MealLog(TimestampMixin, Base):
    __tablename__ = "meal_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_profile.id", ondelete="CASCADE"))
    eaten_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    meal_type: Mapped[str | None] = mapped_column(String(32), nullable=True)  # kahvalti…
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)  # doğal dil girdi
    total_kcal: Mapped[float | None] = mapped_column(Float, nullable=True)
    photo_path: Mapped[str | None] = mapped_column(String(512), nullable=True)


class MealLogItem(Base):
    __tablename__ = "meal_log_item"

    id: Mapped[int] = mapped_column(primary_key=True)
    meal_log_id: Mapped[int] = mapped_column(ForeignKey("meal_log.id", ondelete="CASCADE"))
    canonical_id: Mapped[int | None] = mapped_column(
        ForeignKey("ingredient_canonical.id", ondelete="SET NULL"), nullable=True
    )
    raw_name: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    kcal: Mapped[float | None] = mapped_column(Float, nullable=True)
    protein_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    carb_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    fat_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)  # eşleşme güveni


# --------------------------------------------------------------------------- #
# Sağlık özeti (cihazdan gelen günlük özet)
# --------------------------------------------------------------------------- #
class DailyHealthSummary(TimestampMixin, Base):
    __tablename__ = "daily_health_summary"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_profile.id", ondelete="CASCADE"))
    day: Mapped[str] = mapped_column(String(10), index=True)  # YYYY-MM-DD
    steps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    active_kcal: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_kcal: Mapped[float | None] = mapped_column(Float, nullable=True)
    exercise_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (UniqueConstraint("user_id", "day", name="uq_health_day"),)


# --------------------------------------------------------------------------- #
# Egzersiz
# --------------------------------------------------------------------------- #
class WorkoutTemplate(TimestampMixin, Base):
    """free-exercise-db / wger'den normalize edilmiş egzersiz/şablon."""

    __tablename__ = "workout_template"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True)
    name_tr: Mapped[str] = mapped_column(String(255))
    primary_muscle: Mapped[str | None] = mapped_column(String(64), nullable=True)
    level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    equipment: Mapped[str | None] = mapped_column(String(96), nullable=True)
    source_id: Mapped[int | None] = mapped_column(
        ForeignKey("source_attribution.id", ondelete="SET NULL"), nullable=True
    )
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class WorkoutLog(TimestampMixin, Base):
    """Kullanıcının yaptığı antrenman kaydı (gün bazlı)."""

    __tablename__ = "workout_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_profile.id", ondelete="CASCADE"))
    day: Mapped[str] = mapped_column(String(10), index=True)  # YYYY-MM-DD
    template_slug: Mapped[str] = mapped_column(String(96))
    name_tr: Mapped[str] = mapped_column(String(160))
    sets: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reps: Mapped[str | None] = mapped_column(String(32), nullable=True)
    minutes: Mapped[int] = mapped_column(Integer, default=30)
    kcal: Mapped[int | None] = mapped_column(Integer, nullable=True)
    done: Mapped[bool] = mapped_column(Boolean, default=True)


class WorkoutRecommendation(TimestampMixin, Base):
    __tablename__ = "workout_recommendation"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_profile.id", ondelete="CASCADE"))
    day: Mapped[str] = mapped_column(String(10), index=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)


# --------------------------------------------------------------------------- #
# Öneri motoru + geri bildirim
# --------------------------------------------------------------------------- #
class Recommendation(TimestampMixin, Base):
    __tablename__ = "recommendation"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_profile.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(32))  # meal / workout
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class RecommendationFeedback(TimestampMixin, Base):
    __tablename__ = "recommendation_feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    recommendation_id: Mapped[int] = mapped_column(
        ForeignKey("recommendation.id", ondelete="CASCADE")
    )
    action: Mapped[str] = mapped_column(String(32))  # accepted / rejected / edited
    note: Mapped[str | None] = mapped_column(Text, nullable=True)


# --------------------------------------------------------------------------- #
# Lisans / kaynak takibi + içe alma işleri
# --------------------------------------------------------------------------- #
class SourceAttribution(TimestampMixin, Base):
    __tablename__ = "source_attribution"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(96))  # TurKomp / OpenFoodFacts / USDA …
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    license: Mapped[str | None] = mapped_column(String(64), nullable=True)  # CC0 / ODbL …
    license_mode: Mapped[str | None] = mapped_column(String(32), nullable=True)


class ImportJob(TimestampMixin, Base):
    __tablename__ = "import_job"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_type: Mapped[str] = mapped_column(String(64))  # seed_exercises / seed_turkomp …
    status: Mapped[str] = mapped_column(String(32), default="pending")
    detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)
