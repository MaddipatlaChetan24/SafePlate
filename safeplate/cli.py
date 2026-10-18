"""Command-line interface.

    safeplate suggest --ingredients "chicken, garlic, lemon" --diet keto --save
    safeplate suggest --use-pantry --allergies nuts,dairy --time 30
    safeplate pantry add rice onion "soy sauce"
    safeplate plan --days 5 --use-pantry --export plans/
    safeplate cookbook list | show 3 --servings 6 | rate 3 5 | delete 3
    safeplate shop 1 4 7
    safeplate history
    safeplate serve            # web app on http://127.0.0.1:8000
"""

from __future__ import annotations

import argparse
import sys

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .agent import AgentResult, RecipeAgent
from .export import plan_markdown, recipe_markdown, write_markdown
from .models import Preferences, Recipe
from .shopping import shopping_list, shopping_list_text
from .storage import Store

console = Console()


def _split(text: str) -> list[str]:
    return [t.strip() for t in text.split(",") if t.strip()]


def show_recipe(recipe: Recipe, recommended: bool = False, recipe_id: int | None = None) -> None:
    n = recipe.nutrition_per_serving
    body = [
        f"[dim]{recipe.cuisine} · {recipe.difficulty} · prep {recipe.prep_minutes}m + cook {recipe.cook_minutes}m "
        f"· serves {recipe.servings}[/dim]",
        "",
        "[bold]Ingredients[/bold]",
        *[f"  • {i.label()}" for i in recipe.ingredients],
    ]
    if recipe.missing_ingredients:
        body += ["", "[bold yellow]To buy[/bold yellow]", *[f"  + {i.label()}" for i in recipe.missing_ingredients]]
    body += ["", "[bold]Steps[/bold]", *[f"  {k}. {s}" for k, s in enumerate(recipe.instructions, 1)]]
    body += [
        "",
        f"[bold]Nutrition/serving[/bold]  {n.calories} kcal · P {n.protein_g:g}g · C {n.carbs_g:g}g · F {n.fat_g:g}g",
    ]
    if recipe.substitutions:
        body += ["", "[bold]Swaps[/bold]  " + "; ".join(recipe.substitutions)]
    if recipe.tips:
        body += ["", f"[italic]💡 {recipe.tips}[/italic]"]
    title = f"{'⭐ ' if recommended else ''}{recipe.name}" + (f"  [dim]#{recipe_id}[/dim]" if recipe_id else "")
    console.print(Panel("\n".join(body), title=title, title_align="left", border_style="green" if recommended else "blue"))


def _report(result: AgentResult) -> None:
    if result.corrections:
        console.print(
            f"[yellow]🛡  Safety check caught {len(result.corrections)} issue(s); "
            f"agent self-corrected in {result.attempts} attempt(s).[/yellow]"
        )
    for p in result.unresolved:
        console.print(f"[red]Removed: {p}[/red]")


def _prefs(args) -> Preferences:
    return Preferences(
        diet=args.diet,
        allergies=_split(args.allergies),
        cuisine=args.cuisine,
        max_minutes=args.time,
        servings=args.servings,
        skill=args.skill,
    )


def _ingredients(args, store: Store) -> list[str]:
    items = _split(args.ingredients or "")
    if args.use_pantry:
        items += [p for p in store.pantry_list() if p not in items]
    return items


def cmd_suggest(args, store: Store) -> None:
    ingredients = _ingredients(args, store)
    prefs = _prefs(args)
    agent = RecipeAgent(model=args.model, demo=args.demo)
    if agent.demo:
        console.print("[dim]Demo mode (no OPENAI_API_KEY) - recipes are placeholders.[/dim]")

    extra = ""
    liked = store.favourite_cuisines()
    if liked and not prefs.cuisine:
        extra = f"The user has rated these cuisines highly before: {', '.join(liked)}. Lean towards them for at least one recipe."

    with console.status(f"Cooking up ideas with {', '.join(ingredients) or 'pantry staples'}..."):
        result = agent.suggest(ingredients, prefs, count=args.count, extra=extra)
    _report(result)
    store.log_search(ingredients, prefs, result.recipes)

    for r in result.recipes:
        rid = store.save_recipe(r) if args.save else None
        show_recipe(r, recommended=r.name == result.recommended, recipe_id=rid)
        if args.export:
            console.print(f"[dim]Exported → {write_markdown(recipe_markdown(r), args.export, r.name)}[/dim]")

    items = shopping_list(result.recipes, store.pantry_list())
    if items:
        console.print(Panel(shopping_list_text(items), title="🛒 Shopping list (all recipes)", title_align="left"))


def cmd_plan(args, store: Store) -> None:
    ingredients = _ingredients(args, store)
    prefs = _prefs(args)
    agent = RecipeAgent(model=args.model, demo=args.demo)
    with console.status(f"Planning {args.days} days of dinners..."):
        plan, result = agent.plan_week(ingredients, prefs, args.days)
    _report(result)

    table = Table(title="🗓  Meal plan")
    for col in ("Day", "Recipe", "Cuisine", "Time", "kcal"):
        table.add_column(col)
    for d in plan.days:
        r = d.recipe
        table.add_row(d.day, r.name, r.cuisine, f"{r.total_minutes}m", str(r.nutrition_per_serving.calories))
    console.print(table)

    pantry = store.pantry_list()
    console.print(Panel(shopping_list_text(shopping_list([d.recipe for d in plan.days], pantry)), title="🛒 Weekly shopping list"))
    if args.export:
        path = write_markdown(plan_markdown(plan, pantry), args.export, "meal-plan")
        console.print(f"[green]Full plan exported → {path}[/green]")
    if args.save:
        for d in plan.days:
            store.save_recipe(d.recipe)
        console.print(f"[green]Saved {len(plan.days)} recipes to your cookbook.[/green]")


def cmd_pantry(args, store: Store) -> None:
    if args.action == "add":
        added = store.pantry_add(_split(",".join(args.items)))
        console.print(f"[green]Added: {', '.join(added)}[/green]")
    elif args.action == "remove":
        store.pantry_remove(_split(",".join(args.items)))
        console.print("[green]Removed.[/green]")
    elif args.action == "clear":
        store.pantry_clear()
        console.print("[green]Pantry cleared.[/green]")
    items = store.pantry_list()
    console.print(Panel(", ".join(items) if items else "[dim]empty[/dim]", title=f"🥫 Pantry ({len(items)})"))


def cmd_cookbook(args, store: Store) -> None:
    if args.action == "list":
        rows = store.list_recipes(args.search or "")
        table = Table(title="📖 Cookbook")
        for col in ("#", "Recipe", "Cuisine", "Time", "Rating", "Saved"):
            table.add_column(col)
        for row in rows:
            r = row["recipe"]
            stars = "★" * (row["rating"] or 0) + "☆" * (5 - (row["rating"] or 0))
            table.add_row(str(row["id"]), r.name, r.cuisine, f"{r.total_minutes}m", stars, row["saved_at"][:10])
        console.print(table if rows else "[dim]Cookbook is empty. Use `suggest --save` to add recipes.[/dim]")
        return

    recipe = store.get_recipe(args.id)
    if recipe is None:
        console.print(f"[red]No recipe #{args.id}[/red]")
        sys.exit(1)
    if args.action == "show":
        if args.servings:
            recipe = recipe.scaled(args.servings)
        show_recipe(recipe, recipe_id=args.id)
        if args.export:
            console.print(f"[dim]Exported → {write_markdown(recipe_markdown(recipe), args.export, recipe.name)}[/dim]")
    elif args.action == "rate":
        store.rate_recipe(args.id, args.rating, args.notes)
        console.print(f"[green]Rated '{recipe.name}' {args.rating}/5.[/green]")
    elif args.action == "delete":
        store.delete_recipe(args.id)
        console.print(f"[green]Deleted '{recipe.name}'.[/green]")


def cmd_shop(args, store: Store) -> None:
    recipes = [r for r in (store.get_recipe(i) for i in args.ids) if r]
    if not recipes:
        console.print("[red]None of those recipe ids exist.[/red]")
        sys.exit(1)
    items = shopping_list(recipes, store.pantry_list())
    console.print(Panel(shopping_list_text(items), title=f"🛒 Shopping list for {len(recipes)} recipe(s)"))


def cmd_history(args, store: Store) -> None:
    table = Table(title="🕘 Recent searches")
    for col in ("When", "Ingredients", "Got"):
        table.add_column(col)
    for h in store.history(args.limit):
        table.add_row(h["created_at"].replace("T", " "), ", ".join(h["ingredients"]), "; ".join(h["results"]))
    console.print(table)


def cmd_serve(args, store: Store) -> None:
    import uvicorn

    console.print(f"[bold green]SafePlate[/bold green] running at [link]http://{args.host}:{args.port}[/link]")
    uvicorn.run("safeplate.server:app", host=args.host, port=args.port, log_level="warning")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="safeplate", description="AI recipe assistant with pantry, cookbook and meal planning")
    sub = p.add_subparsers(dest="command", required=True)

    def add_prefs(sp):
        sp.add_argument("-i", "--ingredients", default="", help="Comma-separated ingredients")
        sp.add_argument("--use-pantry", action="store_true", help="Include everything in your saved pantry")
        sp.add_argument("--diet", default="", help="vegan, vegetarian, pescatarian, keto, gluten-free, dairy-free...")
        sp.add_argument("--allergies", default="", help="Comma-separated, e.g. nuts,dairy,shellfish")
        sp.add_argument("--cuisine", default="", help="Preferred cuisine")
        sp.add_argument("--time", type=int, default=0, help="Max total minutes (prep + cook)")
        sp.add_argument("--servings", type=int, default=2)
        sp.add_argument("--skill", default="", choices=["", "beginner", "intermediate", "advanced"])
        sp.add_argument("--model", default=None, help="OpenAI model (default gpt-4o-mini or $SAFEPLATE_MODEL)")
        sp.add_argument("--demo", action="store_true", help="Run offline with placeholder recipes")
        sp.add_argument("--save", action="store_true", help="Save results to your cookbook")
        sp.add_argument("--export", metavar="DIR", help="Write Markdown files to DIR")

    s = sub.add_parser("suggest", help="Suggest recipes from ingredients")
    add_prefs(s)
    s.add_argument("-n", "--count", type=int, default=3, help="Number of recipes")
    s.set_defaults(func=cmd_suggest)

    s = sub.add_parser("plan", help="Generate a multi-day meal plan with a combined shopping list")
    add_prefs(s)
    s.add_argument("--days", type=int, default=5, help="1-7")
    s.set_defaults(func=cmd_plan)

    s = sub.add_parser("pantry", help="Manage ingredients you keep at home")
    s.add_argument("action", choices=["list", "add", "remove", "clear"], nargs="?", default="list")
    s.add_argument("items", nargs="*")
    s.set_defaults(func=cmd_pantry)

    cb = sub.add_parser("cookbook", help="Browse, scale, rate and delete saved recipes")
    cbs = cb.add_subparsers(dest="action", required=True)
    x = cbs.add_parser("list")
    x.add_argument("--search", default="")
    x = cbs.add_parser("show")
    x.add_argument("id", type=int)
    x.add_argument("--servings", type=int, help="Scale to this many servings")
    x.add_argument("--export", metavar="DIR")
    x = cbs.add_parser("rate")
    x.add_argument("id", type=int)
    x.add_argument("rating", type=int, choices=range(1, 6))
    x.add_argument("--notes")
    x = cbs.add_parser("delete")
    x.add_argument("id", type=int)
    cb.set_defaults(func=cmd_cookbook)

    s = sub.add_parser("shop", help="Shopping list for saved recipes")
    s.add_argument("ids", type=int, nargs="+")
    s.set_defaults(func=cmd_shop)

    s = sub.add_parser("history", help="Show recent searches")
    s.add_argument("--limit", type=int, default=15)
    s.set_defaults(func=cmd_history)

    s = sub.add_parser("serve", help="Launch the web app")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8000)
    s.set_defaults(func=cmd_serve)
    return p


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    args = build_parser().parse_args(argv)
    store = Store()
    try:
        args.func(args, store)
    finally:
        store.close()


if __name__ == "__main__":
    main()
