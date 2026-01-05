# Specification: Comprehensive Parameter Abstraction & Config Externalization

## 1. Overview
The NHRA game theory model contains numerous hardcoded coefficients and "magic numbers" in its core simulation logic (`engine.py`), stage games (`games.py`), and policy rules (`rules.py`). These hardcoded values act as hidden hyperparameters that dictate system behavior, making calibration difficult and obscuring behavioral assumptions. This track aims to abstract all significant coefficients into the `Params` schema, enabling full differentiable calibration and comprehensive sensitivity analysis.

## 2. Functional Requirements

### 2.1 Nested Parameter Schema
- **Goal:** Organize the expanded parameter set into logical groups using nested Pydantic models (and corresponding JAX-compatible structures).
- **Proposed Groups:**
    - `OperationalParams`: Slopes and intercepts for occupancy, wait times, and system pressure.
    - `BehavioralParams`: Coefficients for subgame payoffs (realism benefits, conflict costs, shift gains).
    - `PolicyParams`: Multipliers for audit penalties, bailout thresholds, and rule generosity.

### 2.2 Externalize Magic Numbers
- **Target:** `src/nhra_gt/engine.py`, `src/nhra_gt/subgames/games.py`, `src/nhra_gt/rules.py`.
- **Change:** Replace every non-trivial hardcoded float with a reference to the `Params` object.
- **Example:**
    - Old: `pidx = 0.8 + 0.2 * (wait_min / 60.0) + 0.5 * (occ - 0.8) / 0.1`
    - New: `pidx = p.ops.pressure_base + p.ops.wait_weight * (wait_min / 60.0) + p.ops.occ_weight * (occ - p.ops.occ_target)`

### 2.3 JAX Compatibility
- Ensure all new nested structures are valid JAX PyTrees (using `flax.struct.dataclass` for the internal representation).
- Maintain performance by ensuring no Python overhead during the simulation loop.

### 2.5 Phase 2 Abstraction (Post-Audit Findings)
- **Engine Dynamics:** Abstract clipping bounds (discharge, occupancy), capacity scaling factors, and auditor suspicion decay/increments.
- **Subgames:** Abstract remaining literal offsets in `definition_game` and other legacy games.
- **Rules:** Parameterize internal constants in `EligibilityRule` (e.g., clip bounds).
- **Queuing:** Expose capacity scaling factor and default utility params.

## 3. Acceptance Criteria
- [ ] No significant magic numbers remain in `engine.py`, `games.py`, `rules.py`, `games_jax.py`, or `queuing.py`.
- [ ] The `Params` object (and `ParamsJax`) contains the abstracted coefficients.
- [ ] `defaults.yaml` is fully populated with the new schema.
- [ ] All existing tests pass (parity check).
- [ ] A calibration smoke test demonstrates that the JAX optimizer can now "tune" a previously hardcoded coefficient.
- [ ] **Final Verification:** The `codebase_investigator` agent confirms no significant hardcoded parameters remain.
