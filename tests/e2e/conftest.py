import os
import subprocess
import time

import pytest
import requests
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def streamlit_app():
    """Start the Streamlit app for the test session and tear it down after."""
    # Define port and command
    port = 8503
    app_path = "scripts/dashboard.py"
    cmd = ["streamlit", "run", app_path, "--server.port", str(port), "--server.headless", "true"]

    # Start the process
    print(f"Starting Streamlit app on port {port}...")
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid,  # To ensure we can kill the whole group
    )

    # Wait for the app to be ready
    health_url = f"http://localhost:{port}/_stcore/health"
    timeout = 30
    start_time = time.time()

    app_ready = False
    while time.time() - start_time < timeout:
        try:
            response = requests.get(health_url, timeout=5)
            if response.text == "ok":
                app_ready = True
                break
        except requests.exceptions.ConnectionError:
            time.sleep(1)

    if not app_ready:
        os.killpg(os.getpgid(proc.pid), 15)
        # Capture output for debugging
        out, err = proc.communicate()
        print(f"\nStreamlit stdout:\n{out.decode()}")
        print(f"\nStreamlit stderr:\n{err.decode()}")
        pytest.fail(f"Streamlit app failed to start within {timeout} seconds.")

    yield f"http://localhost:{port}"

    # Teardown
    print("Stopping Streamlit app...")
    os.killpg(os.getpgid(proc.pid), 15)


@pytest.fixture
def dashboard(page: Page, streamlit_app):
    """Load the dashboard page and return the page object."""
    from tests.e2e.pom.dashboard_page import DashboardPage

    dashboard_page = DashboardPage(page, streamlit_app)
    dashboard_page.load()
    return dashboard_page
