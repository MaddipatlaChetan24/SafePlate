"""The recipe agent: generate -> verify -> self-correct.

Unlike a single prompt-and-parse call, the agent validates every recipe
against the user's hard constraints (allergies, diet, time limit) with
deterministic rules and, when something is wrong, sends the violations back
to the model and asks it to fix them. Output is typed via Pydantic structured
output, so there is no fragile JSON regex parsing.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from .models import DayPlan, Ingredient, MealPlan, Nutrition, Preferences, Recipe, RecipeSet
from .safety import check_recipe

SYSTEM_PROMPT = """You are a professional chef and registered nutritionist.
Suggest recipes that make the most of the ingredients the user already has.
Rules:
- Prefer recipes that use many of the available ingredients and need few extras.
- List every ingredient used in `ingredients` with realistic quantities for the requested servings.
- Put anything the user did NOT list (other than water, salt, pepper and cooking oil) in `missing_ingredients`.
- Allergies and dietary restrictions are hard constraints. Never include a forbidden ingredient, even as a garnish.
- Respect the time limit for prep + cook combined.
- Give honest per-serving nutrition estimates.
- Offer 1-3 practical substitutions per recipe.
"""

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@dataclass
class AgentResult:
    recipes: list[Recipe]
    recommended: str
    attempts: int = 1
    corrections: list[str] = field(default_factory=list)  # violations fixed along the way
    unresolved: list[str] = field(default_factory=list)  # violations remaining after max retries


class RecipeAgent:
    def __init__(self, model: str | None = None, temperature: float = 0.6, max_retries: int = 2, demo: bool = False):
        self.model = model or os.getenv("SAFEPLATE_MODEL", "gpt-4o-mini")
        self.temperature = temperature
        self.max_retries = max_retries
        self.demo = demo or not os.getenv("OPENAI_API_KEY")
        self._llm = None

    # --- LLM plumbing -----------------------------------------------------

    def _structured_llm(self):
        if self._llm is None:
            from langchain_openai import ChatOpenAI

            self._llm = ChatOpenAI(model=self.model, temperature=self.temperature).with_structured_output(RecipeSet)
        return self._llm

    def _call(self, messages: list[tuple[str, str]], ingredients: list[str], prefs: Preferences, count: int) -> RecipeSet:
        if self.demo:
            return demo_recipes(ingredients, prefs, count)
        return self._structured_llm().invoke(messages)

    # --- Public API -------------------------------------------------------

    def suggest(self, ingredients: list[str], prefs: Preferences, count: int = 3, extra: str = "") -> AgentResult:
        user_msg = (
            f"Available ingredients: {', '.join(ingredients) or 'none - suggest pantry-staple recipes'}\n\n"
            f"Constraints:\n{prefs.describe()}\n\n"
            f"Suggest exactly {count} distinct recipes."
        )
        if extra:
            user_msg += f"\n\n{extra}"
        messages: list[tuple[str, str]] = [("system", SYSTEM_PROMPT), ("human", user_msg)]

        corrections: list[str] = []
        for attempt in range(1, self.max_retries + 2):
            result = self._call(messages, ingredients, prefs, count)
            problems = [p for r in result.recipes for p in check_recipe(r, prefs)]
            if not problems:
                return AgentResult(result.recipes, result.recommended, attempt, corrections)
            corrections.extend(problems)
            if attempt > self.max_retries:
                break
            messages += [
                ("ai", result.model_dump_json()),
                (
                    "human",
                    "Some recipes break my constraints:\n- "
                    + "\n- ".join(problems)
                    + "\nReplace or fix ONLY those recipes and return the full set again.",
                ),
            ]

        # Out of retries: drop the offending recipes rather than show unsafe ones.
        safe = [r for r in result.recipes if not check_recipe(r, prefs)]
        recommended = result.recommended if any(r.name == result.recommended for r in safe) else (safe[0].name if safe else "")
        return AgentResult(safe, recommended, attempt, corrections, problems)

    def plan_week(self, ingredients: list[str], prefs: Preferences, days: int = 5) -> tuple[MealPlan, AgentResult]:
        days = max(1, min(days, 7))
        extra = (
            f"This is a {days}-day dinner plan. Vary cuisines and proteins across days, "
            "and reuse perishable extras (herbs, dairy, vegetables) across recipes to minimise food waste."
        )
        result = self.suggest(ingredients, prefs, count=days, extra=extra)
        plan = MealPlan(days=[DayPlan(day=DAYS[i], recipe=r) for i, r in enumerate(result.recipes)])
        return plan, result


# --- Offline demo backend ------------------------------------------------
# Lets the app, CLI and tests run without an API key. Produces simple but
# well-formed recipes built from whatever the user has.

_TEMPLATES = [
    ("{main} Masala", "North Indian", "Easy", 10, 20),
    ("Jeera {main} Sabzi", "Punjabi", "Easy", 10, 15),
    ("Kadai {main}", "Punjabi", "Medium", 15, 25),
    ("{main} Curry", "South Indian", "Medium", 15, 30),
    ("{main} Pulao", "North Indian", "Easy", 10, 25),
    ("{main} Thoran", "Kerala", "Easy", 10, 15),
    ("Tawa {main}", "Mumbai Street", "Easy", 10, 15),
]


def demo_recipes(ingredients: list[str], prefs: Preferences, count: int) -> RecipeSet:
    from .samples import match_library

    recipes = match_library(ingredients, prefs, count)
    if len(recipes) < count:
        recipes += _template_recipes(ingredients, prefs, count - len(recipes), offset=len(recipes))
    return RecipeSet(recipes=recipes, recommended=recipes[0].name)


def _template_recipes(ingredients: list[str], prefs: Preferences, count: int, offset: int = 0) -> list[Recipe]:
    pool = [i for i in ingredients if i] or ["chickpeas", "rice", "onion"]
    allowed = [i for i in pool if not check_recipe(_stub(i), prefs)] or ["rice"]
    recipes = []
    for n in range(offset, offset + count):
        title, cuisine, diff, prep, cook = _TEMPLATES[n % len(_TEMPLATES)]
        if prefs.max_minutes and prep + cook > prefs.max_minutes:
            prep, cook = prefs.max_minutes // 3, prefs.max_minutes - prefs.max_minutes // 3
        main = allowed[n % len(allowed)]
        used = [Ingredient(name=i, quantity=100 * prefs.servings / 2, unit="g") for i in allowed[:5]]
        extras = [Ingredient(name="oil", quantity=2, unit="tbsp"), Ingredient(name="fresh coriander", quantity=1, unit="handful")]
        recipes.append(
            Recipe(
                name=title.format(main=main.title()),
                cuisine=cuisine,
                difficulty=diff,
                prep_minutes=prep,
                cook_minutes=cook,
                servings=prefs.servings,
                ingredients=used + extras,
                missing_ingredients=extras[1:],
                instructions=[
                    f"Prep the {', '.join(allowed[:5])}: wash, then chop into bite-sized pieces.",
                    "Heat the oil in a kadai and splutter 1 tsp cumin seeds.",
                    f"Cook the {main} with a pinch of turmeric until golden, about {max(cook // 2, 3)} minutes.",
                    "Add the remaining ingredients and 1 tsp garam masala, season with salt, and cook until tender.",
                    "Finish with chopped coriander and serve hot with roti or rice.",
                ],
                nutrition_per_serving=Nutrition(calories=420 + 25 * n, protein_g=22, carbs_g=38, fat_g=16),
                substitutions=["oil -> ghee (not vegan)", "garam masala -> curry powder"],
                tips="Demo mode recipe. Set OPENAI_API_KEY to get real AI-generated recipes.",
            )
        )
    return recipes


def _stub(name: str) -> Recipe:
    return Recipe(
        name=name, cuisine="", difficulty="Easy", prep_minutes=0, cook_minutes=0, servings=1,
        ingredients=[Ingredient(name=name)], instructions=[],
        nutrition_per_serving=Nutrition(calories=0, protein_g=0, carbs_g=0, fat_g=0),
    )
