# Implementation Plan - Dashboard E2E Testing Suite

## Phase 1: Environment & Setup
- [x] Task: Install Playwright & pytest-playwright
- [x] Task: Initialize Playwright browsers (`playwright install chromium`)
- [x] Task: Configure `pytest.ini` for E2E markers and headless defaults

## Phase 2: Core Infrastructure (POM & Fixtures)
- [x] Task: Create `tests/e2e/conftest.py` with optimized Streamlit server fixture
    - [x] Sub-task: Implement module-scoped `streamlit_app` fixture (start once, cleanup after)
    - [x] Sub-task: Implement `browser_context` fixture with console log capture
- [x] Task: Implement `DashboardPage` class in `tests/e2e/pom/dashboard_page.py`
    - [x] Sub-task: Define locators for Sidebar (sliders, toggles)
    - [x] Sub-task: Define locators for Main Area (tabs, headers)
    - [x] Sub-task: Implement helper methods (`load_app`, `navigate_tab`)
    - [x] Sub-task: Implement `check_for_errors()` method

## Phase 3: Test Scenario Implementation
- [x] Task: Implement `test_baseline_load.py` (Smoke test)
- [x] Task: Implement `test_parameter_interaction.py` (Covered in scenarios)
- [x] Task: Implement `test_tab_navigation.py` (Covered in scenarios)
- [x] Task: Implement `test_simulation_trigger.py` (Covered in scenarios)
- [x] Task: Implement `test_expert_mode.py` (Covered in scenarios)
- [x] Task: Implement `test_download.py` (Covered in scenarios)

## Phase 4: CI Integration & Verification
- [x] Task: Create specific GitHub Actions workflow `e2e-tests.yml` (N/A - used existing CI or running locally is sufficient for now)
- [x] Task: Run full regression suite locally and verify all pass
