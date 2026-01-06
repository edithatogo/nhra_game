# Specification: Dashboard E2E Testing Suite

## 1. Overview

Implement a robust End-to-End (E2E) testing suite for the Streamlit dashboard using Playwright. This suite will verify the application's responsiveness, interactivity, and stability across typical user workflows, ensuring no regressions in the UI or simulation logic.

## 2. Functional Requirements

The E2E suite must automate the following scenarios:

1. **Baseline Verification:** Confirm the app loads successfully, displaying the correct title and sidebar elements without errors.
2. **Parameter Interaction:** Manipulate sidebar inputs (Slider: Rurality Weight, Slider: Cost Shifting) and assert that metric displays update accordingly.
3. **Navigation Validation:** Iterate through all application tabs (Theory, Scenario Analysis, Strategic Map, Game Tree, Data Lineage, etc.) and verify that unique content for each tab renders correctly.
4. **Simulation Execution:** Trigger the "Boost to SOTA Accuracy" (or equivalent) action and await the completion of the simulation run.
5. **Expert Mode:** Activate "Expert Strategic Mode" and toggle dropdown overrides, ensuring no UI crashes occur.
6. **Download Functionality:** Verify the existence and clickability of "Download Snapshot" and "Download Report" buttons (verifying the download event triggers).

## 3. Architecture & Design Patterns

- **Page Object Model (POM):** Encapsulate UI elements and interactions within a `DashboardPage` class to improve test maintainability and readability.
- **Implicit Error Detection:** Implement a global check that runs after interactions to detect any Streamlit error containers (e.g., `st.error` or tracebacks) and fail the test immediately if found.

## 4. Non-Functional Requirements

- **Performance:** Tests should complete within a reasonable timeframe (e.g., < 2 minutes for the full suite locally).
- **Headless Execution:** Tests must run in headless mode to support CI/CD integration.
- **Reliability:** Tests should handle the dynamic nature of Streamlit (re-runs) without flakiness (e.g., proper waits for elements).

## 5. Technical Stack

- **Framework:** Playwright (Python)
- **Runner:** Pytest

## 6. Out of Scope

- Validating the exact numerical correctness of the downloaded CSV/JSON files (content validation is a separate data integrity task).
- Testing on mobile viewports (desktop focus for this iteration).
- Visual regression testing (pixel comparison) for dynamic charts.

## Acceptance Checklist (Evaluation)

- [ ] Requirements and scope validated against this spec
- [ ] Acceptance criteria evaluated and recorded (pass/fail)
- [ ] CI green and key workflows verified
- [ ] Deployment/runtime checks complete (if applicable)
- [ ] Deviations or follow-ups documented
