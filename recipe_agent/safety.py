"""Rule-based checks that verify LLM output against the user's hard constraints.

LLMs occasionally slip an allergen or a non-vegan ingredient into a recipe.
These checks run after every generation; violations are fed back to the model
so it can correct itself (see agent.RecipeAgent).
"""

from __future__ import annotations

import re

from .models import Preferences, Recipe

ALLERGEN_KEYWORDS: dict[str, list[str]] = {
    "nuts": ["almond", "cashew", "walnut", "pecan", "pistachio", "hazelnut", "macadamia", "peanut", "nut"],
    "peanut": ["peanut"],
    "dairy": ["milk", "cheese", "butter", "cream", "yogurt", "yoghurt", "ghee", "parmesan", "mozzarella", "paneer"],
    "gluten": ["wheat", "flour", "pasta", "bread", "noodle", "barley", "rye", "couscous", "breadcrumb", "soy sauce"],
    "egg": ["egg", "mayonnaise", "mayo"],
    "shellfish": ["shrimp", "prawn", "crab", "lobster", "scallop", "mussel", "clam", "oyster"],
    "fish": ["fish", "salmon", "tuna", "cod", "anchovy", "sardine", "fish sauce"],
    "soy": ["soy", "tofu", "tempeh", "edamame", "miso"],
    "sesame": ["sesame", "tahini"],
}

MEAT = ["chicken", "beef", "pork", "lamb", "bacon", "ham", "turkey", "sausage", "mutton", "duck", "veal", "prosciutto"]
SEAFOOD = ALLERGEN_KEYWORDS["fish"] + ALLERGEN_KEYWORDS["shellfish"]
ANIMAL_PRODUCTS = ALLERGEN_KEYWORDS["dairy"] + ALLERGEN_KEYWORDS["egg"] + ["honey", "gelatin"]

# Phrases that contain a forbidden word but mean something else. Each is
# rewritten to its "real" ingredient before keyword matching, so e.g. almond
# milk still counts as a nut but not as dairy.
REWRITES: dict[str, str] = {
    "coconut milk": "coconut", "coconut cream": "coconut", "almond milk": "almond",
    "oat milk": "oat", "soy milk": "soy", "rice milk": "rice", "peanut butter": "peanut",
    "almond butter": "almond", "cashew cream": "cashew", "vegan butter": "margarine",
    "vegan cheese": "plant cheese", "nutritional yeast": "yeast", "cream of tartar": "tartar",
    "eggplant": "aubergine", "nutmeg": "spice",
}

DIET_RULES: dict[str, list[str]] = {
    "vegetarian": MEAT + SEAFOOD,
    "pescatarian": MEAT,
    "vegan": MEAT + SEAFOOD + ANIMAL_PRODUCTS,
    "dairy-free": ALLERGEN_KEYWORDS["dairy"],
    "gluten-free": ALLERGEN_KEYWORDS["gluten"],
}


def _contains(name: str, keywords: list[str]) -> str | None:
    text = name.lower()
    for phrase, real in REWRITES.items():
        text = text.replace(phrase, real)
    for kw in keywords:
        # Match at a word start so "ham" doesn't hit "champignon" and
        # "nut" doesn't hit "coconut"; plurals ("eggs") still match.
        if re.search(rf"\b{re.escape(kw)}", text):
            return kw
    return None


def check_recipe(recipe: Recipe, prefs: Preferences) -> list[str]:
    """Return a list of human-readable violations (empty if the recipe is OK)."""
    problems: list[str] = []
    names = [i.name for i in recipe.ingredients + recipe.missing_ingredients]

    for allergy in prefs.allergies:
        keywords = ALLERGEN_KEYWORDS.get(allergy.lower().strip(), [allergy.lower().strip()])
        for n in names:
            hit = _contains(n, keywords)
            if hit:
                problems.append(f"'{recipe.name}' contains '{n}', which conflicts with allergy '{allergy}'")

    diet = prefs.diet.lower().strip()
    if diet in DIET_RULES:
        for n in names:
            hit = _contains(n, DIET_RULES[diet])
            if hit:
                problems.append(f"'{recipe.name}' contains '{n}', which is not {diet}")

    if prefs.max_minutes and recipe.total_minutes > prefs.max_minutes:
        problems.append(
            f"'{recipe.name}' takes {recipe.total_minutes} min, over the {prefs.max_minutes} min limit"
        )
    return problems
