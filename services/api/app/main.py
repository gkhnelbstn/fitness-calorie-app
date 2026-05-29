"""FastAPI uygulama giriş noktası."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .config import get_settings
from .routers import (
    admin,
    blacklist,
    health,
    meal_plans,
    meals,
    profile,
    recipes,
    recommendations,
    summary,
    workouts,
)

settings = get_settings()

app = FastAPI(
    title="Türkçe Beslenme & Fitness Koçu API",
    version=__version__,
    description="Free-first modüler monolit backend.",
)

# CORS — Flutter web (lokal dev). flutter run -d chrome rastgele port açar.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(meals.router)
app.include_router(recipes.router)
app.include_router(summary.router)
app.include_router(blacklist.router)
app.include_router(profile.router)
app.include_router(recommendations.router)
app.include_router(meal_plans.router)
app.include_router(admin.router)
app.include_router(workouts.router)


@app.get("/", tags=["root"])
async def root() -> dict:
    return {"app": settings.app_name, "version": __version__, "docs": "/docs"}
