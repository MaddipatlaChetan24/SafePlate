"""Export recipes and meal plans to Markdown files."""

from __future__ import annotations

import re
from pathlib import Path

from .models import MealPlan, Recipe
from .shopping import shopping_list, shopping_list_text


def recipe_markdown(recipe: Recipe) -> str:
    n = recipe.nutrition_per_serving
    lines = [
        f"# {recipe.name}",
        "",
        f"**Cuisine:** {recipe.cuisine} · **Difficulty:** {recipe.difficulty} · "
        f"**Prep:** {recipe.prep_minutes} min · **Cook:** {recipe.cook_minutes} min · **Serves:** {recipe.servings}",
        "",
        "## Ingredients",
        *[f"- {i.label()}" for i in recipe.ingredients],
    ]
    if recipe.missing_ingredients:
        lines += ["", "## You'll need to buy", *[f"- {i.label()}" for i in recipe.missing_ingredients]]
    lines += ["", "## Instructions", *[f"{k}. {s}" for k, s in enumerate(recipe.instructions, 1)]]
    lines += [
        "",
        "## Nutrition (per serving)",
        f"{n.calories} kcal · Protein {n.protein_g:g} g · Carbs {n.carbs_g:g} g · Fat {n.fat_g:g} g",
    ]
    if recipe.substitutions:
        lines += ["", "## Substitutions", *[f"- {s}" for s in recipe.substitutions]]
    if recipe.tips:
        lines += ["", f"> **Chef's tip:** {recipe.tips}"]
    return "\n".join(lines) + "\n"


def plan_markdown(plan: MealPlan, pantry: list[str] | None = None) -> str:
    out = ["# Meal Plan", ""]
    out += [f"- **{d.day}:** {d.recipe.name} ({d.recipe.total_minutes} min)" for d in plan.days]
    items = shopping_list([d.recipe for d in plan.days], pantry)
    out += ["", "## Shopping list", "```", shopping_list_text(items), "```", ""]
    for d in plan.days:
        out += ["---", "", f"_{d.day}_", "", recipe_markdown(d.recipe)]
    return "\n".join(out)


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "recipe"


def write_markdown(content: str, directory: str | Path, name: str) -> Path:
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    target = path / f"{slugify(name)}.md"
    target.write_text(content, encoding="utf-8")
    return target
