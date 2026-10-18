"""Typed data models for recipes, preferences and meal plans."""

from __future__ import annotations

import math
from typing import Literal

from pydantic import BaseModel, Field


class Ingredient(BaseModel):
    name: str = Field(description="Ingredient name, lowercase, no quantity (e.g. 'garlic')")
    quantity: float | None = Field(default=None, description="Numeric amount, null if 'to taste'")
    unit: str = Field(default="", description="Unit such as g, ml, tbsp, cup, clove; empty for countable items")

    def label(self) -> str:
        if self.quantity is None:
            return f"{self.name} (to taste)"
        qty = _fmt_qty(self.quantity)
        return f"{qty} {self.unit} {self.name}".replace("  ", " ").strip()


class Nutrition(BaseModel):
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float


class Recipe(BaseModel):
    name: str
    cuisine: str
    difficulty: Literal["Easy", "Medium", "Hard"]
    prep_minutes: int
    cook_minutes: int
    servings: int
    ingredients: list[Ingredient] = Field(description="Everything the recipe uses, with amounts")
    missing_ingredients: list[Ingredient] = Field(
        default_factory=list, description="Ingredients used that the user did NOT list"
    )
    instructions: list[str] = Field(description="Ordered steps, without 'Step N:' prefixes")
    nutrition_per_serving: Nutrition
    substitutions: list[str] = Field(default_factory=list, description="Useful swaps, e.g. 'butter -> olive oil'")
    tips: str = ""

    @property
    def total_minutes(self) -> int:
        return self.prep_minutes + self.cook_minutes

    def scaled(self, servings: int) -> "Recipe":
        """Return a copy with ingredient quantities scaled to a new serving count.

        Per-serving nutrition is unchanged; times are left as-is because cook time
        does not scale linearly with quantity.
        """
        if servings <= 0:
            raise ValueError("servings must be positive")
        factor = servings / self.servings

        def scale(items: list[Ingredient]) -> list[Ingredient]:
            return [
                i.model_copy(update={"quantity": None if i.quantity is None else round(i.quantity * factor, 2)})
                for i in items
            ]

        return self.model_copy(
            update={
                "servings": servings,
                "ingredients": scale(self.ingredients),
                "missing_ingredients": scale(self.missing_ingredients),
            }
        )


class RecipeSet(BaseModel):
    recipes: list[Recipe]
    recommended: str = Field(description="Name of the best-matching recipe")


class Preferences(BaseModel):
    diet: str = ""
    allergies: list[str] = Field(default_factory=list)
    cuisine: str = ""
    max_minutes: int = 0
    servings: int = 2
    skill: str = ""

    def describe(self) -> str:
        lines = []
        if self.diet:
            lines.append(f"Dietary restriction: {self.diet}")
        if self.allergies:
            lines.append(f"Allergies (must NOT appear in any form): {', '.join(self.allergies)}")
        if self.cuisine:
            lines.append(f"Preferred cuisine: {self.cuisine}")
        if self.max_minutes:
            lines.append(f"Max total time (prep + cook): {self.max_minutes} minutes")
        if self.skill:
            lines.append(f"Cook skill level: {self.skill}")
        lines.append(f"Servings: {self.servings}")
        return "\n".join(lines)


class DayPlan(BaseModel):
    day: str
    recipe: Recipe


class MealPlan(BaseModel):
    days: list[DayPlan]


def _fmt_qty(q: float) -> str:
    if math.isclose(q, round(q)):
        return str(int(round(q)))
    return f"{q:.2f}".rstrip("0").rstrip(".")
