# Track Specification: Modular Rules Engine (P3)

## 1. Overview

**Goal**: Refactor and expand the simulation's rules engine to be modular, pluggable, and consistent across both Legacy and JAX implementations. This aligns with the audit recommendation to separate "Rules" from "Agents" and "World".
**Context**: Derived from plan phases for modular_rules_engine_20251228.
**Constraints**: None explicitly stated in plan.

## 2. Functional Requirements

- Refactor `src/nhra_gt/rules.py` to use `flax.struct.dataclass` for rules to ensure JAX compatibility (PyTree registration).
- Define standard interfaces for `CapRule`, `AuditRule`, `EligibilityRule`, and `ReconciliationRule`.
- Move existing `HardCap`, `SoftCap`, `ProportionalAudit`, and `ThresholdAudit` to the new structure.
- Eligibility Rules: Implement logic for determining NWAU eligibility (e.g., ABF vs Block Funding boundaries).
- Reconciliation Rules: Implement annual true-up logic, including "Safety Net" or "Bailout" mechanics.
- Pricing Rules: Modularize NEP and WPI application (indexation).

## 3. Non-Functional Requirements

- Automated tests cover track changes.
- Validation checks pass for track changes.
- Verification steps are automated where possible.
- Legacy and JAX implementations remain in parity.
- CI checks are run and must pass.

## 4. Acceptance Criteria

- [ ] Refactor `src/nhra_gt/rules.py` to use `flax.struct.dataclass` for rules to ensure JAX compatibility (PyTree registration).
- [ ] Define standard interfaces for `CapRule`, `AuditRule`, `EligibilityRule`, and `ReconciliationRule`.
- [ ] Move existing `HardCap`, `SoftCap`, `ProportionalAudit`, and `ThresholdAudit` to the new structure.
- [ ] Eligibility Rules: Implement logic for determining NWAU eligibility (e.g., ABF vs Block Funding boundaries).
- [ ] Relevant tests pass for track changes.

## Acceptance Checklist (Evaluation)

- [ ] Requirements and scope validated against this spec
- [ ] Acceptance criteria evaluated and recorded (pass/fail)
- [ ] CI green and key workflows verified
- [ ] Deployment/runtime checks complete (if applicable)
- [ ] Deviations or follow-ups documented
