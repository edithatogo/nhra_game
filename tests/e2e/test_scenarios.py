from playwright.sync_api import expect


def test_tab_navigation(dashboard):
    """
    Test navigation through all main tabs.
    """
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
    """
    Test enabling expert mode and interacting with overrides.
    """
    # Navigate to scenario tab where expert mode lives
    dashboard.navigate_to_tab(dashboard.tab_scenario)

    # Toggle Expert Mode
    dashboard.expert_checkbox.click()
    dashboard.page.wait_for_timeout(500)
    dashboard.check_for_errors()

    # Verify Override headers appear (generic check for "Override")
    expect(dashboard.page.get_by_text("Overrides", exact=False).first).to_be_visible()


def test_simulation_trigger(dashboard):
    """
    Test triggering a simulation run.
    """
    dashboard.navigate_to_tab(dashboard.tab_scenario)

    # Click Boost
    if dashboard.boost_button.is_visible():
        dashboard.boost_button.click()
        # Wait for "Running" indicator or completion
        dashboard.page.wait_for_timeout(2000)
        dashboard.check_for_errors()


def test_download_functionality(dashboard):
    """
    Test that the download button triggers a download event.
    """
    # Locate the sidebar download button
    download_btn = dashboard.page.get_by_role("button", name="📥 Download Snapshot (JSON)")

    # Ensure it's visible (sidebar usually open)
    expect(download_btn).to_be_visible()

    # Trigger download and wait for event
    with dashboard.page.expect_download() as download_info:
        download_btn.click()

    download = download_info.value
    # Filename depends on scenario, but should verify extension
    assert ".json" in download.suggested_filename
