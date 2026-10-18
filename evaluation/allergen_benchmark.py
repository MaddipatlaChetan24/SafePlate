"""Held-out benchmark for the allergen / diet matcher in recipe_agent/safety.py.

The cases below were written AFTER safety.py was finished and were not used to
tune it — the rules were frozen before this file was run for the first time.
(The 12 cases in tests/test_core.py are the "dev set" the rules were written
against.) Failures are reported as found, not patched to make the table look
better.

Three matchers are compared using the exact same keyword lists:
  naive      plain substring match               ("nut" in "coconut" -> True)
  boundary   match only at a word start          (regex \\bkeyword)
  full       word-boundary + phrase rewrites     (what the app actually ships)

Run:  python -m evaluation.allergen_benchmark
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

from recipe_agent import safety

# (ingredient, kind, value, should_flag, note)
CASES: list[tuple[str, str, str, bool, str]] = [
    # --- nuts
    ("cashews", "allergy", "nuts", True, ""),
    ("walnut halves", "allergy", "nuts", True, ""),
    ("pine nuts", "allergy", "nuts", True, ""),
    ("hazelnut spread", "allergy", "nuts", True, ""),
    ("pistachios", "allergy", "nuts", True, ""),
    ("almond milk", "allergy", "nuts", True, "plant milk still a nut"),
    ("peanut butter", "allergy", "nuts", True, ""),
    ("pesto", "allergy", "nuts", True, "hidden: pesto contains pine nuts"),
    ("coconut flakes", "allergy", "nuts", False, "coconut is not a tree nut here"),
    ("coconut milk", "allergy", "nuts", False, ""),
    ("nutmeg", "allergy", "nuts", False, ""),
    ("butternut squash", "allergy", "nuts", False, ""),
    ("doughnut", "allergy", "nuts", False, ""),
    ("chestnut mushrooms", "allergy", "nuts", False, "a mushroom variety"),
    ("water chestnuts", "allergy", "nuts", False, "an aquatic vegetable"),
    ("nutritional yeast", "allergy", "nuts", False, ""),
    # --- dairy
    ("butter", "allergy", "dairy", True, ""),
    ("buttermilk", "allergy", "dairy", True, ""),
    ("ghee", "allergy", "dairy", True, ""),
    ("greek yogurt", "allergy", "dairy", True, ""),
    ("milk chocolate", "allergy", "dairy", True, ""),
    ("cheddar", "allergy", "dairy", True, "specific cheese name"),
    ("ricotta", "allergy", "dairy", True, "specific cheese name"),
    ("coconut cream", "allergy", "dairy", False, ""),
    ("cream of tartar", "allergy", "dairy", False, ""),
    ("oat milk", "allergy", "dairy", False, ""),
    ("vegan butter", "allergy", "dairy", False, ""),
    ("peanut butter", "allergy", "dairy", False, ""),
    ("cocoa butter", "allergy", "dairy", False, "plant fat"),
    # --- egg
    ("eggs", "allergy", "egg", True, ""),
    ("egg noodles", "allergy", "egg", True, ""),
    ("mayonnaise", "allergy", "egg", True, ""),
    ("eggplant", "allergy", "egg", False, ""),
    ("aubergine", "allergy", "egg", False, ""),
    # --- gluten
    ("plain flour", "allergy", "gluten", True, ""),
    ("soy sauce", "allergy", "gluten", True, "contains wheat"),
    ("breadcrumbs", "allergy", "gluten", True, ""),
    ("pasta", "allergy", "gluten", True, ""),
    ("cornbread", "allergy", "gluten", True, "usually wheat flour"),
    ("rice flour", "allergy", "gluten", False, ""),
    ("tamari", "allergy", "gluten", False, "wheat-free soy sauce"),
    ("rice noodles", "allergy", "gluten", False, ""),
    ("gluten-free pasta", "allergy", "gluten", False, ""),
    ("buckwheat", "allergy", "gluten", False, "not wheat despite the name"),
    # --- shellfish / fish
    ("shrimp", "allergy", "shellfish", True, ""),
    ("king prawns", "allergy", "shellfish", True, ""),
    ("crab sticks", "allergy", "shellfish", True, ""),
    ("fish sauce", "allergy", "shellfish", False, ""),
    ("anchovies", "allergy", "fish", True, ""),
    ("fish sauce", "allergy", "fish", True, ""),
    ("catfish fillets", "allergy", "fish", True, ""),
    ("worcestershire sauce", "allergy", "fish", True, "hidden: contains anchovy"),
    ("fishcake mix", "allergy", "fish", True, ""),
    # --- vegetarian
    ("chicken stock", "diet", "vegetarian", True, ""),
    ("ham hock", "diet", "vegetarian", True, ""),
    ("beef mince", "diet", "vegetarian", True, ""),
    ("bacon bits", "diet", "vegetarian", True, ""),
    ("gelatin", "diet", "vegetarian", True, "animal-derived"),
    ("champignons", "diet", "vegetarian", False, ""),
    ("graham crackers", "diet", "vegetarian", False, ""),
    ("vegetable stock", "diet", "vegetarian", False, ""),
    ("shallots", "diet", "vegetarian", False, ""),
    # --- vegan
    ("honey", "diet", "vegan", True, ""),
    ("parmesan", "diet", "vegan", True, ""),
    ("ghee", "diet", "vegan", True, ""),
    ("eggplant", "diet", "vegan", False, ""),
    ("coconut milk", "diet", "vegan", False, ""),
    ("nutritional yeast", "diet", "vegan", False, ""),
    ("almond milk", "diet", "vegan", False, ""),
    ("vegan cheese", "diet", "vegan", False, ""),
]


def keywords_for(kind: str, value: str) -> list[str]:
    if kind == "allergy":
        return safety.ALLERGEN_KEYWORDS.get(value, [value])
    return safety.DIET_RULES[value]


def naive(name: str, kws: list[str]) -> bool:
    return any(k in name.lower() for k in kws)


def boundary(name: str, kws: list[str]) -> bool:
    return any(re.search(rf"\b{re.escape(k)}", name.lower()) for k in kws)


def full(name: str, kws: list[str]) -> bool:
    return safety._contains(name, kws) is not None


MATCHERS = {"naive": naive, "boundary": boundary, "full": full}


def score(preds: list[bool], truth: list[bool]) -> dict:
    tp = sum(p and t for p, t in zip(preds, truth))
    fp = sum(p and not t for p, t in zip(preds, truth))
    fn = sum(t and not p for p, t in zip(preds, truth))
    tn = sum(not p and not t for p, t in zip(preds, truth))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "accuracy": (tp + tn) / len(truth),
            "precision": precision, "recall": recall, "f1": f1}


def main(out_dir: Path = Path("results")) -> dict:
    out_dir.mkdir(exist_ok=True)
    truth = [c[3] for c in CASES]
    summary, rows = {}, []
    for mname, fn in MATCHERS.items():
        preds = [fn(ing, keywords_for(kind, val)) for ing, kind, val, *_ in CASES]
        summary[mname] = score(preds, truth)
        for (ing, kind, val, expected, note), p in zip(CASES, preds):
            rows.append({"matcher": mname, "ingredient": ing, "constraint": f"{kind}:{val}",
                         "expected": expected, "predicted": p, "correct": p == expected, "note": note})

    with open(out_dir / "allergen_benchmark_cases.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    with open(out_dir / "allergen_benchmark_summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["matcher", "n", "accuracy", "precision", "recall", "f1", "false_positives", "false_negatives"])
        for m, s in summary.items():
            w.writerow([m, len(CASES), f"{s['accuracy']:.3f}", f"{s['precision']:.3f}", f"{s['recall']:.3f}",
                        f"{s['f1']:.3f}", s["fp"], s["fn"]])

    print(f"{len(CASES)} held-out cases ({sum(truth)} should flag, {len(truth) - sum(truth)} should pass)\n")
    print(f"{'matcher':<10}{'acc':>7}{'prec':>7}{'recall':>8}{'F1':>7}{'FP':>5}{'FN':>5}")
    for m, s in summary.items():
        print(f"{m:<10}{s['accuracy']:>7.3f}{s['precision']:>7.3f}{s['recall']:>8.3f}{s['f1']:>7.3f}{s['fp']:>5}{s['fn']:>5}")
    print("\nErrors made by the shipped ('full') matcher:")
    for r in rows:
        if r["matcher"] == "full" and not r["correct"]:
            kind = "MISSED" if r["expected"] else "FALSE ALARM"
            print(f"  {kind:<12}{r['ingredient']:<24}{r['constraint']:<20}{r['note']}")
    return summary


if __name__ == "__main__":
    main()
