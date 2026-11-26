"""Fixtures for launching and diagnosing dashboard tests."""

import logging
import os
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import pytest
import requests

from tests.e2e.pom.dashboard_page import DashboardPage

_HTTP_OK = 200

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
def streamlit_server():
    """Starts a local Streamlit server for the duration of the test session."""
    if os.getenv("STREAMLIT_REMOTE_URL"):
        yield os.getenv("STREAMLIT_REMOTE_URL")
        return

    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    logger.info("Starting local Streamlit server...")
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "streamlit_app.py",
            "--server.address",
            "127.0.0.1",
            "--server.headless",
            "true",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env={**os.environ, "STREAMLIT_SERVER_PORT": str(port)},
    )

    # Wait for server to be ready
    url = f"http://localhost:{port}"
    timeout = 30
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == _HTTP_OK:
                logger.info("Local Streamlit server ready.")
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    else:
        proc.terminate()
        message = "Local Streamlit server failed to start within 30 seconds."
        raise RuntimeError(message)

    yield url

    logger.info("Stopping local Streamlit server...")
    proc.terminate()
    proc.wait()


@pytest.fixture(scope="session")
def base_url(streamlit_server):
    """Return the base URL for testing (local or remote)."""
    return streamlit_server


@pytest.fixture
def page(page):
    """Extends playwright page fixture with error logging and screenshots."""
    # Set default timeout
    page.set_default_timeout(30000)

    return page

    # Optional: Logic to take screenshot on failure could go here if using a custom wrapper,
    # but pytest-playwright handles some of this. We will add custom error logging.


@pytest.fixture
def dashboard(page, base_url):
    """Fixture for DashboardPage POM."""
    return DashboardPage(page, base_url)


def pytest_exception_interact(node, call, report):
    """Save an end-to-end test failure with its captured output."""
    if report.failed:
        logger.error(f"Test failed: {node.name}")
        logger.error(f"Error details: {call.excinfo.value}")
        # Note: screenshots are handled by pytest-playwright --screenshot on-failure
