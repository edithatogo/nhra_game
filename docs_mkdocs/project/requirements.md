# Requirements & Scope

This document outlines the research questions, modelling scope, and limitations of the NHRA Game Theory toolkit.

---

## Research Questions

The simulation toolkit is designed to explore:

1. **Funding mechanism effects**: How do different NHRA funding mechanisms (block vs activity-based, Commonwealth/State cost-sharing) affect hospital system pressure?

2. **Strategic incentives**: What equilibrium behaviours emerge from the current institutional structure?

3. **Policy interventions**: Which policy levers (pooled funding, governance integration, transparency) most effectively reduce system pressure?

4. **Interface coordination**: How do aged care, NDIS, and discharge coordination interfaces affect flow?

---

## Modelling Scope

### In Scope

- **Stage game equilibria**: Nine two-player games representing key strategic decision points
- **System dynamics**: Annual evolution of pressure, efficiency gap, and flow metrics
- **Sensitivity analysis**: Sobol global sensitivity analysis for parameter importance
- **Policy comparison**: Scenario modelling for intervention evaluation

### Out of Scope

- **Patient-level microsimulation**: The model operates at system level, not individual patients
- **Spatial heterogeneity**: No geographic variation (state/regional differences)
- **Dynamic games**: Games are static (one-shot); no repeated game dynamics
- **Private sector**: Focus is public hospital funding; private not modelled

---

## Key Assumptions

| Assumption | Justification |
|------------|---------------|
| Two-player games | Simplifies multi-stakeholder dynamics to bilateral negotiations |
| Annual time step | Aligns with NHRA funding cycle; sufficient for policy analysis |
| Nash equilibrium | Standard solution concept; represents strategic stability |
| Parameter independence | First-order sensitivity analysis; interactions via Sobol indices |

---

## Limitations

!!! warning "Model Limitations"

    This is a **stylised mechanism model** for policy reasoning, **not a forecast**. It should be used to understand strategic incentives and compare policy directions, not to predict specific outcomes.

### Key limitations:

1. **Simplified payoffs**: Payoff functions are parameterised approximations, not empirically estimated
2. **Equilibrium selection**: When multiple equilibria exist, selection rules are heuristic
3. **Exogenous shocks**: The model does not include pandemic-like exogenous disruptions
4. **Behavioural factors**: Assumes rational utility-maximising agents; bounded rationality not modelled

---

## Data Sources

All parameters must be grounded in publicly accessible sources. See:

- [Context and Handover](../context.md) for the evidence system
- `context/04_parameter_registry.csv` for the full parameter registry

---

## Roadmap

### Completed

- [x] Core game theory engine with 9 stage games
- [x] Nash equilibrium solver (pure + mixed)
- [x] Monte Carlo simulation with confidence intervals
- [x] Sobol sensitivity analysis integration
- [x] Streamlit dashboard
- [x] MkDocs documentation site

### Planned

- [ ] Repeated game extensions (trigger strategies)
- [ ] Bayesian calibration against empirical data
- [ ] Geographic disaggregation (state-level)
- [ ] Interactive policy scenario builder
