# Round 4 peer-review simulation (v19)

Date: 2025-12-21

## Simulated panel discussion (Round 4)

### Shared priorities (highest to lowest)

1. **Correct framing and restraint in claims.** All participants want the report to emphasise “conceptual model / equilibrium selection,” not prediction.
2. **NEP/NWAU correctness.** Health Economics and the Deputy Secretary strongly prefer explicit wording that NEP is annual and applied to NWAU weights.
3. **Actionable packages.** Policy and Management prioritise packaging: realistic clusters of levers rather than isolated technical knobs.
4. **Methodological transparency.** Economics and Policy want clear explanations of why multiple equilibria matter and what Monte Carlo does (uncertainty + regime switching).
5. **Reproducibility.** The Editor wants a clean “how to reproduce” path, archiving guidance, and a consistent quality stack.

### Points of disagreement (resolved by prioritisation)

- **Optimisation:** Economics is interested, but others prefer keeping v19 scenario-based. Resolution: keep Optuna as an optional future extension only.
- **Granular ABF mechanics:** Health Economics notes IHACPA calculators are complex; Medicine and Policy are neutral; Management worries about distracting from the governance message. Resolution: keep NEP/NWAU explanation correct but avoid embedding classification detail in the core model.

### Agreed presentation approach

- Use the equilibrium grids + package trajectories as the primary communication artefacts.
- Keep the D3 network as an optional workshop tool with a prominent disclaimer.
