# Initial Concept

This is a project which was developed in chatgpt, and has over a dozen versions. It's supposed to be incremental development, but there might have been variations throughout. What I'm thinking is that I'll need you to setup the most recent version as a repo, initiatlising git etc. but also archiving the old copies. I'd also want you to then review all of the older versions, and ascertain whether any features have unintentionally been dropped, then develop a plan to add them back in. From there I'm keen for you to develop a roadmap to get this to be a SOTA model for the stated purpose.

---

# Product Guide

## Vision
To develop a State-of-the-Art (SOTA) predictive game-theory model of the National Health Reform Agreement (NHRA) negotiations. This model will evolve from an illustrative tool to a rigorous forecasting instrument capable of influencing public policy.

## Primary Goals
1.  **Predictive Fidelity & Calibration:** Elevate the model to predictive forecasting, validated through rigorous backtesting against historical NHRA outcomes.
2.  **Evidence Grounding:** Establish rigorous, publicly traceable evidence for all parameters.
3.  **Reproducibility:** Ensure all results are independently reproducible via strict provenance tracking and containerization (critical for MJA).
4.  **Feature Recovery:** Systematically review and re-integrate valuable features lost during iterative development.
5.  **Publication:** Produce original research suitable for publication in the Medical Journal of Australia (MJA).

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
9.  **Standardized Visualization API:** A unified, configuration-driven plotting infrastructure with visual regression testing (`pytest-mpl`) to ensure publication-ready figures.
10. **SOTA Technical Artifacts:** Formal C4/ODD technical diagrams, evidence-linked feature matrices, and automated documentation drift detection integrated into the development lifecycle.
