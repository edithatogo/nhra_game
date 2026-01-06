"""Automated screenshot capture for the NHRA dashboard."""

import time
from pathlib import Path

from playwright.sync_api import sync_playwright


def capture_screenshots() -> None:
    """Navigate the dashboard and capture screenshots of key tabs."""
    # Ensure screenshots directory exists
    output_dir = Path("screenshots")
    output_dir.mkdir(parents=True, exist_ok=True)

    url = "https://nhra-gt.streamlit.app"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        print(f"Navigating to {url}...")
        page.goto(url, timeout=60000)
        time.sleep(5)
        page.screenshot(path=output_dir / "dashboard_home.png")
        browser.close()


if __name__ == "__main__":
    capture_screenshots()
