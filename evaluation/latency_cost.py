"""Wall-clock and payload-size measurements for the classical (non-LLM) parts.

Everything here runs in demo mode, so it measures the app's own overhead —
safety checks, scaling, shopping-list merging, SQLite, HTTP — not model
latency, which depends entirely on the provider. LLM token counts are
ESTIMATES from payload size (~4 characters per token), not billed numbers.

Run:  python -m evaluation.latency_cost
"""

from __future__ import annotations

import csv
import os
import statistics
import tempfile
import time
from pathlib import Path

from safeplate.agent import SYSTEM_PROMPT
from safeplate.models import Preferences, RecipeSet
from safeplate.safety import check_recipe
from safeplate.samples import LIBRARY, match_library
from safeplate.shopping import shopping_list


def timeit(fn, n: int) -> tuple[float, float]:
    samples = []
    for _ in range(n):
        t = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - t) * 1000)
    samples.sort()
    return statistics.median(samples), samples[int(0.95 * (len(samples) - 1))]


def main(out_dir: Path = Path("results")):
    out_dir.mkdir(exist_ok=True)
    os.environ["SAFEPLATE_HOME"] = tempfile.mkdtemp()
    os.environ.pop("OPENAI_API_KEY", None)
    from fastapi.testclient import TestClient

    from safeplate.server import app

    client = TestClient(app)
    strict = Preferences(diet="vegan", allergies=["nuts", "dairy", "gluten", "egg", "shellfish", "fish", "soy", "sesame"], max_minutes=30)
    recipe = LIBRARY[1]
    body = {"ingredients": ["tofu", "broccoli", "garlic"], "preferences": {"allergies": ["nuts"]}, "count": 3}
    suggested = client.post("/api/suggest", json=body).json()["recipes"]

    rows = []
    def add(name, fn, n):
        p50, p95 = timeit(fn, n)
        rows.append({"operation": name, "runs": n, "p50_ms": p50, "p95_ms": p95})

    add("safety check, 1 recipe (all 9 allergens + vegan + time)", lambda: check_recipe(recipe, strict), 2000)
    add("scale recipe to 6 servings", lambda: recipe.scaled(6), 2000)
    week = match_library(["garlic"], Preferences(), 7)
    assert sum(len(r.missing_ingredients) for r in week) > 30  # real work, not an empty loop
    add("shopping list, 7 recipes merged", lambda: shopping_list(week, ["rice", "onion", "garlic"]), 500)
    add("HTTP POST /api/suggest (demo, 3 recipes)", lambda: client.post("/api/suggest", json=body), 100)
    add("HTTP POST /api/plan (demo, 7 days)", lambda: client.post("/api/plan", json={**body, "days": 7}), 50)
    add("HTTP POST /api/scale", lambda: client.post("/api/scale", json={"recipe": suggested[0], "servings": 4}), 200)
    add("HTTP GET /api/cookbook", lambda: client.get("/api/cookbook"), 200)

    sample = RecipeSet(recipes=LIBRARY[:3], recommended=LIBRARY[0].name).model_dump_json()
    user_msg = "Available ingredients: tofu, broccoli, garlic\n\nConstraints:\n" + strict.describe() + "\n\nSuggest exactly 3 distinct recipes."
    tokens = {
        "input_first_call": round((len(SYSTEM_PROMPT) + len(user_msg)) / 4),
        "output_per_call": round(len(sample) / 4),
        # A retry re-sends the conversation including the previous answer + feedback.
        "input_retry_call": round((len(SYSTEM_PROMPT) + len(user_msg) + len(sample) + 300) / 4),
    }

    with open(out_dir / "latency_cost.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        for r in rows:
            w.writerow({**r, "p50_ms": f"{r['p50_ms']:.3f}", "p95_ms": f"{r['p95_ms']:.3f}"})
        f.write("\n# estimated tokens (~4 chars/token)\n")
        for k, v in tokens.items():
            f.write(f"# {k},{v}\n")

    print(f"{'operation':<58}{'p50 ms':>9}{'p95 ms':>9}")
    for r in rows:
        print(f"{r['operation']:<58}{r['p50_ms']:>9.3f}{r['p95_ms']:>9.3f}")
    print("\nEstimated tokens:", tokens)


if __name__ == "__main__":
    main()
