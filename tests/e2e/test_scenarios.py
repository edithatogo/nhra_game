"""Tests for scenarios."""

import json

from playwright.sync_api import expect


def test_tab_navigation(dashboard):
    """Test navigation through all main tabs."""
    tabs = [
        dashboard.tab_theory,
        dashboard.tab_scenario,
        dashboard.tab_strategic,
        dashboard.tab_tree,
        dashboard.tab_data,
    ]

    for tab in tabs:
        dashboard.navigate_to_tab(tab)
        expect(tab).to_have_attribute("aria-selected", "true")


def test_expert_mode_interaction(dashboard):
    """Test enabling expert mode and interacting with overrides."""
    # Navigate to scenario tab where expert mode lives
    dashboard.navigate_to_tab(dashboard.tab_scenario)

    # Toggle Expert Mode
    dashboard.expert_checkbox.click()
    expect(dashboard.page.get_by_text("Strategy Overrides", exact=True)).to_be_visible()
    dashboard.check_for_errors()


def test_simulation_trigger(dashboard):
    """Changing the scenario applies its simulation inputs and renders results."""
    dashboard.navigate_to_tab(dashboard.tab_scenario)
    dashboard.scenario_picker.click()
    dashboard.page.get_by_role("option", name="Fiscal Cliff 2026").click()
    expect(dashboard.funding_share).to_have_value("0.38")
    expect(dashboard.page.get_by_text("Resilience", exact=True)).to_be_visible()
    dashboard.check_for_errors()


def test_download_functionality(dashboard):
    """Test that the download button triggers a download event."""
    # Locate the sidebar download button
    download_btn = dashboard.page.get_by_role("button", name="📥 Download Snapshot (JSON)")

    # Ensure it's visible (sidebar usually open)
    expect(download_btn).to_be_visible()

    # Trigger download and wait for event
    with dashboard.page.expect_download() as download_info:
        download_btn.click()

    download = download_info.value
    assert download.suggested_filename.endswith(".json")
    snapshot = json.loads(download.path().read_text(encoding="utf-8"))
    assert snapshot["scenario_name"] == "Manual / Custom"
    assert snapshot["params"]["nominal_cth_share_target"] == float(
        dashboard.funding_share.input_value()
    )


def test_forensic_audit_load(dashboard):
    """Test loading the 'Forensic Audit' sub-tab to ensure no crashes due to missing columns."""
    dashboard.navigate_to_tab(dashboard.tab_forensic)
    expect(dashboard.page.get_by_text("Forensic Audit & Solver Integrity")).to_be_visible()
    dashboard.check_for_errors()
