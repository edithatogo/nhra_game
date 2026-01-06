# Track Specification: Hysteresis Analysis Expansion (P2)

## 1. Overview

**Goal**: Expand the system dynamics analysis by enhancing phase-space visualizations and implementing quantitative metrics for hysteresis (tipping points and recovery paths).
**Context**: Derived from plan phases for hysteresis_expansion_20251228.
**Constraints**: None explicitly stated in plan.

## 2. Functional Requirements

- Update `plot_phase_space` in `interactive.py` to color the trajectory by `SystemMode`.
- Add markers for each year and distinct start/end symbols.
- Add arrowheads or direction markers to the phase-space line to indicate time flow.
- Implement a function to calculate the "Hysteresis Loop Area" as a measure of system lag/inertia.
- Implement "Time-to-Recovery" metrics (months spent in non-Normal modes).
- Integrate these metrics into the `summarise_outcome` function in `engine.py`.

## 3. Non-Functional Requirements

- Automated tests cover track changes.
- Validation checks pass for track changes.
- Verification steps are automated where possible.
- Dashboard updates reflect new outputs.
- CI checks are run and must pass.

## 4. Acceptance Criteria

- [ ] Update `plot_phase_space` in `interactive.py` to color the trajectory by `SystemMode`.
- [ ] Add markers for each year and distinct start/end symbols.
- [ ] Add arrowheads or direction markers to the phase-space line to indicate time flow.
- [ ] Implement a function to calculate the "Hysteresis Loop Area" as a measure of system lag/inertia.
- [ ] Relevant tests pass for track changes.
- [ ] Dashboard reflects the new outputs or views.

## Acceptance Checklist (Evaluation)

- [ ] Requirements and scope validated against this spec
- [ ] Acceptance criteria evaluated and recorded (pass/fail)
- [ ] CI green and key workflows verified
- [ ] Deployment/runtime checks complete (if applicable)
- [ ] Deviations or follow-ups documented
