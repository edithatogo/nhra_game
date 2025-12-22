# tasks.md — Roadmap and implementation plan (v21)

**Version:** v21  
**Date:** 2025-12-21

## Completed in v21

1. Added **requirements.md**, **design.md**, **tasks.md** as durable context artifacts.
2. Extended the **context pack** to incorporate these artifacts.
3. Tightened the grounding system to enforce **publicly retrievable sources only**.
4. Updated developer workflows (`just`, `snakemake`) to build the context pack and run grounding checks.

## Next (v22) — make the model more “MJA original article” ready

### Empirical spine
- Add NEP time series sourced to public IHACPA determinations (annual $/NWAU) with locators.
- Add input-cost proxy series (ABS WPI health) with locators.
- Add a lightweight back-test: demonstrate the model reproduces directionality of 2–3 observed indicators.

### Reporting
- Add an “NHRA negotiation dashboard”:
  - threshold plot for effective share drift,
  - ranked intervention table with uncertainty ranges.
- Expand the methods appendix and the parameter registry export into the paper-ready format.

### Robustness
- Add PSA with evidence-based distributions for selected parameters.
- Add stability analysis summary for deterministic dynamics.

## Governance and maintenance

- Maintain a `decisions/` log for major modelling choices.
- Ensure each version update:
  - increments CHANGELOG,
  - regenerates CONTEXT_PACK.md/json,
  - re-runs `just all` in CI.
