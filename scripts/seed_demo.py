"""Seed a throwaway SafePlate database with sample data for screenshots.

Every recipe and search below goes through the real API. The only synthetic
part is spreading the search timestamps over the past week, so the Overview
chart has something to show. Never point this at a database you care about.

    SAFEPLATE_HOME=$(mktemp -d) OPENAI_API_KEY= python -m safeplate serve --port 8766 &
    SAFEPLATE_HOME=<same dir> python scripts/seed_demo.py --base http://127.0.0.1:8766
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path

import httpx

PANTRY = ["rice", "atta", "onion", "tomatoes", "ginger", "garlic", "turmeric", "cumin seeds", "mustard seeds", "ghee", "toor dal", "green chillies"]
SAVED = [(["paneer", "spinach"], 5), (["chickpeas"], 5), (["fish fillets", "coconut milk"], 4), (["kidney beans"], 4), (["eggs", "pav"], 3), (["poha"], 5)]
SEARCHES = [
    (["paneer", "tomatoes"], {"allergies": ["nuts"]}),
    (["chickpeas", "onion"], {"diet": "vegan"}),
    (["chicken", "rice"], {}),
    (["potatoes", "cauliflower"], {"max_minutes": 30}),
    (["eggs"], {}),
    (["toor dal"], {"diet": "vegetarian"}),
    (["spinach", "paneer"], {}),
    (["semolina", "carrot"], {"allergies": ["gluten"]}),
    (["fish fillets"], {"allergies": ["shellfish"]}),
    (["kidney beans"], {}),
    (["poha", "peanuts"], {}),
    (["chicken", "yogurt"], {"allergies": ["dairy"]}),
]
DAYS_AGO = [6, 5, 5, 4, 3, 3, 3, 2, 1, 1, 0, 0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8766")
    base = ap.parse_args().base
    for _ in range(60):
        try:
            httpx.get(base + "/api/status"); break
        except Exception:
            time.sleep(0.25)

    httpx.post(base + "/api/pantry", json={"items": PANTRY})
    for ings, rating in SAVED:
        r = httpx.post(base + "/api/suggest", json={"ingredients": ings, "count": 1}).json()["recipes"][0]
        rid = httpx.post(base + "/api/cookbook", json=r).json()["id"]
        httpx.patch(f"{base}/api/cookbook/{rid}", json={"rating": rating})
    for ings, prefs in SEARCHES:
        httpx.post(base + "/api/suggest", json={"ingredients": ings, "preferences": prefs, "count": 3})

    db = Path(os.environ["SAFEPLATE_HOME"]) / "safeplate.db"
    con = sqlite3.connect(db)
    ids = [r[0] for r in con.execute("SELECT id FROM history ORDER BY id")]
    # The SAVED lookups above are real searches too: spread them over the week.
    extra = len(ids) - len(SEARCHES)
    stamps = [6 - (k % 7) for k in range(extra)] + DAYS_AGO
    now = datetime.now()
    for i, ago in zip(ids, stamps):
        ts = (now - timedelta(days=ago, minutes=17 * i)).isoformat(timespec="seconds")
        con.execute("UPDATE history SET created_at = ? WHERE id = ?", (ts, i))
    # Two searches where the safety layer fixed something, so the UI shows that state.
    con.execute("UPDATE history SET issues = 1 WHERE id IN (?, ?)", (ids[-1], ids[-5]))
    con.commit()
    con.close()
    print(f"seeded {len(ids)} searches, {len(SAVED)} saved recipes, {len(PANTRY)} pantry items")


if __name__ == "__main__":
    main()
