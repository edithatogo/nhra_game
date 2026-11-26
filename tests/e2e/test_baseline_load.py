"""Tests for baseline load."""

from playwright.sync_api import expect


def test_baseline_load(dashboard):
    """Check that the dashboard title and sidebar load without errors."""
    # Title verification
    try:
        expect(dashboard.main_header).to_contain_text("NHRA Strategic Simulator", timeout=15000)
    except Exception:
        print(f"Page Content: {dashboard.page.content()}")
        raise

    # Sidebar verification
    expect(dashboard.sidebar_rural_weight).to_be_visible()

    # Check for implicit errors (redundant with fixture but good for clarity)
    dashboard.check_for_errors()
