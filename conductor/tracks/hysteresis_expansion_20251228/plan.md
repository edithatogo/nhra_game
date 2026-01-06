# Track Plan: Hysteresis Analysis Expansion (P2)

**Goal:** Expand the system dynamics analysis by enhancing phase-space visualizations and implementing quantitative metrics for hysteresis (tipping points and recovery paths).

## CI-Relevant Commands

- `just lint`
- `just type`
- `just test`
- `just docs`

## Phase 1: Enhanced Visualization

- [x] Task: Update `plot_phase_space` in `interactive.py` to color the trajectory by `SystemMode`.
- [x] Task: Add markers for each year and distinct start/end symbols.
- [x] Task: Add arrowheads or direction markers to the phase-space line to indicate time flow.

## Phase 2: Analytical Metrics

- [x] Task: Implement a function to calculate the "Hysteresis Loop Area" as a measure of system lag/inertia.
- [x] Task: Implement "Time-to-Recovery" metrics (months spent in non-Normal modes).
- [x] Task: Integrate these metrics into the `summarise_outcome` function in `engine.py`.

## Phase 3: Dashboard Integration

- [x] Task: Add Resilience and Hysteresis metrics to the Executive Summary sidebar in the dashboard.
- [x] Task: Add a dedicated "System Dynamics & Hysteresis" section to the dashboard (Tab 5 extension or new Tab).

## Phase 4: Validation

- [x] Task: Create `tests/test_hysteresis.py` to verify metric calculations.

---
**Track Status:** COMPLETED 2025-12-28
System dynamics analysis expanded with qualitative (colored phase-space) and quantitative (loop area, resilience index) metrics. Dashboard updated with a dedicated analysis sub-tab.
