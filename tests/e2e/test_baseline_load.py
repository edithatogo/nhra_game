from playwright.sync_api import expect


def test_baseline_load(dashboard):
    """Test that the dashboard loads the main title and sidebar components
    without generating any implicit errors.
    """
    # Title verification
    try:
        expect(dashboard.main_header).to_contain_text("NHRA Strategic Simulator", timeout=15000)
    except Exception as e:
        print(f"Page Content: {dashboard.page.content()}")
        raise e

    # Sidebar verification
    expect(dashboard.sidebar_rural_weight).to_be_visible()

    # Check for implicit errors (redundant with fixture but good for clarity)
    dashboard.check_for_errors()
