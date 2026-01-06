import logging
import os
from datetime import datetime
from pathlib import Path

import pytest

# Setup centralized logging
log_dir = Path("logs/e2e")
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"e2e_errors_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)
logger = logging.getLogger("e2e")


@pytest.fixture(scope="session")
def base_url():
    """Return the remote URL for testing."""
    return os.getenv("STREAMLIT_REMOTE_URL", "https://gameofnhra.streamlit.app/")


@pytest.fixture(scope="function")
def page(page, base_url):
    """Extends playwright page fixture with error logging and screenshots."""
    # Set default timeout
    page.set_default_timeout(30000)

    return page

    # Optional: Logic to take screenshot on failure could go here if using a custom wrapper,
    # but pytest-playwright handles some of this. We will add custom error logging.


@pytest.fixture(scope="function")
def dashboard(page, base_url):
    """Fixture for DashboardPage POM."""
    from tests.e2e.pom.dashboard_page import DashboardPage

    return DashboardPage(page, base_url)


def pytest_exception_interact(node, call, report):
    if report.failed:
        logger.error(f"Test failed: {node.name}")
        logger.error(f"Error details: {call.excinfo.value}")
        # Note: screenshots are handled by pytest-playwright --screenshot on-failure
