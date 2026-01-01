# Implementation Plan - Dashboard E2E Testing Suite

## Phase 1: Environment & Setup
- [ ] Task: Install Playwright & pytest-playwright
- [ ] Task: Initialize Playwright browsers (`playwright install chromium`)
- [ ] Task: Configure `pytest.ini` for E2E markers and headless defaults

## Phase 2: Core Infrastructure (POM & Fixtures)
- [ ] Task: Create `tests/e2e/conftest.py` with optimized Streamlit server fixture
    - [ ] Sub-task: Implement module-scoped `streamlit_app` fixture (start once, cleanup after)
    - [ ] Sub-task: Implement `browser_context` fixture with console log capture
- [ ] Task: Implement `DashboardPage` class in `tests/e2e/pom/dashboard_page.py`
    - [ ] Sub-task: Define locators for Sidebar (sliders, toggles)
    - [ ] Sub-task: Define locators for Main Area (tabs, headers)
    - [ ] Sub-task: Implement helper methods (`load_app`, `navigate_tab`)
    - [ ] Sub-task: Implement `check_for_errors()` method

## Phase 3: Test Scenario Implementation
- [ ] Task: Implement `test_baseline_load.py` (Smoke test)
- [ ] Task: Implement `test_parameter_interaction.py` (Sliders check)
- [ ] Task: Implement `test_tab_navigation.py` (Walk through all tabs)
- [ ] Task: Implement `test_simulation_trigger.py` (Boost button)
- [ ] Task: Implement `test_expert_mode.py` (Conflict detection logic)
- [ ] Task: Implement `test_download.py` (Event listening)

## Phase 4: CI Integration & Verification
- [ ] Task: Create specific GitHub Actions workflow `e2e-tests.yml`
- [ ] Task: Run full regression suite locally and verify all pass
