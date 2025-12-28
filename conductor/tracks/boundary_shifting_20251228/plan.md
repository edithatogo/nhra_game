# Implementation Plan: Boundary Shifting & Stream Mix Game

## Phase 1: Engine Extension [checkpoint: 3239f38]
- [x] Task: Update `LhnState` and `StateJax` to include `block_funding_revenue` and `stream_mix`.
- [x] Task: Update `ParamsJax` with `block_funding_base` and `shifting_friction`.
- [x] Task: Implement `calculate_boundary_shift` in `src/nhra_gt/engine_jax.py`.

## Phase 2: Multi-Agent Logic [checkpoint: 3239f38]
- [x] Task: Add `VENUE_SHIFT` to the LHN utility function in `src/nhra_gt/agents.py`.
- [x] Task: Implement the "Venue Selection" game in JAX solvers.

## Phase 3: Dashboard & Visualization [checkpoint: 3239f38]
- [x] Task: Update "Intra-State LHN Variance" tab with a "Funding Stream Mix" chart.
- [x] Task: Final verification with `tests/test_boundary_shifting.py`.
