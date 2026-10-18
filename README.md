<div align="center">

# 🍽️ SafePlate

Indian recipes from what's in your fridge, checked against your allergies and diet
by an AI that fixes its own mistakes.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688?style=flat-square&logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-structured_output-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-gpt--4o--mini-412991?style=flat-square&logo=openai&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-storage-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Tests](https://img.shields.io/badge/tests-40_passing-16a34a?style=flat-square&logo=pytest&logoColor=white)

<br/>

<img src="docs/screenshots/linkedin-banner.png" alt="SafePlate" width="100%">

</div>

## Features

- **Cook from your fridge**: Indian recipes ranked by how many of your ingredients they use
- **Allergy and diet safe**: 9 allergen groups, vegan/vegetarian/gluten-free and more, plus a time limit
- **Self-correcting AI**: if a recipe breaks a rule, the AI is told exactly why and fixes it
- **Meal planner**: 3–7 day plans across regions with one shopping list
- **Pantry, cookbook and history**: ratings shape future suggestions
- **Works offline**: 14 built-in Indian dishes when no API key is set

## How it works

```mermaid
flowchart LR
    A[Your ingredients] --> B[AI drafts recipes]
    B --> C{Safety check}
    C -->|pass| D[Verified recipes]
    C -->|fail| E[Tell the AI what's wrong]
    E -->|retry up to 2x| B
```

In testing, this loop shows **about 5× fewer unsafe recipes** than trusting the AI directly,
while still delivering **98%+** of requested recipes. Scripts in `evaluation/` reproduce every number.

## Quick start

```bash
git clone https://github.com/MaddipatlaChetan24/SafePlate.git
cd SafePlate
pip install -r requirements.txt
python -m safeplate serve        # open http://127.0.0.1:8000
```

Add `OPENAI_API_KEY` to a `.env` file for live AI recipes (see `.env.example`).

## Screenshots

<table>
  <tr>
    <td width="50%"><img src="docs/screenshots/discover-light.png" alt="Discover"><br><sub><b>Discover</b></sub></td>
    <td width="50%"><img src="docs/screenshots/recipe-detail.png" alt="Recipe"><br><sub><b>Recipe details</b></sub></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/meal-planner.png" alt="Meal planner"><br><sub><b>Meal planner</b></sub></td>
    <td><img src="docs/screenshots/overview-dark.png" alt="Dark mode"><br><sub><b>Dashboard (dark mode)</b></sub></td>
  </tr>
</table>

## Tech stack

Python · FastAPI · LangChain · OpenAI · Pydantic · SQLite · HTML/CSS/JavaScript · pytest · Docker

## Project structure

```
safeplate/     agent, safety checker, API, CLI, web app
evaluation/    benchmark and simulation scripts
tests/         40 tests
scripts/       screenshot tools
```

## Tests

```bash
python -m pytest -q
```

## License

MIT
