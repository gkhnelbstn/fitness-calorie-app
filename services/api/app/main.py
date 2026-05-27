"""FastAPI uygulama giriş noktası."""

from __future__ import annotations

from fastapi import FastAPI

from . import __version__
from .config import get_settings
from .routers import health, meals, recipes, summary

settings = get_settings()

app = FastAPI(
    title="Türkçe Beslenme & Fitness Koçu API",
    version=__version__,
    description="Free-first modüler monolit backend (Faz 0 iskeleti).",
)

app.include_router(health.router)
app.include_router(meals.router)
app.include_router(recipes.router)
app.include_router(summary.router)


@app.get("/", tags=["root"])
async def root() -> dict:
    return {"app": settings.app_name, "version": __version__, "docs": "/docs"}
