# Reporting checklist guidance

This work mixes **policy analysis**, **simulation modelling**, and **game-theory mechanism mapping**.

For the modelling and simulation components, the closest fit is:

- **STRESS** (Strengthening the Reporting of Empirical Simulation Studies) guideline.

Depending on how the MJA paper is framed:
- If positioned as a policy analysis with a conceptual model, STRESS can be used for the simulation sections while the narrative follows standard MJA IMRAD structure.
- If reframed as an economic/HTA-type model, consider **ISPOR-SMDM** good research practices for modelling; however the current repo is intentionally non-predictive and avoids cost-effectiveness claims.

## STRESS elements we explicitly address in this repo
1. Model purpose, scope, perspective (`context/00_*`, `docs_mkdocs/models.md`).
2. Model structure, logic, and assumptions (`context/02_*`, `context/05_*`).
3. Data/parameters and provenance (`context/04_*`, `context/06_*`).
4. Implementation details and reproducibility (Dockerfile, CI, tests, Snakemake, Justfile).
5. Verification/validation (unit tests for equilibria solvers + invariants; sensitivity and scenario analyses).
6. Results and uncertainty reporting (scenario tables + global sensitivity).
