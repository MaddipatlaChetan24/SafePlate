"""Streamlit web UI.  Run with:  streamlit run app.py"""

from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

from safeplate.agent import RecipeAgent
from safeplate.export import plan_markdown, recipe_markdown, slugify
from safeplate.models import Preferences, Recipe
from safeplate.shopping import shopping_list, shopping_list_text
from safeplate.storage import Store

load_dotenv()
st.set_page_config(page_title="SafePlate", page_icon="🍳", layout="wide")


@st.cache_resource
def get_store() -> Store:
    return Store()


store = get_store()


def render_recipe(recipe: Recipe, key: str, recommended: bool = False, saved_id: int | None = None) -> None:
    n = recipe.nutrition_per_serving
    with st.expander(f"{'⭐ ' if recommended else ''}{recipe.name}  ·  {recipe.cuisine}  ·  {recipe.total_minutes} min", expanded=recommended):
        c = st.columns(4)
        c[0].metric("Calories", n.calories)
        c[1].metric("Protein", f"{n.protein_g:g} g")
        c[2].metric("Carbs", f"{n.carbs_g:g} g")
        c[3].metric("Fat", f"{n.fat_g:g} g")

        servings = st.number_input("Servings", 1, 20, recipe.servings, key=f"{key}-serv")
        shown = recipe.scaled(servings) if servings != recipe.servings else recipe

        left, right = st.columns([1, 2])
        with left:
            st.markdown("**Ingredients**")
            st.markdown("\n".join(f"- {i.label()}" for i in shown.ingredients))
            if shown.missing_ingredients:
                st.markdown("**To buy**")
                st.markdown("\n".join(f"- {i.label()}" for i in shown.missing_ingredients))
        with right:
            st.markdown("**Steps**")
            st.markdown("\n".join(f"{k}. {s}" for k, s in enumerate(shown.instructions, 1)))
            if shown.substitutions:
                st.markdown("**Swaps:** " + "; ".join(shown.substitutions))
            if shown.tips:
                st.info(f"💡 {shown.tips}")

        b = st.columns(3)
        if saved_id is None and b[0].button("💾 Save to cookbook", key=f"{key}-save"):
            store.save_recipe(recipe)
            st.toast(f"Saved {recipe.name}")
        b[1].download_button("⬇️ Markdown", recipe_markdown(shown), f"{slugify(recipe.name)}.md", key=f"{key}-dl")
        if saved_id is not None and b[2].button("🗑 Delete", key=f"{key}-del"):
            store.delete_recipe(saved_id)
            st.rerun()


# --- Sidebar: preferences & pantry ----------------------------------------
with st.sidebar:
    st.header("🥗 Preferences")
    diet = st.selectbox("Diet", ["", "vegetarian", "vegan", "pescatarian", "keto", "gluten-free", "dairy-free", "high-protein"])
    allergies = st.multiselect("Allergies", ["nuts", "peanut", "dairy", "gluten", "egg", "shellfish", "fish", "soy", "sesame"])
    cuisine = st.text_input("Preferred cuisine")
    max_minutes = st.slider("Max total time (0 = any)", 0, 120, 0, step=5)
    servings = st.number_input("Servings", 1, 20, 2)
    skill = st.selectbox("Skill level", ["", "beginner", "intermediate", "advanced"])
    prefs = Preferences(diet=diet, allergies=allergies, cuisine=cuisine, max_minutes=max_minutes, servings=servings, skill=skill)

    st.header("🥫 Pantry")
    new = st.text_input("Add items (comma-separated)", key="pantry_new")
    if st.button("Add") and new:
        store.pantry_add(new.split(","))
        st.rerun()
    pantry = store.pantry_list()
    remove = st.multiselect("Your pantry", pantry, default=[], placeholder=f"{len(pantry)} items — select to remove")
    if remove and st.button("Remove selected"):
        store.pantry_remove(remove)
        st.rerun()
    st.caption(", ".join(pantry) or "Empty")

agent = RecipeAgent()
st.title("🍳 SafePlate")
if agent.demo:
    st.warning("Demo mode: no OPENAI_API_KEY found, so recipes are placeholders. Add a key to `.env` for real results.")

tab_suggest, tab_plan, tab_book, tab_hist = st.tabs(["✨ Suggest", "🗓 Meal plan", "📖 Cookbook", "🕘 History"])

with tab_suggest:
    text = st.text_input("What's in your fridge?", placeholder="chicken, garlic, lemon, rosemary")
    use_pantry = st.checkbox("Also use my pantry", value=bool(pantry))
    count = st.slider("Number of recipes", 1, 6, 3)
    if st.button("Find recipes", type="primary"):
        ingredients = [t.strip() for t in text.split(",") if t.strip()]
        if use_pantry:
            ingredients += [p for p in pantry if p not in ingredients]
        liked = store.favourite_cuisines()
        extra = f"The user has rated these cuisines highly: {', '.join(liked)}." if liked and not cuisine else ""
        with st.spinner("Cooking up ideas..."):
            st.session_state.result = agent.suggest(ingredients, prefs, count=count, extra=extra)
        store.log_search(ingredients, prefs, st.session_state.result.recipes)

    result = st.session_state.get("result")
    if result:
        if result.corrections:
            st.success(f"🛡 Safety check caught {len(result.corrections)} issue(s) and the agent self-corrected.")
            with st.expander("What was fixed"):
                st.write(result.corrections)
        for k, r in enumerate(result.recipes):
            render_recipe(r, key=f"s{k}", recommended=r.name == result.recommended)
        items = shopping_list(result.recipes, pantry)
        if items:
            st.subheader("🛒 Shopping list")
            st.code(shopping_list_text(items), language=None)

with tab_plan:
    days = st.slider("Days", 1, 7, 5)
    plan_text = st.text_input("Ingredients to use up", key="plan_ing")
    if st.button("Plan my week", type="primary"):
        ingredients = [t.strip() for t in plan_text.split(",") if t.strip()] + pantry
        with st.spinner(f"Planning {days} dinners..."):
            st.session_state.plan, _ = agent.plan_week(ingredients, prefs, days)
    plan = st.session_state.get("plan")
    if plan:
        st.table([{"Day": d.day, "Recipe": d.recipe.name, "Cuisine": d.recipe.cuisine, "Minutes": d.recipe.total_minutes,
                   "kcal": d.recipe.nutrition_per_serving.calories} for d in plan.days])
        st.subheader("🛒 Weekly shopping list")
        st.code(shopping_list_text(shopping_list([d.recipe for d in plan.days], pantry)), language=None)
        st.download_button("⬇️ Download full plan (Markdown)", plan_markdown(plan, pantry), "meal-plan.md")
        for d in plan.days:
            render_recipe(d.recipe, key=f"p-{d.day}")

with tab_book:
    search = st.text_input("Search cookbook")
    rows = store.list_recipes(search)
    if not rows:
        st.caption("Nothing saved yet.")
    for row in rows:
        cols = st.columns([4, 1])
        rating = cols[1].select_slider("Rating", [0, 1, 2, 3, 4, 5], value=row["rating"] or 0, key=f"rate{row['id']}")
        if rating and rating != row["rating"]:
            store.rate_recipe(row["id"], rating)
        with cols[0]:
            render_recipe(row["recipe"], key=f"b{row['id']}", saved_id=row["id"])

with tab_hist:
    for h in store.history():
        st.markdown(f"**{h['created_at'].replace('T', ' ')}** — {', '.join(h['ingredients']) or '(pantry staples)'}  \n→ {'; '.join(h['results'])}")
