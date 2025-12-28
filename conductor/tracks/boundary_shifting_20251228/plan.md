# Implementation Plan: Boundary Shifting & Stream Mix Game

## Phase 1: Engine Extension
- [ ] Task: Update `LhnState` and `StateJax` to include `block_funding_revenue` and `stream_mix`.
- [ ] Task: Update `ParamsJax` with `block_funding_base` and `shifting_friction`.
- [ ] Task: Implement `calculate_boundary_shift` in `src/nhra_gt/engine_jax.py`.

## Phase 2: Multi-Agent Logic
- [ ] Task: Add `VENUE_SHIFT` to the LHN utility function in `src/nhra_gt/agents.py`.
- [ ] Task: Implement the "Venue Selection" game in JAX solvers.

## Phase 3: Dashboard & Visualization
- [ ] Task: Update "Intra-State LHN Variance" tab with a "Funding Stream Mix" chart.
- [ ] Task: Final verification with `tests/test_boundary_shifting.py`.
