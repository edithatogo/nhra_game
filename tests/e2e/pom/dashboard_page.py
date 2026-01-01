from playwright.sync_api import Page, expect


class DashboardPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

        # Locators - Sidebar
        self.sidebar_rural_weight = page.locator("div[data-testid='stSlider']").filter(
            has_text="Rurality Weight"
        )

        # Locators - Main Headers
        self.main_header = page.get_by_role("heading", level=1).filter(has_text="Analysis")

        # Locators - Tabs
        self.tab_theory = page.get_by_role("tab", name="📖 Theory & Background")
        self.tab_scenario = page.get_by_role("tab", name="📈 Scenario Analysis")
        self.tab_strategic = page.get_by_role("tab", name="🕸️ Strategic Map")
        self.tab_tree = page.get_by_role("tab", name="🌲 Game Tree Explorer")
        self.tab_data = page.get_by_role("tab", name="🧬 Data Lineage")

        # Locators - Actions
        self.boost_button = page.get_by_role("button", name="Boost to SOTA Accuracy")
        self.expert_checkbox = page.get_by_text("🧠 Expert Strategic Mode")

    def load(self):
        """Navigate to the app and wait for load."""
        self.page.goto(self.base_url)
        # Wait for the main title to ensure basic load
        expect(self.main_header).to_contain_text("NHRA Strategic Scenario", timeout=15000)
        self.check_for_errors()

    def check_for_errors(self):
        """Fail immediately if any Streamlit error is visible."""
        # Only catch actual exceptions (traceback), ignore st.info/st.warning bubbles for now
        # to avoid false positives like "Adjust inputs..."
        errors = self.page.locator("div[data-testid='stException']")
        if errors.count() > 0:
            error_text = errors.first.inner_text()
            raise AssertionError(f"Streamlit Error Detected: {error_text}")

    def navigate_to_tab(self, tab_locator):
        """Click a tab and wait for stability."""
        tab_locator.click()
        self.page.wait_for_timeout(500)  # Small UI settle
        self.check_for_errors()
