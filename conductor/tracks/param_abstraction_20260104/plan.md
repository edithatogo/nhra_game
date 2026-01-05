# Implementation Plan: Parameter Abstraction (Exhaustive)

## Phase 1: Schema Extension
- [x] **Task 1.1: Define Nested Pydantic Models**
  - Update `src/nhra_gt/domain/params.py` to include `OperationalParams`, `BehavioralParams`, and `PolicyParams`.
- [x] **Task 1.2: Update JAX State Definitions**
  - Update `src/nhra_gt/domain/state.py` to include the corresponding `flax.struct.dataclass` structures in `ParamsJax`.
  - Ensure `replace` and `to_params_jax` handle nesting correctly.

## Phase 2: Engine Refactor (Operational)
- [x] **Task 2.1: Abstract `engine.py` Constants**
  - Replace magic numbers in `lhn_step_jax`, `mm_s_queue_wait_jax`, and `within4_from_pressure_jax`.
- [x] **Task 2.2: Abstract `rules.py` Multipliers**
  - Replace hardcoded values in `CapRule`, `AuditRule`, and `ReconciliationRule`.

## Phase 3: Subgame Refactor (Behavioral)
- [x] **Task 3.1: Abstract `games.py` Payoffs**
  - Systematically move subgame coefficients to `BehavioralParams`.
- [x] **Task 3.2: Sync `games_jax.py`**
  - Ensure JAX-native subgame implementations use the new parameters.

## Phase 4: Configuration & Verification
- [x] **Task 4.1: Update `defaults.yaml`**
  - Export current defaults to the configuration file.
- [x] **Task 4.2: Parity Testing**
  - Run existing tests to ensure baseline results are identical to the hardcoded version.
- [x] **Task 4.3: Calibration Demo**
  - Create a test/script showing JAX gradient descent optimization of a strategic coefficient.

## Phase 5: Residual Abstraction (Iterative)
- [x] **Task 5.1: Abstract Engine Residuals**
  - [x] Abstract `lhn_step_jax` clipping bounds (`0.75`, `1.50`, `0.78`, `0.98`) into `OperationalParams`.
  - [x] Abstract `step_jax` auditor constants (`0.03`, `0.95`, `0.25`).
  - [x] Abstract `mm_s_queue_wait_jax` capacity scalar (`10.0`).
- [x] **Task 5.2: Abstract Subgame Residuals**
  - [x] Review and abstract payoff offsets in `definition_game`, `bargaining_game`, `cost_shifting_game`, etc.
  - [x] Ensure `games_jax.py` counterparts are also updated.
- [x] **Task 5.3: Abstract Rule & Queuing Residuals**
  - [x] Parameterize `EligibilityRule` clips.
  - [x] Parameterize `PatientUtilityParams` defaults (if not already covered).
- [x] **Task 5.4: Iterative Verification**
  - [x] Run `codebase_investigator` to verify abstraction completeness.
  - [x] If issues found, repeat abstraction tasks until investigator approves.
