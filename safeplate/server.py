"""FastAPI backend for the web app.  Run with:  safeplate serve"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .agent import AgentResult, RecipeAgent
from .export import plan_markdown, recipe_markdown
from .models import MealPlan, Preferences, Recipe
from .shopping import ingredient_matches, shopping_list
from .storage import Store

load_dotenv()
WEB_DIR = Path(__file__).parent / "web"
app = FastAPI(title="SafePlate", version="1.0.0")
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


def get_store():
    store = Store()
    try:
        yield store
    finally:
        store.close()


def get_agent() -> RecipeAgent:
    return RecipeAgent()


# --- Request models --------------------------------------------------------

class SuggestRequest(BaseModel):
    ingredients: list[str] = Field(default_factory=list)
    use_pantry: bool = False
    preferences: Preferences = Field(default_factory=Preferences)
    count: int = Field(default=3, ge=1, le=6)


class PlanRequest(SuggestRequest):
    days: int = Field(default=5, ge=1, le=7)


class ItemsRequest(BaseModel):
    items: list[str]


class ScaleRequest(BaseModel):
    recipe: Recipe
    servings: int = Field(ge=1, le=50)


class RateRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    notes: str | None = None


# --- Helpers ---------------------------------------------------------------

def _ingredients(req: SuggestRequest, store: Store) -> list[str]:
    items = [i.strip().lower() for i in req.ingredients if i.strip()]
    if req.use_pantry:
        items += [p for p in store.pantry_list() if p not in items]
    return items


def _decorate(recipe: Recipe, have: list[str]) -> dict:
    """Recipe JSON plus how many of the user's ingredients it uses."""
    used = [i.name for i in recipe.ingredients if any(ingredient_matches(h, i.name) for h in have)]
    return {**recipe.model_dump(), "total_minutes": recipe.total_minutes, "uses": used}


def _run_payload(result: AgentResult, ingredients: list[str], store: Store) -> dict:
    return {
        "recipes": [_decorate(r, ingredients) for r in result.recipes],
        "recommended": result.recommended,
        "trace": {"attempts": result.attempts, "corrections": result.corrections, "unresolved": result.unresolved},
        "shopping_list": [i.model_dump() | {"label": i.label()} for i in shopping_list(result.recipes, store.pantry_list())],
        "ingredients": ingredients,
    }


# --- Routes ----------------------------------------------------------------

@app.get("/", include_in_schema=False)
def index():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/status")
def status(agent: RecipeAgent = Depends(get_agent)):
    return {"demo": agent.demo, "model": None if agent.demo else agent.model}


@app.post("/api/suggest")
def suggest(req: SuggestRequest, store: Store = Depends(get_store), agent: RecipeAgent = Depends(get_agent)):
    ingredients = _ingredients(req, store)
    liked = store.favourite_cuisines()
    extra = ""
    if liked and not req.preferences.cuisine:
        extra = f"The user has rated these cuisines highly: {', '.join(liked)}. Lean towards them for at least one recipe."
    result = agent.suggest(ingredients, req.preferences, count=req.count, extra=extra)
    store.log_search(ingredients, req.preferences, result.recipes)
    return _run_payload(result, ingredients, store)


@app.post("/api/plan")
def plan(req: PlanRequest, store: Store = Depends(get_store), agent: RecipeAgent = Depends(get_agent)):
    ingredients = _ingredients(req, store)
    meal_plan, result = agent.plan_week(ingredients, req.preferences, req.days)
    payload = _run_payload(result, ingredients, store)
    payload["days"] = [{"day": d.day, "recipe": _decorate(d.recipe, ingredients)} for d in meal_plan.days]
    payload["markdown"] = plan_markdown(meal_plan, store.pantry_list())
    return payload


@app.post("/api/scale")
def scale(req: ScaleRequest, store: Store = Depends(get_store)):
    return _decorate(req.recipe.scaled(req.servings), store.pantry_list())


@app.post("/api/export/markdown", response_class=PlainTextResponse)
def export_markdown(recipe: Recipe):
    return recipe_markdown(recipe)


@app.post("/api/shopping-list")
def build_shopping_list(recipes: list[Recipe], store: Store = Depends(get_store)):
    return [i.model_dump() | {"label": i.label()} for i in shopping_list(recipes, store.pantry_list())]


# Pantry

@app.get("/api/pantry")
def pantry_list(store: Store = Depends(get_store)):
    return store.pantry_list()


@app.post("/api/pantry")
def pantry_add(req: ItemsRequest, store: Store = Depends(get_store)):
    store.pantry_add(req.items)
    return store.pantry_list()


@app.delete("/api/pantry/{name}")
def pantry_remove(name: str, store: Store = Depends(get_store)):
    store.pantry_remove([name])
    return store.pantry_list()


# Cookbook

@app.get("/api/cookbook")
def cookbook(search: str = "", store: Store = Depends(get_store)):
    pantry = store.pantry_list()
    rows = store.list_recipes(search)
    rated = [r["rating"] for r in rows if r["rating"]]
    cuisines = Counter(r["recipe"].cuisine for r in rows)
    return {
        "recipes": [
            {"id": r["id"], "rating": r["rating"], "notes": r["notes"], "saved_at": r["saved_at"],
             "recipe": _decorate(r["recipe"], pantry)}
            for r in rows
        ],
        "stats": {
            "count": len(rows),
            "avg_rating": round(sum(rated) / len(rated), 1) if rated else None,
            "top_cuisine": cuisines.most_common(1)[0][0] if cuisines else None,
            "avg_minutes": round(sum(r["recipe"].total_minutes for r in rows) / len(rows)) if rows else None,
        },
    }


@app.post("/api/cookbook")
def cookbook_save(recipe: Recipe, store: Store = Depends(get_store)):
    return {"id": store.save_recipe(recipe)}


@app.patch("/api/cookbook/{recipe_id}")
def cookbook_rate(recipe_id: int, req: RateRequest, store: Store = Depends(get_store)):
    if not store.rate_recipe(recipe_id, req.rating, req.notes):
        raise HTTPException(404, "Recipe not found")
    return {"ok": True}


@app.delete("/api/cookbook/{recipe_id}")
def cookbook_delete(recipe_id: int, store: Store = Depends(get_store)):
    if not store.delete_recipe(recipe_id):
        raise HTTPException(404, "Recipe not found")
    return {"ok": True}


@app.get("/api/history")
def history(store: Store = Depends(get_store)):
    return store.history(30)
