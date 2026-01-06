# Track Specification: Pipeline Refactoring & Robustness (20251230)

## Goal

To modernize the NHRA Game simulation pipeline by modularizing the workflow orchestration (Snakemake), integrating standardized NLP capabilities (SpaCy) for evidence alignment, and implementing advanced process mining (PM4PY) for drift analysis and visualization.

## Core Components

### 1. Workflow Modularization (Snakemake)

**Current State:** Monolithic `Snakefile` handling data ingestion, simulation, and plotting.
**Target State:** Modular `workflow/rules/` structure.

- `workflow/Snakefile`: Main entry point, including sub-rules.
- `workflow/rules/ingestion.smk`: Data loading and preprocessing strings.
- `workflow/rules/simulation.smk`: Core simulation sweeps and calibration.
- `workflow/rules/analysis.smk`: Post-processing, plotting, and reporting.

### 2. NLP Standardization (SpaCy)

**Objective:** Replace ad-hoc string parsing with robust NLP for mapping evidence to model parameters.
**Implementation:**

- Dependency: Add `spacy` and `en_core_web_sm` to project dependencies.
- Module: `src/nhra_gt/nlp/processor.py`
- Capabilities: Named Entity Recognition (NER) for policy actors, dependency parsing for claim logic.

### 3. Advanced Process Mining (PM4PY)

**Objective:** Visualize simulation trajectories as event logs to detect policy drift and structural shifts.
**Implementation:**

- Dependency: Add `pm4py` to project dependencies.
- Module: `src/nhra_gt/process_mining/visualizer.py`
- Visualizations:
  - Directly Following Graphs (DFG) for patient flow.
  - Social Network Analysis (SNA) for agent interactions.
- Drift Detection: Implement concept drift analysis to identify when system behavior fundamentally changes (e.g., pre- vs post-policy).

### 4. Robustness & Integration

**Objective:** Ensure the refactored pipeline is stable and reproducible.
**Implementation:**

- Integration Tests: `tests/integration/test_pipeline_e2e.py` running a minimal Snakemake DAG.
- Data Integrity: Checksums and schema validation between pipeline stages.

## Success Criteria

1. `snakemake -n` produces a valid DAG with modular rules.
2. SpaCy pipeline correctly extracts entities from sample policy text.
3. PM4PY generates at least one DFG and one Drift plot from simulation output.
4. End-to-end integration test passes in < 5 minutes.

## Acceptance Checklist (Evaluation)

- [x] Requirements and scope validated against this spec
- [x] Acceptance criteria evaluated and recorded (pass/fail)
  - PASS: Modular Snakemake (Phase 1)
  - PASS: NLP SpaCy integration (Phase 1)
  - PASS: Integration testing (Phase 3)
  - FAIL/CANCELLED: PM4PY (Phase 2 cancelled to prioritize pipeline robustness)
- [x] CI green and key workflows verified
- [x] Deployment/runtime checks complete (if applicable)
- [x] Deviations or follow-ups documented
  - **Deviation:** Advanced Process Mining (PM4PY) was cancelled to focus resources on pipeline modularity and error reconciliation.
  - **Follow-up:** Re-evaluate Process Mining for a future specialized track if needed.
