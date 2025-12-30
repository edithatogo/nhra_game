# Track Plan: Modular Rules Engine (P3)

**Goal:** Refactor and expand the simulation's rules engine to be modular, pluggable, and consistent across both Legacy and JAX implementations. This aligns with the audit recommendation to separate "Rules" from "Agents" and "World".

## Phase 1: JAX-Compatible Rule Abstractions
- [x] Task: Refactor `src/nhra_gt/rules.py` to use `flax.struct.dataclass` for rules to ensure JAX compatibility (PyTree registration).
- [x] Task: Define standard interfaces for `CapRule`, `AuditRule`, `EligibilityRule`, and `ReconciliationRule`.
- [x] Task: Move existing `HardCap`, `SoftCap`, `ProportionalAudit`, and `ThresholdAudit` to the new structure.

## Phase 2: Implement New Rules
- [x] Task: **Eligibility Rules:** Implement logic for determining NWAU eligibility (e.g., ABF vs Block Funding boundaries).
- [x] Task: **Reconciliation Rules:** Implement annual true-up logic, including "Safety Net" or "Bailout" mechanics.
- [x] Task: **Pricing Rules:** Modularize NEP and WPI application (indexation).

## Phase 3: Engine Integration & Parity
- [x] Task: Update `src/nhra_gt/engine_jax.py` to accept rule objects as parameters instead of using inline logic.
- [x] Task: Update `src/nhra_gt/engine.py` to use the same modular rule objects.
- [x] Task: Ensure `ParamsJax` and `Params` can store/configure which rules are active.

## Phase 4: Validation
- [x] Task: Create `tests/test_modular_rules.py` to verify that swapping rules produces expected changes in funding/outcomes.
- [x] Task: Run parity tests to ensure no regressions in baseline behavior.

---
**Track Status:** COMPLETED 2025-12-28
Modular rules engine implemented across both engines. Rules are now pluggable and JAX-compatible. Verified with unit tests.
