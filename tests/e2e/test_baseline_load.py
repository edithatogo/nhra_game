"""Tests for baseline load."""

from playwright.sync_api import expect


def test_baseline_load(dashboard):
    """Check that the dashboard title and sidebar load without errors."""
    expect(dashboard.main_header).to_contain_text("NHRA Strategic Simulator", timeout=60000)
    expect(dashboard.sidebar_rural_weight).to_be_visible()
    dashboard.check_for_errors()
