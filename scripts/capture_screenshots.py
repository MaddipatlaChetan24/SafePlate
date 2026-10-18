"""Regenerate every image used by the README and the LinkedIn post.

    SAFEPLATE_HOME=$(mktemp -d) OPENAI_API_KEY= python -m safeplate serve --port 8766 &
    SAFEPLATE_HOME=<same dir> python scripts/seed_demo.py
    python scripts/capture_screenshots.py

Requires: pip install playwright && playwright install chromium
Writes docs/website_preview_{dark,light}.png and docs/screenshots/*.png.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "docs" / "screenshots"


def run_discover(page, ingredients=("paneer", "spinach", "tomatoes", "onion"), allergies=("nuts",), count=None):
    page.click('[data-view="discover"]')
    for i in ingredients:
        page.fill("#ingredient-input", i)
        page.keyboard.press("Enter")
    for a in allergies:
        page.click(f'[data-allergy="{a}"]')
    if count:
        page.click(f'#f-count button:text-is("{count}")')
    page.click("#generate-btn")
    page.wait_for_selector(".rcard:not(.skeleton)")
    page.wait_for_timeout(1200)


def full_height(page, width):
    page.set_viewport_size({"width": width, "height": page.evaluate("document.documentElement.scrollHeight")})
    page.wait_for_timeout(400)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8766")
    base = ap.parse_args().base
    SHOTS.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch()

        def ctx(theme, w=1440, h=900, scale=2):
            c = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=scale)
            c.add_init_script(f"try{{localStorage.setItem('sp-theme','{theme}')}}catch(e){{}}")
            page = c.new_page()
            page.on("pageerror", lambda e: errors.append(str(e)))
            return c, page

        # README hero: full landing page with the live demo already run
        for theme in ("dark", "light"):
            c, page = ctx(theme)
            page.goto(base + "/?autorun=1")
            page.wait_for_selector(".res-row .art")
            page.wait_for_timeout(3500)  # hero animations settle
            full_height(page, 1440)
            page.screenshot(path=str(ROOT / "docs" / f"website_preview_{theme}.png"))
            c.close()

        # App screens
        for theme in ("light", "dark"):
            c, page = ctx(theme)
            page.goto(base + "/app")
            page.wait_for_selector(".kpi")
            page.wait_for_timeout(1400)
            page.screenshot(path=str(SHOTS / f"overview-{theme}.png"))
            run_discover(page)
            page.screenshot(path=str(SHOTS / f"discover-{theme}.png"))
            if theme == "light":
                page.click(".rcard[data-idx='0'] .rcard-title")
                page.wait_for_timeout(600)
                page.screenshot(path=str(SHOTS / "recipe-detail.png"))
                page.keyboard.press("Escape")
                page.keyboard.press("Meta+k")
                page.keyboard.type("dal")
                page.wait_for_timeout(300)
                page.screenshot(path=str(SHOTS / "command-palette.png"))
                page.keyboard.press("Escape")
                page.click('[data-view="planner"]')
                page.fill("#plan-ingredients", "spinach, paneer, tomatoes")
                page.click("#plan-btn")
                page.wait_for_selector(".day")
                page.wait_for_timeout(900)
                page.screenshot(path=str(SHOTS / "meal-planner.png"))
                page.click('[data-view="cookbook"]')
                page.wait_for_selector(".rcard .stars")
                page.wait_for_timeout(900)
                page.screenshot(path=str(SHOTS / "cookbook.png"))
            c.close()

        # Mobile
        c, page = ctx("light", 390, 844, 3)
        page.goto(base + "/app?view=discover")
        page.wait_for_selector("#ingredient-input")
        for i in ("chickpeas", "onion", "tomatoes"):
            page.fill("#ingredient-input", i)
            page.keyboard.press("Enter")
        page.click("#generate-btn")
        page.wait_for_selector(".rcard:not(.skeleton)")
        page.wait_for_timeout(900)
        page.evaluate("window.scrollTo(0, document.querySelector('#trace').offsetTop - 70)")
        page.wait_for_timeout(300)
        page.screenshot(path=str(SHOTS / "mobile.png"))
        c.close()

        # LinkedIn banner (1200x627): the landing hero itself, in banner mode
        c = browser.new_context(viewport={"width": 1200, "height": 627}, device_scale_factor=2)
        c.add_init_script("try{localStorage.setItem('sp-theme','light')}catch(e){}")
        page = c.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(base + "/?shot=banner")
        page.wait_for_timeout(4000)  # let the thali and story cards finish animating in
        page.screenshot(path=str(SHOTS / "linkedin-banner.png"))
        browser.close()

    print("errors:", errors or "none")


if __name__ == "__main__":
    main()
