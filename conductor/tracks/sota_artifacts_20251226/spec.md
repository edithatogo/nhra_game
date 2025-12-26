# Specification: SOTA Project Documentation & Artifacts Enhancement

## 1. Overview
Elevate the project to a State-of-the-Art (SOTA) standard through high-rigor technical visualization, evidence-linked feature matrices, and formal academic metadata. The goal is to provide "instant clarity" for policy-makers and "methodological transparency" for academic reviewers.

## 2. Functional Requirements

### 2.1 Formal Technical Diagrams (Mermaid/C4/ODD)
- **ER Diagrams (Data Integrity):**
    - `ER-A (Grounded Params)`: Map `Params` dataclass to specific AIHW/NHRA evidence keys.
    - `ER-B (State Vectors)`: Schema of the `State` dictionary and temporal persistence.
    - `ER-C (Strategic Nodes)`: Object model of Game nodes, Strategies, and Payoff matrices.
    - `ER-D (Provenance)`: Relationship between Simulation Seeds, Output Data, and Figure IDs.
- **Engineering Diagrams (C4 Model):**
    - `Level 1 (System Context)`: How the model sits between Data Sources (AIHW) and Users (Dashboard).
    - `Level 2 (Containers)`: The Python runtime, Streamlit server, and Data Storage layers.
    - `Level 3 (Components)`: The relationship between `Engine`, `Domain`, `Sensitivity`, and `Visualization`.
- **Workflow & Logic (ODD Protocol):**
    - `Flow-A (Dev)`: Conductor lifecycle + TDD Quality Gates.
    - `Flow-Data`: The "Evidence-to-Output" pipeline (Ingestion -> Calibration -> GSA -> Report).
    - `Flow-GameTheory`: The "Strategic Chain" (How Bargaining affects Compliance, etc.).
    - `Flow-Conceptual`: A high-level "Mechanism Map" for non-technical stakeholders.

### 2.2 Evidence-Linked Feature Matrix
Created in `docs/feature_matrix.md` with the following columns:
- **Feature Name**: (e.g., 45% Commonwealth Share Logic)
- **Category**: (Modeling, Analysis, Integrity, Policy)
- **Status**: (Alpha/Beta/Stable)
- **Verification**: (Unit Test ID, Visual Regression ID, or Backtest Metric)
- **Evidence Source**: (Direct link to NHRA Section or AIHW Report)

### 2.3 Academic & Metadata Artifacts
- **CITATION.cff**: Full author list, ORCIDs, DOI placeholder, and repository software metadata.
- **README.md Overhaul**: A professional, visual-first landing page with "Badges" for coverage, quality, and security.
- **Social Preview**: A custom-designed `og-image.png` for professional sharing.

## 3. Technical Requirements
- **Diagrams**: Must be rendered in Mermaid (where possible) for accessibility/searchability.
- **Colorblind Safety**: All diagrams must use the project's Teal/Tealrose palette with high contrast.
- **Automation**: Diagrams must be checked for "drift" against code during CI (via `scripts/verify_docs.py`).
