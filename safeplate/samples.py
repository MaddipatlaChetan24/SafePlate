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
        "Paneer Butter Masala", "Punjabi", "Medium", 15, 25,
        ["200|g|paneer", "300|g|tomatoes", "2|tbsp|butter", "60|ml|fresh cream", "15|g|cashews", "1|tbsp|ginger garlic paste",
         "1|tsp|kashmiri chilli powder", "1|tsp|garam masala", "1|tsp|kasuri methi", "||salt"],
        ["Simmer the chopped tomatoes and cashews in a little water for 10 minutes, then blend to a smooth purée.",
         "Melt the butter, fry the ginger garlic paste for a minute, add the chilli powder and the purée, and cook 8 minutes until the butter separates.",
         "Stir in the cream, garam masala and crushed kasuri methi; simmer 2 minutes.",
         "Add the paneer cubes, warm through for 3 minutes, and serve with naan or jeera rice."],
        520, 20, 18, 40, ["cream -> extra cashew paste", "paneer -> firm tofu (dairy-free)"],
        "Crush the kasuri methi between your palms before adding it; that's where the dhaba flavour comes from.",
    ),
    _recipe(
        "Chana Masala", "Punjabi", "Easy", 10, 30,
        ["400|g|chickpeas", "1||onion", "2||tomatoes", "1|tbsp|ginger", "3|clove|garlic", "1||green chilli",
         "2|tsp|chana masala powder", "1|tsp|cumin seeds", "1|handful|coriander"],
        ["Splutter the cumin seeds in hot oil, then fry the finely chopped onion until deep golden, about 8 minutes.",
         "Add grated ginger, garlic and green chilli for 1 minute, then the chopped tomatoes; cook until pulpy.",
         "Stir in the chana masala powder and chickpeas with 1 cup of water; simmer 15 minutes, mashing a few chickpeas to thicken.",
         "Finish with coriander and a squeeze of lemon. Serve with bhature, roti or rice."],
        380, 15, 52, 12, ["chana masala powder -> garam masala + amchur", "canned chickpeas -> soaked kabuli chana (pressure cook 4 whistles)"],
        "Brown the onions properly; pale onions give a flat, sweet gravy.",
    ),
    _recipe(
        "Dal Tadka with Jeera Rice", "North Indian", "Easy", 10, 30,
        ["150|g|toor dal", "1||onion", "1||tomato", "4|clove|garlic", "1|tsp|cumin seeds", "0.5|tsp|turmeric",
         "1|tbsp|ghee", "2||dried red chillies", "150|g|basmati rice", "1|handful|coriander"],
        ["Pressure cook the rinsed toor dal with turmeric and 2.5 cups of water for 3 whistles; whisk smooth.",
         "Cook the basmati rice with half the cumin seeds and a pinch of salt.",
         "Fry the onion and tomato in a little oil until soft, stir into the dal and simmer 5 minutes.",
         "For the tadka, heat ghee until smoking, add cumin, sliced garlic and red chillies, and pour it sizzling over the dal."],
        410, 17, 66, 8, ["ghee -> oil (vegan)", "toor dal -> masoor dal (cooks in 15 min without a cooker)"],
        "Pour the tadka at the table so everyone hears the sizzle; it's half the experience.",
    ),
    _recipe(
        "Palak Paneer", "Punjabi", "Medium", 15, 20,
        ["300|g|spinach", "200|g|paneer", "1||onion", "1||tomato", "1|tbsp|ginger", "3|clove|garlic", "1||green chilli",
         "1|tsp|cumin seeds", "2|tbsp|fresh cream"],
        ["Blanch the spinach for 2 minutes, plunge into ice water, then blend with the green chilli.",
         "Splutter cumin seeds in oil, fry the onion until golden, then add ginger, garlic and tomato.",
         "Add the spinach purée and simmer 5 minutes; don't overcook or it turns dull.",
         "Fold in the paneer and cream, warm through, and serve with roti."],
        420, 22, 14, 30, ["paneer -> tofu (vegan, skip cream)", "cream -> cashew paste"],
        "The ice bath keeps the palak bright green.",
    ),
    _recipe(
        "Aloo Gobi", "Punjabi", "Easy", 10, 25,
        ["300|g|potatoes", "400|g|cauliflower", "1||onion", "1||tomato", "1|tbsp|ginger", "0.5|tsp|turmeric",
         "1|tsp|cumin seeds", "1|tsp|coriander powder", "1|handful|coriander"],
        ["Splutter the cumin seeds in oil and fry the onion until soft.",
         "Add the ginger, turmeric and coriander powder, then the potato cubes; cook covered for 8 minutes.",
         "Add the cauliflower florets and chopped tomato, cover and cook on low for 12 minutes, stirring gently.",
         "Uncover for the last few minutes so the edges char, then finish with fresh coriander."],
        260, 7, 34, 11, ["potatoes -> sweet potato", "fresh tomato -> 1 tsp amchur"],
        "Cook it covered on low heat without water; the vegetables steam in their own moisture and don't go mushy.",
    ),
    _recipe(
        "Rajma Chawal", "Punjabi", "Easy", 10, 35,
        ["400|g|kidney beans", "1||onion", "200|g|tomatoes", "1|tbsp|ginger", "3|clove|garlic", "1|tsp|garam masala",
         "1|tsp|cumin seeds", "150|g|basmati rice"],
        ["Fry the cumin seeds and chopped onion until golden, then add ginger and garlic.",
         "Add the tomato purée and cook until the oil separates, about 8 minutes.",
         "Add the kidney beans with 1.5 cups of water and garam masala; simmer 20 minutes, mashing some beans for a creamy gravy.",
         "Serve over steamed basmati rice with sliced onion."],
        480, 18, 82, 7, ["canned rajma -> overnight-soaked rajma (pressure cook 6 whistles)", "basmati -> brown rice"],
        "Rajma tastes better the next day; make extra.",
    ),
    _recipe(
        "Butter Chicken", "Punjabi", "Medium", 20, 30,
        ["400|g|chicken thighs", "100|g|yogurt", "300|g|tomatoes", "2|tbsp|butter", "60|ml|fresh cream", "15|g|cashews",
         "1|tbsp|ginger garlic paste", "1|tsp|kashmiri chilli powder", "1|tsp|garam masala", "1|tsp|kasuri methi"],
        ["Marinate the chicken in yogurt, half the ginger garlic paste and chilli powder for at least 20 minutes.",
         "Sear the chicken in a hot pan until charred at the edges; set aside.",
         "Simmer tomatoes and cashews, blend smooth, then cook in butter with the remaining paste for 8 minutes.",
         "Add the chicken, cream, garam masala and kasuri methi; simmer 10 minutes until the chicken is cooked through."],
        590, 42, 16, 40, ["chicken thighs -> paneer (vegetarian)", "cream -> coconut cream (dairy-free, with oil instead of butter)"],
        "Thighs stay juicy where breast dries out; char them hard for the tandoor flavour.",
    ),
    _recipe(
        "Kerala Fish Curry", "Kerala", "Easy", 10, 20,
        ["400|g|fish fillets", "400|ml|coconut milk", "1||onion", "2||green chillies", "1|tbsp|ginger", "3|clove|garlic",
         "10||curry leaves", "0.5|tsp|turmeric", "2|tbsp|coconut oil"],
        ["Heat the coconut oil, add curry leaves, then sauté the sliced onion, ginger, garlic and slit green chillies until soft.",
         "Add turmeric and the thin part of the coconut milk; bring to a gentle simmer.",
         "Slide in the fish and cook 6-8 minutes without stirring, just swirling the pan.",
         "Add the thick coconut milk, warm through without boiling, and serve with appam or rice."],
        430, 34, 10, 28, ["fish -> prawns (not for shellfish allergies)", "coconut oil -> any neutral oil"],
        "Never boil after the thick coconut milk goes in; it splits.",
    ),
    _recipe(
        "Egg Bhurji Pav", "Mumbai Street", "Easy", 5, 10,
        ["4||eggs", "1||onion", "1||tomato", "1||green chilli", "0.25|tsp|turmeric", "1|tbsp|butter",
         "1|handful|coriander", "4||pav"],
        ["Melt the butter and fry the chopped onion and green chilli until soft.",
         "Add the tomato and turmeric and cook 2 minutes.",
         "Pour in the beaten, salted eggs and scramble on low heat until just set.",
         "Fold in coriander and serve with butter-toasted pav."],
        380, 20, 30, 20, ["pav -> roti or gluten-free toast", "butter -> oil (dairy-free)"],
        "Take the bhurji off the heat while it's still a little wet; it keeps cooking.",
    ),
    _recipe(
        "Kanda Poha", "Maharashtrian", "Easy", 10, 10,
        ["150|g|poha", "1||onion", "1||potato", "30|g|peanuts", "1|tsp|mustard seeds", "10||curry leaves",
         "0.5|tsp|turmeric", "1||green chilli", "1||lemon", "1|handful|coriander"],
        ["Rinse the poha in a sieve until soft but not mushy; let it drain.",
         "Fry the peanuts until crunchy, then splutter mustard seeds and curry leaves.",
         "Add onion, green chilli and finely diced potato; cook covered until the potato is tender.",
         "Add turmeric and the poha, toss gently for 2 minutes, then finish with lemon and coriander."],
        360, 9, 55, 12, ["peanuts -> roasted chana dal (peanut-free)", "potato -> green peas"],
        "Add a pinch of sugar with the salt; it's how Pune makes it.",
    ),
    _recipe(
        "Lemon Rice", "South Indian", "Easy", 10, 10,
        ["300|g|cooked rice", "1||lemon", "1|tsp|mustard seeds", "1|tbsp|chana dal", "10||curry leaves", "1||green chilli",
         "0.5|tsp|turmeric", "25|g|peanuts", "1|tsp|ginger"],
        ["Spread the cooked rice out to cool so the grains stay separate.",
         "Fry the peanuts and chana dal until golden, then add mustard seeds, curry leaves, green chilli and ginger.",
         "Add turmeric, then the rice; toss gently over low heat.",
         "Turn off the heat and squeeze in the lemon juice."],
        340, 8, 58, 9, ["peanuts -> cashews (not nut-free)", "lemon -> raw mango (mango rice)"],
        "Add the lemon off the heat; cooked lemon juice turns bitter.",
    ),
    _recipe(
        "Vegetable Upma", "South Indian", "Easy", 10, 15,
        ["150|g|semolina", "1||onion", "1||carrot", "50|g|green peas", "1|tsp|mustard seeds", "10||curry leaves",
         "1||green chilli", "1|tsp|ginger", "1|tbsp|ghee"],
        ["Dry-roast the semolina until fragrant and set aside.",
         "Heat ghee, splutter mustard seeds and curry leaves, then sauté onion, ginger, chilli, carrot and peas.",
         "Pour in 2 cups of boiling salted water.",
         "Rain in the semolina while stirring constantly, cover and cook 3 minutes until fluffy."],
        330, 9, 52, 9, ["semolina -> broken millet or quinoa (gluten-free)", "ghee -> oil (vegan)"],
        "Roasting the rava first is what keeps upma from turning lumpy.",
    ),
    _recipe(
        "Pav Bhaji", "Mumbai Street", "Medium", 15, 30,
        ["300|g|potatoes", "150|g|cauliflower", "80|g|green peas", "1||capsicum", "300|g|tomatoes", "1||onion",
         "2|tbsp|pav bhaji masala", "3|tbsp|butter", "4||pav", "1||lemon"],
        ["Pressure cook the potatoes, cauliflower and peas until soft, then mash.",
         "Fry the onion and capsicum in 2 tbsp butter, add tomatoes and pav bhaji masala, and cook until mushy.",
         "Add the mashed vegetables with a splash of water and mash everything together on the heat for 8 minutes.",
         "Toast the pav in the remaining butter and serve with onion and lemon."],
        520, 13, 68, 22, ["butter -> oil (vegan)", "pav -> gluten-free buns"],
        "Mash on the tawa, not in a bowl; the bhaji should look rough, not puréed.",
    ),
    _recipe(
        "Hyderabadi Chicken Biryani", "Hyderabadi", "Hard", 30, 45,
        ["200|g|basmati rice", "400|g|chicken", "100|g|yogurt", "2||onions", "2|tbsp|biryani masala", "1|handful|mint",
         "1|pinch|saffron", "2|tbsp|ghee", "1|tbsp|ginger garlic paste"],
        ["Marinate the chicken in yogurt, biryani masala, ginger garlic paste and mint for 30 minutes.",
         "Fry thinly sliced onions in ghee until deep brown (birista); keep half for layering.",
         "Parboil the basmati rice until 70% cooked.",
         "Layer the chicken, rice, birista, mint and saffron milk in a heavy pot, seal and cook on dum for 25 minutes."],
        650, 38, 70, 22, ["chicken -> mixed vegetables + paneer (veg biryani)", "ghee -> oil"],
        "Seal the lid with dough or foil; the steam does the cooking on dum.",
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
    ranked = [r for *_, r in scored]
    # Prefer variety: take the best recipe from each region first, then fill by rank.
    picked, regions = [], set()
    for r in ranked:
        if len(picked) < count and r.cuisine not in regions:
            picked.append(r)
            regions.add(r.cuisine)
    picked += [r for r in ranked if r not in picked][: count - len(picked)]
    return sorted(picked, key=ranked.index)
