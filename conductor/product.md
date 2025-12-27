# Initial Concept

This is a project which was developed in chatgpt, and has over a dozen versions. It's supposed to be incremental development, but there might have been variations throughout. What I'm thinking is that I'll need you to setup the most recent version as a repo, initiatlising git etc. but also archiving the old copies. I'd also want you to then review all of the older versions, and ascertain whether any features have unintentionally been dropped, then develop a plan to add them back in. From there I'm keen for you to develop a roadmap to get this to be a SOTA model for the stated purpose. **Update (Dec 2025):** The repository has undergone a comprehensive structural audit, standardizing the package name to `nhra_gt` and optimizing core Nash Equilibrium solvers for 2x performance.
**Publication Update (Dec 2025):** A comprehensive publication series has been drafted, including a qualitative mapping of the NHRA statutory text, a quantitative simulation study of strategic gaming equilibria, and a RACMA position statement for the 2025-2030 negotiations.

---

# Product Guide

## Vision
To develop a State-of-the-Art (SOTA) predictive game-theory model of the National Health Reform Agreement (NHRA) negotiations. This model will evolve from an illustrative tool to a rigorous forecasting instrument capable of influencing public policy.

## Primary Goals
1.  **Predictive Fidelity & Calibration:** Elevate the model to predictive forecasting, validated through rigorous backtesting against historical NHRA outcomes. **High-priority focus on JAX/XLA acceleration.**
2.  **Evidence Grounding:** Establish rigorous, publicly traceable evidence for all parameters, now validated through a systematic qualitative mapping of the NHRA statutory text.
3.  **Reproducibility:** Ensure all results are independently reproducible via strict provenance tracking and containerization (critical for MJA).
4.  **Feature Recovery:** Systematically review and re-integrate valuable features lost during iterative development.
5.  **Publication:** Successfully drafted three manuscripts (P1, P2, P3) adhering to MJA and RACMA standards, incorporating a rigorous single-author analytical review protocol.

## Target Audience
-   **Primary:** RACMA Policy & Advocacy Directorate.
-   **Academic:** MJA Reviewers and the broader academic community.
-   **Government:** Commonwealth and State Health Department Analysts.

## Key Features (Prioritized)
1.  **High-Performance Sensitivity & Calibration:** HPC-accelerated global sensitivity analysis (Sobol/Morris) and automated parameter calibration.
2.  **Strategic Scenario Analysis:** Interactive counterfactuals to simulate negotiation outcomes and strategy shifts with expert-level direct control.
3.  **Interactive Web Dashboard:** A user-friendly interface (e.g., Streamlit/Dash) for policy engagement.
4.  **Automated Data Pipelines:** Robust ingestion of public health data (AIHW/ABS) to maintain model currency.
5.  **Modular Pipeline Execution (GUI):** Capability to select individual "games" from the strategic map (Mermaid/Graphviz) via the dashboard to isolate their impact on system performance.
6.  **Real-time Simulation Visualization:** Live visual feedback of agent behaviors and state transitions while the simulation is executing.
7.  **Performance Profiling & Benchmarking Suite:** Automated profiling (e.g., using `pyinstrument` or `scalene`) to ensure computational efficiency as MC rollouts scale.
8.  **Automated Quality & Security Audits:** Formalized mutation testing (mutmut) and security scanning (bandit/safety) integrated into the CI pipeline.
