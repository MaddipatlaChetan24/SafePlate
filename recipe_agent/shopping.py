"""Build a consolidated shopping list from one or more recipes."""

from __future__ import annotations

from collections import OrderedDict

from .models import Ingredient, Recipe

# Things nearly every kitchen has; never put them on the list.
STAPLES = {"salt", "pepper", "black pepper", "water", "oil", "cooking oil", "vegetable oil"}


def _norm(name: str) -> str:
    n = name.lower().strip()
    if n.endswith("oes"):  # tomatoes, potatoes
        return n[:-2]
    if n.endswith("s") and not n.endswith("ss") and len(n) > 3:
        return n[:-1]
    return n


def shopping_list(recipes: list[Recipe], pantry: list[str] | None = None) -> list[Ingredient]:
    """Merge every recipe's missing ingredients, minus pantry items and staples.

    Quantities with the same unit are summed; different units for the same
    item are kept as separate lines rather than guessed at.
    """
    have = {_norm(p) for p in (pantry or [])} | STAPLES
    merged: "OrderedDict[tuple[str, str], Ingredient]" = OrderedDict()
    for recipe in recipes:
        for item in recipe.missing_ingredients:
            key = (_norm(item.name), item.unit.lower())
            if key[0] in have:
                continue
            if key in merged:
                prev = merged[key]
                if prev.quantity is not None and item.quantity is not None:
                    prev.quantity = round(prev.quantity + item.quantity, 2)
            else:
                merged[key] = item.model_copy()
    return list(merged.values())


def shopping_list_text(items: list[Ingredient]) -> str:
    if not items:
        return "Nothing to buy - you have everything!"
    return "\n".join(f"[ ] {i.label()}" for i in items)
