"""Curated offline recipe library used in demo mode (no API key).

Recipes are matched against the user's ingredients, filtered through the same
safety rules as LLM output, and scaled to the requested servings.
"""

from __future__ import annotations

from .models import Ingredient, Nutrition, Preferences, Recipe
from .safety import check_recipe
from .shopping import STAPLES, ingredient_matches


def _ing(spec: str) -> Ingredient:
    qty, unit, name = spec.split("|")
    return Ingredient(name=name, quantity=float(qty) if qty else None, unit=unit)


def _recipe(name, cuisine, difficulty, prep, cook, ingredients, steps, kcal, p, c, f, subs, tip) -> Recipe:
    return Recipe(
        name=name, cuisine=cuisine, difficulty=difficulty, prep_minutes=prep, cook_minutes=cook, servings=2,
        ingredients=[_ing(s) for s in ingredients], instructions=steps,
        nutrition_per_serving=Nutrition(calories=kcal, protein_g=p, carbs_g=c, fat_g=f),
        substitutions=subs, tips=tip,
    )


LIBRARY: list[Recipe] = [
    _recipe(
        "Lemon Rosemary Chicken with Crispy Potatoes", "Mediterranean", "Easy", 15, 40,
        ["2||chicken breast", "400|g|potatoes", "4|clove|garlic", "1||lemon", "2|sprig|rosemary", "3|tbsp|olive oil", "||salt"],
        ["Heat the oven to 220°C. Halve the potatoes and toss with 2 tbsp oil, salt and chopped rosemary.",
         "Roast the potatoes for 20 minutes while you marinate the chicken in lemon juice, zest, crushed garlic and the rest of the oil.",
         "Push the potatoes aside, add the chicken and lemon halves to the tray, and roast 18-20 minutes until the chicken reaches 74°C.",
         "Rest the chicken for 5 minutes, slice, and squeeze the roasted lemon over everything."],
        520, 42, 38, 20, ["chicken breast -> thighs (juicier, +5 min)", "rosemary -> thyme"],
        "Dry the potatoes well before oiling them; moisture is the enemy of crispiness.",
    ),
    _recipe(
        "Ginger Garlic Tofu & Broccoli Stir-Fry", "Asian", "Easy", 10, 12,
        ["400|g|firm tofu", "1||broccoli", "1|tbsp|ginger", "3|clove|garlic", "3|tbsp|soy sauce", "1|tbsp|maple syrup",
         "1|tsp|cornstarch", "150|g|jasmine rice", "2||scallions"],
        ["Press the tofu for 10 minutes, cube it, and toss in cornstarch.",
         "Pan-fry the tofu in a hot wok with a little oil until golden on all sides, then set aside.",
         "Stir-fry the broccoli florets for 3 minutes, add grated ginger and garlic for 30 seconds.",
         "Return the tofu, add soy sauce and maple syrup, and toss until glossy. Serve over rice with scallions."],
        430, 24, 52, 14, ["soy sauce -> tamari (gluten-free)", "maple syrup -> brown sugar"],
        "Cornstarch on the tofu gives you a crisp crust that soaks up the sauce.",
    ),
    _recipe(
        "Tomato Basil Pasta Pomodoro", "Italian", "Easy", 10, 15,
        ["200|g|spaghetti", "400|g|tomatoes", "3|clove|garlic", "1|handful|basil", "30|g|parmesan", "3|tbsp|olive oil"],
        ["Boil the pasta in well-salted water until al dente; save a mug of pasta water.",
         "Gently fry sliced garlic in the oil, then add chopped tomatoes and simmer 10 minutes until jammy.",
         "Toss the pasta into the sauce with a splash of pasta water until it clings.",
         "Tear in the basil, finish with grated parmesan and a drizzle of oil."],
        510, 17, 78, 14, ["fresh tomatoes -> 1 can whole San Marzano", "parmesan -> nutritional yeast (vegan)"],
        "Starchy pasta water is what turns oil and tomato into a silky sauce.",
    ),
    _recipe(
        "Chickpea & Spinach Coconut Curry", "Indian", "Easy", 10, 25,
        ["400|g|chickpeas", "100|g|spinach", "400|ml|coconut milk", "1||onion", "3|clove|garlic", "1|tbsp|ginger",
         "2|tbsp|curry powder", "200|g|tomatoes", "150|g|basmati rice"],
        ["Soften the diced onion in oil for 5 minutes, then add garlic, ginger and curry powder for 1 minute.",
         "Add chopped tomatoes and cook down for 5 minutes.",
         "Stir in the chickpeas and coconut milk; simmer 12 minutes until thickened.",
         "Wilt in the spinach, season, and serve with basmati rice."],
        480, 15, 62, 19, ["chickpeas -> red lentils (add 10 min)", "spinach -> kale"],
        "Blooming the spices in oil before adding liquid doubles the flavour.",
    ),
    _recipe(
        "Black Bean & Sweet Potato Tacos", "Mexican", "Easy", 15, 25,
        ["1||sweet potato", "400|g|black beans", "6||corn tortillas", "1||lime", "1||avocado", "0.5||red onion",
         "1|tsp|cumin", "1|handful|coriander"],
        ["Roast cubed sweet potato with oil, cumin and salt at 210°C for 25 minutes.",
         "Warm the black beans with a pinch of cumin and a squeeze of lime, lightly mashing half of them.",
         "Quick-pickle the sliced red onion in lime juice and salt.",
         "Char the tortillas, then fill with beans, sweet potato, avocado, pickled onion and coriander."],
        460, 13, 72, 14, ["sweet potato -> butternut squash", "corn tortillas -> lettuce cups"],
        "A 10-minute lime pickle on the onion takes these from good to great.",
    ),
    _recipe(
        "Honey Soy Glazed Salmon with Bok Choy", "Japanese", "Easy", 10, 15,
        ["2||salmon fillets", "2|tbsp|soy sauce", "1|tbsp|honey", "2|clove|garlic", "1|tsp|ginger", "2||bok choy",
         "150|g|sushi rice"],
        ["Whisk soy sauce, honey, grated garlic and ginger into a glaze.",
         "Sear the salmon skin-side down for 4 minutes, flip, and pour over the glaze.",
         "Baste for 2-3 minutes until the glaze is sticky and the salmon is just cooked.",
         "Steam the halved bok choy for 3 minutes and serve everything over rice."],
        540, 36, 48, 21, ["salmon -> chicken thighs", "honey -> maple syrup"],
        "Pull the salmon when the centre is still slightly translucent; it finishes cooking off the heat.",
    ),
    _recipe(
        "Mushroom & Spinach Frittata", "French", "Easy", 10, 18,
        ["6||eggs", "200|g|mushrooms", "80|g|spinach", "1||onion", "60|g|feta cheese", "1|tbsp|butter"],
        ["Heat the grill. Fry the sliced onion and mushrooms in butter in an oven-safe pan for 6 minutes.",
         "Add the spinach until wilted.",
         "Pour over beaten, seasoned eggs and crumble in the feta; cook on low for 6 minutes.",
         "Finish under the grill for 3-4 minutes until puffed and set."],
        340, 22, 8, 24, ["feta -> goat cheese", "spinach -> kale or chard"],
        "Cook the mushrooms until all their water evaporates, or the frittata turns soggy.",
    ),
    _recipe(
        "Red Lentil & Vegetable Soup", "Middle Eastern", "Easy", 10, 30,
        ["150|g|red lentils", "2||carrots", "1||onion", "2|stalk|celery", "3|clove|garlic", "1|tsp|cumin",
         "200|g|tomatoes", "1||lemon"],
        ["Soften the diced onion, carrot and celery in oil for 8 minutes.",
         "Add garlic and cumin for 1 minute, then the lentils, tomatoes and 1 litre of water.",
         "Simmer 20 minutes until the lentils collapse.",
         "Blend half the soup for body, season, and finish with lemon juice."],
        320, 18, 50, 5, ["red lentils -> yellow split peas (+20 min)", "cumin -> smoked paprika"],
        "The squeeze of lemon at the end is not optional; it wakes the whole pot up.",
    ),
    _recipe(
        "Shakshuka with Peppers", "North African", "Easy", 10, 20,
        ["4||eggs", "400|g|tomatoes", "1||red bell pepper", "1||onion", "2|clove|garlic", "1|tsp|smoked paprika",
         "1|tsp|cumin", "2|slice|crusty bread"],
        ["Fry the sliced onion and pepper for 8 minutes until soft and sweet.",
         "Add garlic, paprika and cumin, then the tomatoes; simmer 8 minutes until thick.",
         "Make 4 wells, crack in the eggs, cover and cook 5-6 minutes until the whites set.",
         "Serve straight from the pan with toasted bread."],
        360, 19, 34, 16, ["crusty bread -> gluten-free toast", "eggs -> crumbled firm tofu (vegan)"],
        "Season the sauce boldly before the eggs go in; you can't stir it afterwards.",
    ),
    _recipe(
        "Thai Peanut Noodle Salad", "Thai", "Easy", 20, 5,
        ["150|g|rice noodles", "3|tbsp|peanut butter", "0.25||red cabbage", "2||carrots", "1||cucumber", "1||lime",
         "2|tbsp|soy sauce", "1|handful|coriander"],
        ["Soak or boil the rice noodles per the packet, then rinse under cold water.",
         "Whisk peanut butter, soy sauce, lime juice and warm water into a pourable dressing.",
         "Shred the cabbage and julienne the carrots and cucumber.",
         "Toss everything with the dressing and top with coriander."],
        490, 16, 64, 19, ["peanut butter -> sunflower seed butter (nut-free)", "rice noodles -> soba"],
        "Rinsing the noodles in cold water stops them sticking together in the salad.",
    ),
]


def match_library(ingredients: list[str], prefs: Preferences, count: int) -> list[Recipe]:
    """Best library matches for the given ingredients that pass every constraint."""
    scored = []
    for base in LIBRARY:
        recipe = base.scaled(prefs.servings) if prefs.servings != base.servings else base.model_copy(deep=True)
        if check_recipe(recipe, prefs):
            continue
        used = [i for i in recipe.ingredients if any(ingredient_matches(u, i.name) for u in ingredients)]
        missing = [i for i in recipe.ingredients if i not in used and i.name.lower() not in STAPLES and i.quantity is not None]
        recipe.missing_ingredients = missing
        scored.append((len(used), -len(missing), recipe))
    scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
    return [r for *_, r in scored[:count]]
