from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("RECIPE_AGENT_HOME", str(tmp_path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    from recipe_agent.server import app

    return TestClient(app)


def test_index_and_status(client):
    assert "Recipe Agent" in client.get("/").text
    assert client.get("/api/status").json()["demo"] is True


def test_suggest_respects_allergies_and_reports_usage(client):
    body = {"ingredients": ["tofu", "broccoli", "garlic"], "preferences": {"diet": "vegan", "allergies": ["nuts"]}, "count": 3}
    data = client.post("/api/suggest", json=body).json()
    assert len(data["recipes"]) == 3
    assert data["recipes"][0]["name"] == data["recommended"]
    assert "Thai Peanut Noodle Salad" not in [r["name"] for r in data["recipes"]]
    assert data["recipes"][0]["uses"]  # tofu/broccoli/garlic matched
    assert client.get("/api/history").json()[0]["ingredients"] == ["tofu", "broccoli", "garlic"]


def test_pantry_is_included_and_cuts_shopping_list(client):
    client.post("/api/pantry", json={"items": ["scallions", "jasmine rice"]})
    data = client.post("/api/suggest", json={"ingredients": ["tofu"], "use_pantry": True, "count": 1}).json()
    assert "scallions" in data["ingredients"]
    assert not any("scallion" in i["name"] for i in data["shopping_list"])
    assert client.delete("/api/pantry/scallions").json() == ["jasmine rice"]


def test_cookbook_flow(client):
    recipe = client.post("/api/suggest", json={"ingredients": ["eggs"], "count": 1}).json()["recipes"][0]
    rid = client.post("/api/cookbook", json=recipe).json()["id"]
    assert client.patch(f"/api/cookbook/{rid}", json={"rating": 5}).json()["ok"]
    book = client.get("/api/cookbook").json()
    assert book["stats"]["count"] == 1 and book["stats"]["avg_rating"] == 5
    assert client.delete(f"/api/cookbook/{rid}").json()["ok"]
    assert client.delete(f"/api/cookbook/{rid}").status_code == 404


def test_scale_and_plan(client):
    recipe = client.post("/api/suggest", json={"ingredients": ["chickpeas"], "count": 1}).json()["recipes"][0]
    scaled = client.post("/api/scale", json={"recipe": recipe, "servings": 4}).json()
    assert scaled["servings"] == 4
    assert scaled["ingredients"][0]["quantity"] == recipe["ingredients"][0]["quantity"] * 2
    plan = client.post("/api/plan", json={"ingredients": ["spinach"], "days": 5}).json()
    assert [d["day"] for d in plan["days"]][:2] == ["Monday", "Tuesday"]
    assert plan["markdown"].startswith("# Meal Plan")
