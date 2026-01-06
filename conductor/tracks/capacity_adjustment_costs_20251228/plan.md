# Implementation Plan: Capacity Adjustment Costs & Friction

## CI-Relevant Commands

- `just lint`
- `just type`
- `just test`
- `just docs`

## Phase 1: Engine Physics

- [x] Task: Update `ParamsJax` with `expansion_lag`, `contraction_lag`, and `adjustment_cost_beta`.
- [x] Task: Update `lhn_step_jax` to use asymmetric lag logic.
- [x] Task: Implement `calculate_adjustment_costs` in `src/nhra_gt/engine_jax.py`.

## Phase 2: Agent Logic & Utility

- [x] Task: Update `AgentWeights` in `src/nhra_gt/agent_logic.py` with `capacity_inertia_weight`.
- [x] Task: Update `lhn_utility` to penalize large $\Delta TargetCapacity$.

## Phase 3: Dashboard & Parity

- [x] Task: Expose adjustment costs in the "Scenario Analysis" results.
- [x] Task: Synchronize legacy engine `src/nhra_gt/engine.py` for parity.
- [x] Task: Final verification with `tests/test_capacity_friction.py`.

---
**Track Status:** COMPLETED 2025-12-28
Asymmetric capacity friction and fiscal adjustment costs implemented across both engines. Dashboard updated with VFI Waterfall integration. Tests passed.
