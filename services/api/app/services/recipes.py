"""Tarif arama + blacklist hard filter + ikame/adaptasyon + 'şununla ne pişer'.

Karar deterministik (kural motoru). blocked = excluded ∪ blacklist (canonical id'ler).
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import (
    IngredientCanonical,
    Recipe,
    RecipeIngredient,
    RecipeStepTr,
    RecipeTag,
)
from ..schemas.recipe import IngredientLine, MacrosPerServing, RecipeRead
from .substitution import substitute_for
from .text import slugify_tr


async def _canon_by_slug(session: AsyncSession, slug: str) -> IngredientCanonical | None:
    return (
        await session.execute(select(IngredientCanonical).where(IngredientCanonical.slug == slug))
    ).scalar_one_or_none()


async def adapt_recipe(
    session: AsyncSession, recipe: Recipe, blocked: set[int]
) -> RecipeRead | None:
    """Tarifi blacklist'e göre uyarla. Uyarlanamıyorsa None (elenir)."""
    ri_rows = (
        (
            await session.execute(
                select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe.id)
            )
        )
        .scalars()
        .all()
    )

    ids = [r.canonical_id for r in ri_rows if r.canonical_id is not None]
    canon_map: dict[int, IngredientCanonical] = {}
    if ids:
        canon_map = {
            c.id: c
            for c in (
                await session.execute(
                    select(IngredientCanonical).where(IngredientCanonical.id.in_(ids))
                )
            )
            .scalars()
            .all()
        }

    lines: list[IngredientLine] = []
    notes: list[str] = []
    for r in ri_rows:
        line = IngredientLine(
            raw_name=r.raw_name,
            quantity=r.quantity,
            unit=r.unit,
            canonical_id=r.canonical_id,
            optional=r.optional,
        )
        if r.canonical_id is not None and r.canonical_id in blocked:
            if r.optional:
                line.status = "removed"
                notes.append(f"{r.raw_name} çıkarıldı")
            else:
                canon = canon_map.get(r.canonical_id)
                sub_slug = substitute_for(canon.slug) if canon else None
                sub = await _canon_by_slug(session, sub_slug) if sub_slug else None
                if sub is not None and sub.id not in blocked:
                    line.status = "substituted"
                    line.substitute = sub.name_tr
                    notes.append(f"{r.raw_name} yerine {sub.name_tr}")
                else:
                    return None  # zorunlu malzeme çıkarılamaz/ikame edilemez → ele
        lines.append(line)

    steps = [
        s.text_tr
        for s in (
            await session.execute(
                select(RecipeStepTr)
                .where(RecipeStepTr.recipe_id == recipe.id)
                .order_by(RecipeStepTr.step_no)
            )
        )
        .scalars()
        .all()
    ]
    tags = [
        t.tag
        for t in (await session.execute(select(RecipeTag).where(RecipeTag.recipe_id == recipe.id)))
        .scalars()
        .all()
    ]
    mps = None
    if recipe.total_kcal is not None and recipe.servings:
        mps = MacrosPerServing(kcal=round(recipe.total_kcal / recipe.servings))
    return RecipeRead(
        id=recipe.id,
        slug=recipe.slug,
        title_tr=recipe.title_tr,
        servings=recipe.servings,
        region=recipe.region,
        category=recipe.category,
        cook_minutes=recipe.cook_minutes,
        difficulty=recipe.difficulty,
        image_url=recipe.image_url,
        total_kcal=recipe.total_kcal,
        macros_per_serving=mps,
        adaptable=True,
        ingredients=lines,
        steps=steps,
        tags=tags,
        notes=notes,
    )


def _tokens(text: str) -> set[str]:
    """Ascii kelime token'ları (slugify_tr ile). 'Tavuklu Pide' → {'tavuklu','pide'}."""
    return {t for t in slugify_tr(text).split("-") if t}


def _query_matches(query: str, title: str, ingredient_names: list[str]) -> bool:
    """Sorgu, başlık VEYA malzemelerde kelime-başı olarak geçiyor mu?

    Kelime-başı eşleşme (substring değil): 'et' → 'etli' eşleşir ama 'spagetti'
    eşleşmez; 'tavuk' → 'tavuklu' eşleşir. Çok kelimeli sorguda tüm token'lar geçmeli.
    """
    q_tokens = _tokens(query)
    if not q_tokens:
        return True
    words: set[str] = set()
    words |= _tokens(title)
    for name in ingredient_names:
        words |= _tokens(name)
    return all(any(w.startswith(tok) for w in words) for tok in q_tokens)


async def search_recipes(
    session: AsyncSession,
    q: str | None,
    blocked: set[int],
    *,
    category: str | None = None,
    limit: int | None = None,
    offset: int = 0,
) -> list[RecipeRead]:
    """Tarif araması (kelime-başı, başlık + malzeme) + blacklist adaptasyonu + pagination.

    Sorgu başlıkta VEYA malzeme adında kelime-başı olarak geçen tarifler döner;
    böylece 'tavuk' yalnızca tavuk içeren tarifleri getirir (substring yanlış-pozitifi yok).
    """
    stmt = select(Recipe)
    if category:
        stmt = stmt.where(func.lower(Recipe.category) == category.strip().lower())
    recipes = (await session.execute(stmt.order_by(Recipe.title_tr))).scalars().all()

    if q and q.strip():
        # Eşleşme için malzeme adlarını toplu yükle (recipe başına ayrı sorgu yerine).
        ids = [r.id for r in recipes]
        ing_by_recipe: dict[int, list[str]] = {i: [] for i in ids}
        if ids:
            rows = (
                await session.execute(
                    select(RecipeIngredient.recipe_id, RecipeIngredient.raw_name).where(
                        RecipeIngredient.recipe_id.in_(ids)
                    )
                )
            ).all()
            for rid, raw in rows:
                ing_by_recipe.setdefault(rid, []).append(raw)
        recipes = [r for r in recipes if _query_matches(q, r.title_tr, ing_by_recipe.get(r.id, []))]

    out: list[RecipeRead] = []
    for rc in recipes:
        adapted = await adapt_recipe(session, rc, blocked)
        if adapted is not None:
            out.append(adapted)
    if limit is not None:
        return out[offset : offset + limit]
    return out[offset:] if offset else out


async def cook_with(session: AsyncSession, have: set[int], blocked: set[int]) -> list[RecipeRead]:
    """Elindeki (canonical) malzemelerle pişirilebilen tarifler.

    Zorunlu malzemelerin tümü 'have' içinde olmalı; opsiyoneller gözardı edilir.
    """
    recipes = (await session.execute(select(Recipe))).scalars().all()
    out: list[RecipeRead] = []
    for rc in recipes:
        ri = (
            (
                await session.execute(
                    select(RecipeIngredient).where(RecipeIngredient.recipe_id == rc.id)
                )
            )
            .scalars()
            .all()
        )
        req_ids = {r.canonical_id for r in ri if not r.optional and r.canonical_id is not None}
        if not req_ids or req_ids & blocked:
            continue
        if req_ids <= have:
            adapted = await adapt_recipe(session, rc, blocked)
            if adapted is not None:
                out.append(adapted)
    return out
