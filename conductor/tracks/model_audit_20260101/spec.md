# Track Spec: Comprehensive Model Audit and Repairs

## Overview
Conduct a full audit of all computational models in the repository. For every model, validate all inputs, assumptions, and outputs against published sources only. Document the audit with clear references and justified assumptions, then repair any issues found (including model logic changes when needed).

## Scope
- All computational models in the repo.
- Inputs/assumptions must be tied to published sources only.
- Output "sense checks" must include both:
  - Comparison to known historical NHRA outcomes or published benchmarks, and
  - Sanity checks (ranges/units/monotonicity/edge cases).

## Definitions
- **Model:** Any computational component that transforms inputs into outputs for simulation, prediction, optimization, calibration, or decision analysis.
- **Published Source:** Peer-reviewed papers, official government reports, or formally published datasets. (No internal docs as sources for parameter values.)

## Functional Requirements
1. **Model Inventory**
   - Produce a complete inventory of all models in scope.
   - Record model location, purpose, inputs, outputs, and dependencies.

2. **Input & Assumption Validation**
   - For each input parameter: map to a published source.
   - For each assumption: justify explicitly and mark risk/uncertainty.
   - Record DOI/URL, publication date, parameter value mapping, units, and scaling.

3. **Reference & Assumption Policy**
   - **Sourced Inputs:** must have published references only.
   - **Assumptions:** must include rationale, risk level (low/med/high), and impact note.
   - All references must be traceable, consistent with values, and properly cited.

4. **Output Validation (Sense Checks)**
   - Benchmark comparison vs. historical NHRA outcomes or published benchmarks where available.
   - Sanity checks: ranges, units, monotonicity, edge cases.
   - If no benchmark exists: document the gap and apply expanded sanity checks.

5. **Issue Tracking and Repair**
   - Classify issues by severity (critical/high/medium/low).
   - Repair all issues found, including model logic changes when required.
   - Record before/after evidence for each fix.

6. **Audit Report**
   - Document model inventory, validations, references, assumptions, output checks, issues, and fixes.
   - Use a structured table format for traceability.
   - Include an **Assumption & Risk Register** table.

7. **Audit Methodology**
   - Step-by-step workflow covering inventory, validation, sense checks, and repair evidence.
   - Define how benchmarks are selected and what constitutes a pass/fail.

8. **Provenance & Reproducibility**
   - Record git SHA, data version, run timestamp, random seed(s), and environment details for all validations.

9. **Reference Management**
   - Centralize references in the existing citation pipeline (e.g., `manage_refs.py`) when applicable.
   - Ensure every reference used in the audit is registered and traceable.

10. **Output Thresholds**
   - Define acceptance bands or tolerances for benchmark comparisons when available.
   - If no benchmark exists, document alternative thresholds and rationale.

## Non-Functional Requirements
- References must be published sources only.
- Audit documentation must be clear, reproducible, and traceable.
- Changes must align with the existing tech stack and workflow.
- Repairs must include updated/added tests where appropriate.

## Acceptance Criteria
- All models are inventoried with clear boundaries and locations.
- Every input and assumption is validated with published sources or explicit justification.
- All references include DOI/URL, publication date, value mapping, units, and scaling.
- Output validation includes benchmark comparisons (where available) and sanity checks.
- Audit report includes a structured methodology, provenance, and risk register.
- Audit report is stored at `conductor/tracks/<track_id>/audit.md`.
- All identified issues are repaired with before/after evidence.

## Out of Scope
- New features not required for validation or repairs.
- Refactors unrelated to audit findings.

## Assumptions
- Published sources relevant to NHRA parameters are accessible.
- Model boundaries are discoverable with reasonable inspection.
