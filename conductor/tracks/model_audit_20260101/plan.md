# Plan: Comprehensive Model Audit and Repairs

## Phase 1: Audit Setup & Inventory [checkpoint: 9535c5f]
- [x] Task: Confirm model definition and scan repo for candidate models d3875f3
  - [x] Sub-task: Identify directories/modules containing models
  - [x] Sub-task: Review docs/README for model list
- [x] Task: Create audit report structure in `audit.md` (methodology, tables, provenance placeholders) 526f425
- [x] Task: Define audit artifacts/deliverables (inventory table, reference registry, risk register, validation results table) 1e1910e
- [x] Task: Build initial model inventory table (name, location, purpose, inputs/outputs, dependencies) 2fa442a
- [x] Task: Establish reference registry and citation conventions (manage_refs.py workflow) fac4200
- [x] Task: Define assumption & risk register template fedc255
- [x] Task: Check data access/licensing constraints for published sources bc0a980
- [x] Task: Conductor - User Manual Verification 'Phase 1: Audit Setup & Inventory' (Protocol in workflow.md) 9535c5f

## Phase 2: Input & Assumption Validation [checkpoint: d94e2f6]
- [x] Task: For each model, enumerate inputs and parameter sources aafdf8f
- [x] Task: Map each input to a published source; record DOI/URL, date, units, scaling 0cfaaac
- [x] Task: Document and assess assumptions (rationale, risk, impact) 0cfaaac
- [x] Task: Validate reference correctness vs parameter values (units/scales) 0cfaaac
- [x] Task: Conductor - User Manual Verification 'Phase 2: Input & Assumption Validation' (Protocol in workflow.md) d94e2f6

## Phase 3: Output Validation (Benchmarks + Sanity Checks) [checkpoint: 80ce822]
- [x] Task: Define benchmark selection criteria and rationale 85a7fdf
- [x] Task: Identify benchmarks for each model and define acceptance thresholds 9d9da3f
- [x] Task: Implement/extend validation harness with tests (TDD: write failing tests, implement, refactor) 06cb139
  - [x] Sub-task: Add sanity checks (range/unit/monotonicity/edge cases)
  - [x] Sub-task: Add benchmark comparison tests where available
- [x] Task: Run validation suite and record results in audit report, noting gaps 06cb139
- [x] Task: Conductor - User Manual Verification 'Phase 3: Output Validation (Benchmarks + Sanity Checks)' (Protocol in workflow.md) 80ce822

## Phase 4: Repairs & Verification
- [x] Task: Triage issues by severity and prioritize fixes ca1c4ff
- [ ] Task: For each issue, write failing tests or validation checks (TDD)
- [ ] Task: Implement fixes (including model logic changes) and rerun tests
- [ ] Task: Run full test/coverage/lint/type checks and record results
- [ ] Task: Update references/assumptions and record before/after evidence
- [ ] Task: Produce consolidated change log with before/after metrics
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Repairs & Verification' (Protocol in workflow.md)

## Phase 5: Audit Finalization
- [ ] Task: Stakeholder review of audit report (lightweight sign-off)
- [ ] Task: Finalize audit report (inventory, validations, issues, fixes, evidence)
- [ ] Task: Record provenance metadata (git SHA, data version, timestamps, seeds, environment)
- [ ] Task: Review for completeness, traceability, and policy compliance
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Audit Finalization' (Protocol in workflow.md)
