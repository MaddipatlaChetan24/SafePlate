from __future__ import annotations

import pytest

from safeplate.agent import RecipeAgent
from safeplate.export import plan_markdown, recipe_markdown
from safeplate.models import Ingredient, Nutrition, Preferences, Recipe, RecipeSet
from safeplate.safety import check_recipe
from safeplate.shopping import shopping_list
from safeplate.storage import Store


def make_recipe(name="Test", ingredients=("rice",), missing=(), minutes=(10, 20), servings=2, cuisine="Thai") -> Recipe:
    return Recipe(
        name=name, cuisine=cuisine, difficulty="Easy", prep_minutes=minutes[0], cook_minutes=minutes[1], servings=servings,
        ingredients=[Ingredient(name=i, quantity=100, unit="g") for i in ingredients],
        missing_ingredients=[Ingredient(name=i, quantity=50, unit="g") for i in missing],
        instructions=["Cook."], nutrition_per_serving=Nutrition(calories=400, protein_g=20, carbs_g=40, fat_g=10),
    )


# --- models ----------------------------------------------------------------

def test_scaling_doubles_quantities_and_keeps_to_taste():
    r = make_recipe(servings=2)
    r.ingredients.append(Ingredient(name="salt"))
    s = r.scaled(4)
    assert s.servings == 4
    assert s.ingredients[0].quantity == 200
    assert s.ingredients[-1].quantity is None
    assert r.ingredients[0].quantity == 100  # original untouched


def test_scaling_rejects_zero():
    with pytest.raises(ValueError):
        make_recipe().scaled(0)


def test_ingredient_label():
    assert Ingredient(name="garlic", quantity=2, unit="clove").label() == "2 clove garlic"
    assert Ingredient(name="eggs", quantity=1.5).label() == "1.5 eggs"
    assert Ingredient(name="salt").label() == "salt (to taste)"


# --- safety ----------------------------------------------------------------

@pytest.mark.parametrize(
    "ingredient,prefs,bad",
    [
        ("cashews", Preferences(allergies=["nuts"]), True),
        ("coconut milk", Preferences(allergies=["nuts", "dairy"]), False),
        ("almond milk", Preferences(allergies=["dairy"]), False),
        ("almond milk", Preferences(allergies=["nuts"]), True),
        ("parmesan", Preferences(diet="vegan"), True),
        ("eggplant", Preferences(diet="vegan"), False),
        ("champignon mushrooms", Preferences(diet="vegetarian"), False),
        ("ham", Preferences(diet="vegetarian"), True),
        ("salmon", Preferences(diet="pescatarian"), False),
        ("soy sauce", Preferences(diet="gluten-free"), True),
        ("nutmeg", Preferences(allergies=["nuts"]), False),
        ("kiwi", Preferences(allergies=["kiwi"]), True),  # unknown allergy falls back to literal match
        # Regressions found by evaluation/allergen_benchmark.py
        ("anchovies", Preferences(allergies=["fish"]), True),
        ("vegan cheese", Preferences(diet="vegan"), False),
    ],
)
def test_constraint_checks(ingredient, prefs, bad):
    assert bool(check_recipe(make_recipe(ingredients=[ingredient]), prefs)) is bad


def test_time_limit():
    assert check_recipe(make_recipe(minutes=(20, 30)), Preferences(max_minutes=30))
    assert not check_recipe(make_recipe(minutes=(10, 15)), Preferences(max_minutes=30))


# --- agent self-correction loop -------------------------------------------

class ScriptedAgent(RecipeAgent):
    """Returns pre-baked responses in order and records the conversation."""

    def __init__(self, responses, **kw):
        super().__init__(demo=True, **kw)
        self.responses = list(responses)
        self.seen = []

    def _call(self, messages, ingredients, prefs, count):
        self.seen.append(list(messages))
        return self.responses.pop(0)


def test_agent_retries_and_feeds_back_violations():
    bad = RecipeSet(recipes=[make_recipe("Pesto", ingredients=["pine nuts", "basil"])], recommended="Pesto")
    good = RecipeSet(recipes=[make_recipe("Basil Oil", ingredients=["basil"])], recommended="Basil Oil")
    agent = ScriptedAgent([bad, good])
    result = agent.suggest(["basil"], Preferences(allergies=["nuts"]), count=1)

    assert result.attempts == 2
    assert [r.name for r in result.recipes] == ["Basil Oil"]
    assert result.corrections and not result.unresolved
    assert "pine nuts" in agent.seen[1][-1][1]  # violation was sent back to the model


def test_agent_drops_unsafe_recipes_after_max_retries():
    bad = RecipeSet(
        recipes=[make_recipe("Satay", ingredients=["peanut"]), make_recipe("Rice", ingredients=["rice"])],
        recommended="Satay",
    )
    agent = ScriptedAgent([bad] * 3, max_retries=2)
    result = agent.suggest(["rice"], Preferences(allergies=["peanut"]), count=2)

    assert result.attempts == 3
    assert [r.name for r in result.recipes] == ["Rice"]
    assert result.recommended == "Rice"
    assert result.unresolved


def test_demo_mode_respects_constraints():
    agent = RecipeAgent(demo=True)
    result = agent.suggest(["chicken", "tofu", "rice"], Preferences(diet="vegan", max_minutes=20), count=3)
    assert len(result.recipes) == 3
    assert not result.unresolved
    assert all(r.total_minutes <= 20 for r in result.recipes)


def test_meal_plan_days():
    plan, _ = RecipeAgent(demo=True).plan_week(["lentils", "spinach"], Preferences(), days=4)
    assert [d.day for d in plan.days] == ["Monday", "Tuesday", "Wednesday", "Thursday"]
    assert "Shopping list" in plan_markdown(plan)


# --- shopping --------------------------------------------------------------

def test_shopping_list_merges_and_skips_pantry_and_staples():
    a = make_recipe(missing=["onion", "tomatoes", "salt"])
    b = make_recipe(missing=["onions", "basil"])
    items = {i.name: i.quantity for i in shopping_list([a, b], pantry=["basil"])}
    assert items == {"onion": 100, "tomatoes": 50}


# --- storage ---------------------------------------------------------------

@pytest.fixture
def store(tmp_path):
    s = Store(tmp_path / "test.db")
    yield s
    s.close()


def test_pantry_roundtrip(store):
    store.pantry_add(["Rice", " onion ", "rice", ""])
    assert store.pantry_list() == ["onion", "rice"]
    store.pantry_remove(["ONION"])
    assert store.pantry_list() == ["rice"]


def test_cookbook_save_rate_and_favourites(store):
    a = store.save_recipe(make_recipe("A", cuisine="Thai"))
    b = store.save_recipe(make_recipe("B", cuisine="Thai"))
    c = store.save_recipe(make_recipe("C", cuisine="Italian"))
    store.rate_recipe(a, 5)
    store.rate_recipe(b, 4)
    store.rate_recipe(c, 2)
    assert store.get_recipe(a).name == "A"
    assert store.favourite_cuisines() == ["Thai"]
    assert [r["recipe"].name for r in store.list_recipes("B")] == ["B"]
    with pytest.raises(ValueError):
        store.rate_recipe(a, 9)
    assert store.delete_recipe(c) and store.get_recipe(c) is None


def test_history(store):
    store.log_search(["egg"], Preferences(), [make_recipe("Omelette")])
    assert store.history()[0]["results"] == ["Omelette"]


def test_markdown_export():
    md = recipe_markdown(make_recipe("Fried Rice", missing=["scallion"]))
    assert md.startswith("# Fried Rice")
    assert "You'll need to buy" in md
