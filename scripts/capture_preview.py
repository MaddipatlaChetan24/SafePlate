"""Regenerate docs/website_preview_{dark,light}.png (the README hero image).

Start a fresh demo server first, then run this script:
    SAFEPLATE_HOME=$(mktemp -d) OPENAI_API_KEY= python -m safeplate serve --port 8766
    python scripts/capture_preview.py docs

Requires: pip install playwright && playwright install chromium
"""
import sys
import time

import httpx
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8766"
OUT = sys.argv[1]

for _ in range(40):
    try:
        httpx.get(BASE + "/api/status"); break
    except Exception:
        time.sleep(0.25)

httpx.post(BASE + "/api/pantry", json={"items": ["rice", "onion", "olive oil", "soy sauce", "eggs", "chickpeas", "basmati rice", "spinach"]})
for ings, rating in [(["eggs", "mushrooms"], 5), (["chickpeas", "coconut milk"], 5), (["salmon"], 4), (["pasta"], 4)]:
    r = httpx.post(BASE + "/api/suggest", json={"ingredients": ings, "count": 1}).json()["recipes"][0]
    rid = httpx.post(BASE + "/api/cookbook", json=r).json()["id"]
    httpx.patch(f"{BASE}/api/cookbook/{rid}", json={"rating": rating})

with sync_playwright() as p:
    browser = p.chromium.launch()
    for theme in ["dark", "light"]:
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2, color_scheme=theme)
        page = ctx.new_page()
        page.add_init_script(f"try{{localStorage.setItem('sp-theme','{theme}')}}catch(e){{}}")
        page.goto(BASE)
        page.wait_for_selector(".status-card.demo, .status-card.live")
        for i in ["chicken", "garlic", "lemon", "rosemary", "potatoes", "tomatoes"]:
            page.fill("#ingredient-input", i)
            page.keyboard.press("Enter")
        page.select_option("#f-time", "60")
        page.click('[data-allergy="nuts"]')
        page.click('[data-allergy="shellfish"]')
        page.click("#f-count button:nth-child(3)")  # 6 recipes -> fuller grid
        page.click("#generate-btn")
        page.wait_for_selector(".rcard:not(.skeleton)")
        page.wait_for_timeout(1200)
        # Grow the viewport to the full page so the sticky 100vh sidebar spans the whole capture.
        height = page.evaluate("document.documentElement.scrollHeight")
        page.set_viewport_size({"width": 1440, "height": height})
        page.wait_for_timeout(400)
        page.screenshot(path=f"{OUT}/website_preview_{theme}.png")
        print(theme, height)
        ctx.close()
    browser.close()
