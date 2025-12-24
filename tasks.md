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

## Next (v26) — Cloud & Cognitive Agents (Future Vision)

### Cognitive Simulation
- **LLM Agents:** Replace heuristic game strategies with LLM-driven agents that negotiate based on actual policy documents (RAG).
- **Narrative Generation:** Auto-generate policy briefs explaining *why* a specific equilibrium was reached.

### Operationalisation
- **Cloud Deployment:** Terraform/IaC for deploying the Streamlit dashboard to AWS Fargate or Azure Container Apps.
- **Continuous Data:** GitHub Actions workflow to run `ingest_aihw_api.py` weekly and commit fresh data.

### Advanced Calibration
- **Bayesian Inference:** Move from TPESampler to fully Bayesian calibration (PyMC/Stan) for posterior uncertainty estimation.

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
