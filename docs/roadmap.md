# tasks.md — Roadmap and implementation plan (v21)

**Version:** v21
**Date:** 2025-12-21

## Completed in v21

1. Added **requirements.md**, **design.md**, **tasks.md** as durable context artifacts.
2. Extended the **context pack** to incorporate these artifacts.
3. Tightened the grounding system to enforce **publicly retrievable sources only**.
4. Updated developer workflows (`just`, `snakemake`) to build the context pack and run grounding checks.

## Completed in v23 — Reporting & Scenarios
1. **Negotiation Dashboard:** Added Effective Share Drift analysis and Ranked Intervention Table.
2. **Automated Methods:** Implemented `generate_methods_appendix.py` and academic-style parameter exports.
3. **Refined Mechanisms:** Resolved validation discrepancies; model now aligns with historical Rank #1 driver (Discharge Delay).

## Completed in v24/v25 — Evidence, Security & Release
1. **Empirical API:** Automated ingestion from AIHW MyHospitals API (ED performance).
2. **Bibliography Engine:** Implemented academic citation manager with RIS/ENW/BIB exports.
3. **Security Hardening:** Integrated Bandit security scanning, Mutmut mutation testing, and pinned `requirements.lock`.
4. **Audit Trails:** Implemented `Recorder` for high-fidelity experiment provenance.
5. **Gold Master:** Released v25.0.0 with optimized Docker environment.

## Completed in v26 — Codebase Maturity
1. **Modern Tooling:** Prepared dependencies for JAX acceleration.
2. **Community Standards:** Added CONTRIBUTING/CODE_OF_CONDUCT and automated docs deployment.
3. **CI Hardening:** Expanded testing matrix to Ubuntu/macOS/Windows.

## Next (v27) — Refactoring, Visualization & Deep Audit (Polishing the Core)

### Core Refactoring
- **Naming Convention:** Rename opaque files (e.g., `v9.py` -> `engine.py`) for intuitive navigation.
- **Artifact Versioning:** Implement timestamped output directories (`outputs/experiments/YYYY-MM-DD/...`) to prevent overwrites.

### Visualization & Polish
- **Dynamic Animation:** Generate GIFs/Videos of simulation trajectories (Pressure/Risk over time).
- **Publication Polish:** Ensure all dashboard plots and exported figures meet high-impact journal standards (vector graphics, colorblind safe).

### Dashboard & Visualization Parity (From Forensic Audit)
- **Interactive Map:** Integrate the D3-based games network into the Streamlit dashboard.
- **GSA Visualization:** Implement full Sobol variance decomposition and interaction heatmap tabs.
- **Expert Mode:** Add direct subgame strategy overrides (e.g., forcing Commonwealth to play 'Strict').
- **Convergence Guard:** Implement UI indicator for Monte Carlo statistical convergence.

### Forensic Deep Dive
- **Code Investigator:** Systematically audit all legacy versions using AI agents to recover any missed logic or "ghost" features.
- **Library Review:** Evaluate integration of new libraries (e.g., Mesa, PyGambit) vs current custom implementations.

## Future Track: Advanced Calibration & Validation
- **Bayesian Inference:** Move from TPESampler to fully Bayesian calibration (PyMC/Stan).
- **Counterfactual Validation:** Test model against historical shocks not in training data.

## Future Track: Enhanced User Experience
- **Interactive Scenarios:** Allow policymakers to build intervention bundles via UI drag-and-drop.
- **Explainable AI:** Add tooltips and narrative generation explaining *why* a specific outcome occurred.

## Future Track: Cloud & Cognitive Agents (On Hold)
- **Simulation Visualization:** Live visual feedback during execution.
- **LLM Agent Sophistication:**
    - **Debate Loop:** Cth/State agents exchange structured arguments.
    - **RAG Integration:** Agents cite specific NHRA clauses from `context/`.
    - **Multi-Agent Negotiation:** Enable dynamic adaptation beyond static parameters.
- **Cloud Operations:** Terraform/Docker hardening for AWS/Azure.

## Governance and maintenance

- Maintain a `decisions/` log for major modelling choices.
- Ensure each version update:
  - increments CHANGELOG,
  - regenerates CONTEXT_PACK.md/json,
  - re-runs `just all` in CI.

## Governance and maintenance

- Maintain a `decisions/` log for major modelling choices.
- Ensure each version update:
  - increments CHANGELOG,
  - regenerates CONTEXT_PACK.md/json,
  - re-runs `just all` in CI.
