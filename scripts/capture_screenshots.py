import time
from pathlib import Path

from playwright.sync_api import sync_playwright


def capture_screenshots():
    # Ensure screenshots directory exists
    output_dir = Path("screenshots")
    output_dir.mkdir(exist_ok=True)

    url = "https://gameofnhra.streamlit.app/"

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        print(f"Navigating to {url}...")
        page.goto(url, timeout=60000)

        # Wait for the main app container to load
        # specific to Streamlit, usually checking for the main container or specific elements
        try:
            print("Waiting for app to load...")

            # Check for "Wake up" button
            try:
                wake_up_btn = page.get_by_role("button", name="Yes, get this app back up!")
                if wake_up_btn.is_visible(timeout=5000):
                    print("App is sleeping. Waking it up...")
                    wake_up_btn.click()
                    print("Clicked wake up button. Waiting for boot...")
                    page.wait_for_load_state("networkidle", timeout=120000)
            except Exception:
                pass

            # Wait for the main streamlit container
            # It's inside an iframe
            print("Waiting for iframe...")
            # Use FrameLocator
            frame = page.frame_locator("iframe[title='streamlitApp']")

            # Wait for app content inside iframe
            print("Waiting for app content inside iframe...")
            # We wait for the element *inside* the frame
            frame.locator("[data-testid='stAppViewContainer']").wait_for(timeout=120000)

            # Wait for some text content to stabilize
            time.sleep(10)  # content loading

            # Print page title for debug
            print(f"Page title: {page.title()}")
        except Exception as e:
            print(f"Error loading page: {e}")
            # Try to take a screenshot anyway to debug
            page.screenshot(path=output_dir / "error_loading.png")
            # Dump content
            with open(output_dir / "error_page.html", "w") as f:
                f.write(page.content())
            browser.close()
            return

        # List of tabs as identified in dashboard.py, cleaned of emojis for easier matching if needed,
        # but exact match is better if we can.
        # Streamlit tabs are usually buttons with role="tab"

        tabs_to_capture = [
            "Theory & Background",
            "Scenario Analysis",
            "Strategic Map",
            "Game Tree Explorer",
            "Intra-State LHN Variance",
            "Data Lineage",
            "Validation Scorecard",
            "Technical Analytics",
            "Evidence Manager",
            "Forensic Audit",
            "Game Theoretic Encyclopedia",
        ]

        # Locate all tab elements
        print("Locating tabs...")
        # Streamlit tabs often are within a specific container or just buttons with role="tab"
        # We can try to match by text content containing the tab name

        for i, tab_name in enumerate(tabs_to_capture):
            print(f"Processing tab: {tab_name}")
            try:
                # Find the tab button inside the frame
                # Streamlit tabs usually have the name inside.
                # The text selector works well with Playwright's lax matching

                # Check if tab is already identifying itself (sometimes they are just p elements in buttons)
                # We use a broad locator for the tab
                tab_locator = frame.get_by_text(tab_name, exact=True)

                # Sometimes tabs are "p" tags inside a div with specific class or role="tab"
                if tab_locator.count() == 0:
                    tab_locator = frame.get_by_role("tab", name=tab_name)

                # Check if it exists and is visible
                # Note: count() is synchronous
                # For frame locators, we can't easily count without waiting or using strict mode
                # So we just try to click likely candidates

                try:
                    tab_locator.first.click(timeout=2000)
                    time.sleep(5)

                    # Take screenshot
                    safe_name = tab_name.replace(" ", "_").replace("&", "and").lower()
                    screenshot_path = output_dir / f"{i:02d}_{safe_name}.png"
                    # Capture full page (main page, not just frame)
                    page.screenshot(path=screenshot_path, full_page=True)
                    print(f"Saved {screenshot_path}")
                    continue
                except:
                    pass

                print(f"⚠️ Could not click tab: {tab_name}")

            except Exception as e:
                print(f"Error processing tab {tab_name}: {e}")

        browser.close()
        print("Done!")


if __name__ == "__main__":
    capture_screenshots()
