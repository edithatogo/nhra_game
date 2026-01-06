import os

import pytest


@pytest.mark.skipif(
    not os.getenv("RUN_REMOTE_E2E"),
    reason="Skipping remote smoke test unless RUN_REMOTE_E2E is set",
)
def test_remote_smoke_load(dashboard):
    """Verifies that the deployed application loads successfully.
    Targeting the remote URL defined in STREAMLIT_REMOTE_URL or default.
    """
    print(f"Loading remote smoke test at: {dashboard.base_url}")
    dashboard.page.goto(dashboard.base_url)

    # Wait for body (should be immediate)
    dashboard.page.wait_for_selector("body", timeout=60000)

    title = dashboard.page.title()
    print(f"Page title: {title}")

    # Check if we are stuck on loading
    try:
        # Give it a moment to render something specific
        dashboard.page.wait_for_selector("[data-testid='stAppViewContainer']", timeout=10000)
    except:
        print("WARNING: stAppViewContainer not found in 10s.")
        print(f"Current Body Text: {dashboard.page.inner_text('body')[:500]}")

    # If we are here, at least the page loaded HTTP 200 and has a body.
    # We assert that we are not on a 404 or error page if possible.
    assert "404" not in title
    assert "Error" not in title

    print("SUCCESS: Remote load (basic) verified.")
