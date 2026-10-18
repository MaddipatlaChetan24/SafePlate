# 🍳 Recipe Agent

An AI cooking assistant that turns whatever is in your fridge into recipes, and **checks its own output** against your allergies, diet and time limit before showing you anything.

It also keeps a pantry, a rated cookbook, search history, multi-day meal plans and combined shopping lists. You can use it from the terminal (CLI) or the browser (Streamlit).

## Features

| Feature | What it does |
|---|---|
| **Self-correcting agent loop** | Each generated recipe is checked by rule-based safety checks for allergens, diet violations and time limits. If a check fails, the violations go back to the LLM so it can fix them. If it still fails after the retries, the unsafe recipes are removed instead of shown. |
| **Typed structured output** | Pydantic models + `with_structured_output`. The original version parsed JSON with regex; this one doesn't. |
| **Allergy & diet handling** | Nuts, peanut, dairy, gluten, egg, shellfish, fish, soy and sesame, plus vegan, vegetarian, pescatarian, gluten-free and dairy-free. Matches on word starts, so it knows that *coconut milk* isn't a nut or dairy, *eggplant* isn't egg, and *almond milk* is still a nut. |
| **Pantry** | Save what you always keep at home and add it to any search with `--use-pantry`. |
| **Cookbook** | Save recipes, rate them 1–5, add notes, search, delete. |
| **Personalisation** | Cuisines you rate 4★ or higher are given extra weight in later suggestions. |
| **Serving scaler** | Rescale any recipe's quantities (e.g. 2 → 6 servings). |
| **Meal planner** | 1–7 day dinner plan that mixes up cuisines and reuses perishables to cut food waste. |
| **Smart shopping list** | Combines missing ingredients across recipes, sums matching quantities, and skips pantry items and staples. |
| **Markdown export** | Export single recipes or full meal plans. |
| **Offline demo mode** | Runs with placeholder recipes when no API key is set, so you can try the app (and run the tests) for free. |
| **Tests** | 25 pytest tests covering scaling, safety rules, the retry loop, shopping-list merging and storage. |

## Architecture

```
            ┌──────────────┐     ┌──────────────┐
 CLI / Web ─▶  RecipeAgent  ├────▶  LLM (OpenAI) │  structured output → RecipeSet
            └──────┬───────┘     └──────────────┘
                   │  ▲ violations fed back (max 2 retries)
                   ▼  │
            ┌──────────────┐
            │ safety rules │  allergens · diet · time limit
            └──────┬───────┘
                   ▼
   shopping list · scaler · markdown export · SQLite (pantry, cookbook, history)
```

```
recipe_agent/
  agent.py     generate → verify → self-correct loop, meal planner, demo backend
  safety.py    deterministic allergen / diet / time checks
  models.py    Pydantic models (Recipe, Ingredient, Preferences, MealPlan)
  storage.py   SQLite: pantry, cookbook, ratings, history
  shopping.py  shopping-list merging
  export.py    Markdown export
  cli.py       rich terminal UI
app.py         Streamlit web UI
tests/         pytest suite
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env      # add your OPENAI_API_KEY (optional, demo mode works without it)
```

## Usage

### Web UI
```bash
streamlit run app.py
```

### CLI
```bash
# Suggestions
python -m recipe_agent suggest -i "chicken, garlic, lemon, rosemary"
python -m recipe_agent suggest -i "tofu, broccoli, ginger" --diet vegan --time 20 --allergies sesame
python -m recipe_agent suggest -i "pasta, tomatoes, basil" --servings 4 --save --export exports/

# Pantry
python -m recipe_agent pantry add rice onion "soy sauce" garlic
python -m recipe_agent suggest --use-pantry --cuisine Thai

# Meal plan + shopping list
python -m recipe_agent plan --days 5 --use-pantry --diet vegetarian --export exports/ --save

# Cookbook
python -m recipe_agent cookbook list
python -m recipe_agent cookbook show 3 --servings 6
python -m recipe_agent cookbook rate 3 5 --notes "add more chilli"
python -m recipe_agent shop 1 3 4          # combined shopping list for saved recipes
python -m recipe_agent history
```

Install it as a command with `pip install -e .`, then call `recipe-agent ...`.

### Configuration
| Variable | Default | |
|---|---|---|
| `OPENAI_API_KEY` | — | Turns on real LLM output. If it isn't set, the app runs in demo mode |
| `RECIPE_AGENT_MODEL` | `gpt-4o-mini` | Any OpenAI chat model |
| `RECIPE_AGENT_HOME` | `~/.recipe_agent` | Where the SQLite database lives |

## Tests
```bash
python -m pytest -q
```

## Acknowledgements

Started from the [Recipe Recommendation Agent](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/17-recipe-agent) by ashishpatel26 (MIT), a single-file script that prompts an LLM once and prints 3 recipes. This project rewrites and extends it with the self-correcting safety loop, typed output, persistence, meal planning, shopping lists, a web UI and tests.
