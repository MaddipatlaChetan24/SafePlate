"""Local persistence: pantry, saved recipes (cookbook) and search history.

Everything lives in a single SQLite file under ~/.recipe_agent (override with
the RECIPE_AGENT_HOME environment variable).
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from .models import Preferences, Recipe

SCHEMA = """
CREATE TABLE IF NOT EXISTS pantry (
    name TEXT PRIMARY KEY,
    added_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    data TEXT NOT NULL,
    rating INTEGER,
    notes TEXT DEFAULT '',
    saved_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredients TEXT NOT NULL,
    preferences TEXT NOT NULL,
    results TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def default_path() -> Path:
    home = Path(os.getenv("RECIPE_AGENT_HOME", Path.home() / ".recipe_agent"))
    home.mkdir(parents=True, exist_ok=True)
    return home / "recipe_agent.db"


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


class Store:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else default_path()
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    def close(self) -> None:
        self.conn.close()

    # --- Pantry -----------------------------------------------------------

    def pantry_add(self, items: list[str]) -> list[str]:
        cleaned = [i.strip().lower() for i in items if i.strip()]
        with self.conn:
            self.conn.executemany(
                "INSERT OR IGNORE INTO pantry (name, added_at) VALUES (?, ?)", [(i, _now()) for i in cleaned]
            )
        return cleaned

    def pantry_remove(self, items: list[str]) -> int:
        with self.conn:
            cur = self.conn.executemany("DELETE FROM pantry WHERE name = ?", [(i.strip().lower(),) for i in items])
        return cur.rowcount

    def pantry_list(self) -> list[str]:
        return [r["name"] for r in self.conn.execute("SELECT name FROM pantry ORDER BY name")]

    def pantry_clear(self) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM pantry")

    # --- Cookbook ---------------------------------------------------------

    def save_recipe(self, recipe: Recipe) -> int:
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO recipes (name, data, saved_at) VALUES (?, ?, ?)",
                (recipe.name, recipe.model_dump_json(), _now()),
            )
        return cur.lastrowid

    def get_recipe(self, recipe_id: int) -> Recipe | None:
        row = self.conn.execute("SELECT data FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
        return Recipe.model_validate_json(row["data"]) if row else None

    def list_recipes(self, search: str = "") -> list[dict]:
        rows = self.conn.execute(
            "SELECT id, name, data, rating, notes, saved_at FROM recipes WHERE name LIKE ? ORDER BY id DESC",
            (f"%{search}%",),
        ).fetchall()
        out = []
        for r in rows:
            recipe = Recipe.model_validate_json(r["data"])
            out.append(
                {"id": r["id"], "recipe": recipe, "rating": r["rating"], "notes": r["notes"], "saved_at": r["saved_at"]}
            )
        return out

    def rate_recipe(self, recipe_id: int, rating: int, notes: str | None = None) -> bool:
        if not 1 <= rating <= 5:
            raise ValueError("rating must be between 1 and 5")
        with self.conn:
            if notes is None:
                cur = self.conn.execute("UPDATE recipes SET rating = ? WHERE id = ?", (rating, recipe_id))
            else:
                cur = self.conn.execute(
                    "UPDATE recipes SET rating = ?, notes = ? WHERE id = ?", (rating, notes, recipe_id)
                )
        return cur.rowcount > 0

    def delete_recipe(self, recipe_id: int) -> bool:
        with self.conn:
            cur = self.conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        return cur.rowcount > 0

    def favourite_cuisines(self, limit: int = 3) -> list[str]:
        """Cuisines from recipes rated 4+, most common first — used to personalise suggestions."""
        counts: dict[str, int] = {}
        for r in self.conn.execute("SELECT data FROM recipes WHERE rating >= 4"):
            cuisine = json.loads(r["data"]).get("cuisine", "")
            if cuisine:
                counts[cuisine] = counts.get(cuisine, 0) + 1
        return [c for c, _ in sorted(counts.items(), key=lambda kv: -kv[1])][:limit]

    # --- History ----------------------------------------------------------

    def log_search(self, ingredients: list[str], prefs: Preferences, recipes: list[Recipe]) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO history (ingredients, preferences, results, created_at) VALUES (?, ?, ?, ?)",
                (json.dumps(ingredients), prefs.model_dump_json(), json.dumps([r.name for r in recipes]), _now()),
            )

    def history(self, limit: int = 20) -> list[dict]:
        rows = self.conn.execute(
            "SELECT ingredients, results, created_at FROM history ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [
            {"ingredients": json.loads(r["ingredients"]), "results": json.loads(r["results"]), "created_at": r["created_at"]}
            for r in rows
        ]
