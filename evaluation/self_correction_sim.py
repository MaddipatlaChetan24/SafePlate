"""Fault-injection simulation of the generate -> verify -> self-correct loop.

This is a SIMULATION, not a measurement of a real LLM. A scripted "faulty
model" returns real recipes from the offline library, but with probability
`p_violate` slips an allergen into each recipe — the failure mode the loop
exists to catch. It lets us measure the loop's behaviour under controlled,
reproducible conditions (fixed seed) without paying for API calls, and
without the result depending on any one model's mood that day.

Two kinds of injected allergen:
  detectable  named directly ("cashews") — the rule checker can see it
  hidden      inside a compound ingredient ("pesto" -> pine nuts) — it can't

Assumptions (stated, not hidden):
  * When told about a flagged recipe, the model fixes it with prob `p_fix`.
  * The model never fixes violations it was not told about (hidden ones).
  * Retries do not introduce new violations.

Configurations compared:
  trust       return the model's first answer, no checking (single-call baseline)
  check       verify once, drop anything flagged, no retries   (max_retries=0)
  retry1/2    verify, feed violations back, retry up to 1 / 2 times, then drop

Run:  python -m evaluation.self_correction_sim
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

from safeplate.agent import RecipeAgent
from safeplate.models import Ingredient, Preferences, RecipeSet
from safeplate.samples import LIBRARY

DETECTABLE = ["cashews", "walnuts", "almonds", "pistachios"]
HIDDEN = ["pesto", "praline", "marzipan glaze", "satay dressing"]  # all contain nuts; none say "nut"
PREFS = Preferences(allergies=["nuts"])
NUT_FREE = [r for r in LIBRARY if "peanut" not in " ".join(i.name for i in r.ingredients)]


class FaultyModel(RecipeAgent):
    def __init__(self, rng: random.Random, p_violate: float, p_hidden: float, p_fix: float, max_retries: int):
        super().__init__(demo=True, max_retries=max_retries)
        self.rng, self.p_violate, self.p_hidden, self.p_fix = rng, p_violate, p_hidden, p_fix
        self.calls = 0
        self.injected: dict[str, str] = {}  # recipe name -> injected ingredient
        self.current: RecipeSet | None = None

    def _call(self, messages, ingredients, prefs, count):
        self.calls += 1
        if self.current is None:  # first draft
            recipes = []
            for base in self.rng.sample(NUT_FREE, count):
                r = base.model_copy(deep=True)
                if self.rng.random() < self.p_violate:
                    item = self.rng.choice(HIDDEN if self.rng.random() < self.p_hidden else DETECTABLE)
                    r.ingredients.append(Ingredient(name=item, quantity=30, unit="g"))
                    self.injected[r.name] = item
                recipes.append(r)
            self.current = RecipeSet(recipes=recipes, recommended=recipes[0].name)
            return self.current
        # Retry: fix only the recipes the agent complained about, with prob p_fix.
        feedback = messages[-1][1]
        fixed = []
        for r in self.current.recipes:
            item = self.injected.get(r.name)
            if item and f"'{r.name}'" in feedback and self.rng.random() < self.p_fix:
                r = r.model_copy(update={"ingredients": [i for i in r.ingredients if i.name != item]})
                del self.injected[r.name]
            fixed.append(r)
        self.current = RecipeSet(recipes=fixed, recommended=self.current.recommended)
        return self.current


def run_trial(rng, p_violate, p_hidden, p_fix, mode, count=3):
    if mode == "trust":
        agent = FaultyModel(rng, p_violate, p_hidden, p_fix, max_retries=0)
        draft = agent._call([], [], PREFS, count)
        shown, calls = draft.recipes, 1
    else:
        retries = {"check": 0, "retry1": 1, "retry2": 2}[mode]
        agent = FaultyModel(rng, p_violate, p_hidden, p_fix, max_retries=retries)
        shown = agent.suggest([], PREFS, count=count).recipes
        calls = agent.calls
    unsafe = sum(1 for r in shown if r.name in agent.injected)  # ground truth, not the checker's opinion
    return {"shown": len(shown), "unsafe": unsafe, "calls": calls, "requested": count}


def main(out_dir: Path = Path("results"), trials: int = 2000, seed: int = 7):
    out_dir.mkdir(exist_ok=True)
    rows = []
    for p_violate in (0.1, 0.3, 0.5):
        for mode in ("trust", "check", "retry1", "retry2"):
            rng = random.Random(seed)  # same random stream for every mode -> paired comparison
            agg = {"shown": 0, "unsafe": 0, "calls": 0, "requested": 0}
            for _ in range(trials):
                for k, v in run_trial(rng, p_violate, p_hidden=0.2, p_fix=0.8, mode=mode).items():
                    agg[k] += v
            rows.append({
                "p_violate": p_violate,
                "mode": mode,
                "unsafe_shown_pct": 100 * agg["unsafe"] / agg["shown"] if agg["shown"] else 0.0,
                "recipes_delivered_pct": 100 * agg["shown"] / agg["requested"],
                "llm_calls_per_request": agg["calls"] / trials,
            })

    with open(out_dir / "self_correction_sim.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.2f}" if isinstance(v, float) else v) for k, v in r.items()})

    print(f"{trials} requests x 3 recipes per cell, seed={seed}, p_hidden=0.2, p_fix=0.8\n")
    print(f"{'p_violate':>9}  {'mode':<7}{'unsafe shown':>13}{'delivered':>11}{'LLM calls':>11}")
    for r in rows:
        print(f"{r['p_violate']:>9}  {r['mode']:<7}{r['unsafe_shown_pct']:>12.2f}%{r['recipes_delivered_pct']:>10.1f}%{r['llm_calls_per_request']:>11.2f}")
    plot(rows, out_dir)
    return rows


def plot(rows, out_dir: Path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    modes = ["trust", "check", "retry1", "retry2"]
    labels = {"trust": "Trust LLM (no check)", "check": "Check + drop", "retry1": "Check + 1 retry", "retry2": "Check + 2 retries"}
    colors = {"trust": "#94a3b8", "check": "#f59e0b", "retry1": "#f97316", "retry2": "#e8552d"}
    ps = sorted({r["p_violate"] for r in rows})
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, metric, title in (
        (axes[0], "unsafe_shown_pct", "Unsafe recipes shown to user (%)"),
        (axes[1], "recipes_delivered_pct", "Recipes delivered (% of requested)"),
    ):
        width = 0.2
        for k, m in enumerate(modes):
            vals = [next(r[metric] for r in rows if r["mode"] == m and r["p_violate"] == p) for p in ps]
            ax.bar([i + (k - 1.5) * width for i in range(len(ps))], vals, width, label=labels[m], color=colors[m])
        ax.set_xticks(range(len(ps)), [f"{int(p * 100)}%" for p in ps])
        ax.set_xlabel("Model's per-recipe violation rate")
        ax.set_title(title, fontsize=11, loc="left")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.25)
    axes[0].legend(frameon=False, fontsize=9)
    fig.suptitle("Fault-injection simulation (seed 7, 2000 requests per cell)", fontsize=10, color="#475569", x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(out_dir / "self_correction_sim.png", dpi=160)


if __name__ == "__main__":
    main()
