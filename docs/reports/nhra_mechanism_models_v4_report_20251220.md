# NHRA mechanism models — v4 report (20251220)

This version implements the requested improvements in a single, reproducible pipeline:

- **Empirical anchoring / backcast check**: a coarse grid-search reproduces the *ED proxy shift* between two anchor regimes.
- **Jurisdiction heterogeneity**: metro/regional/remote parameterisation with a weighted aggregate.
- **Global sensitivity (Morris screening)** over key parameters (importance ranking).
- **Correlated uncertainty robustness** (multivariate lognormal draws) with 10–90% bands.
- **Single “policy dashboard” plot**: ED proxy vs capacity with occupancy and offload encoded.
- **Intervention → policy ask translation table**.
- **Bargaining layer**: Nash bargaining + a discrete alternating-offers approximation.

> **Important**: these are stylised mechanism models and proxy outcomes (not forecasts). Use as structured reasoning aids.

---

## Key outputs (paths)

### Weighted intervention summary (main table)
- `outputs/v4/v8_v4/v8_interventions_summary_weighted.csv`

### By-jurisdiction intervention summary
- `outputs/v4/v8_v4/v8_interventions_by_jurisdiction.csv`

### Policy asks mapping
- `outputs/v4/policy_asks.csv`

### Backcast validation
- `outputs/v4/backcast_v4/backcast_best.csv`
- `outputs/v4/backcast_v4/backcast_error_heatmap.png`
- `outputs/v4/backcast_v4/backcast_timeseries.png`

### Sensitivity (Morris)
- `outputs/v4/sensitivity_v4/morris_screening.csv`
- `outputs/v4/sensitivity_v4/morris_mu_star.png`

### Correlated robustness
- `outputs/v4/robustness_corr_v4/v8_corr_robustness_summary.csv`
- `outputs/v4/robustness_corr_v4/v8_corr_robustness_ed_bands.png`

### Bargaining
- `outputs/v4/bargaining_v4/nash_solution_alpha0p5.csv`
- `outputs/v4/bargaining_v4/payoff_space.png`
- `outputs/v4/bargaining_v4/alt_offers_choice_heatmap.png`

---

## Weighted scenario ranking (higher ED proxy is better)

| tag                |   mean_ed |   mean_occ |   mean_los |   mean_offload |   mean_c |
|:-------------------|----------:|-----------:|-----------:|---------------:|---------:|
| capacity_build     |     0.57  |      0.9   |       5.76 |           26.2 |    0.925 |
| governance_package |     0.563 |      0.907 |       5.89 |           27.5 |    0.852 |
| baseline           |     0.553 |      0.911 |       5.98 |           28.4 |    0.816 |
| treasury_relax     |     0.553 |      0.911 |       5.98 |           28.4 |    0.816 |
| audit_heavy        |     0.525 |      0.93  |       6.35 |           32.2 |    0.628 |

---

## Backcast validation (best grid point)

This selects new-regime multipliers (S0, dep0) that best match the two ED-proxy anchors.

|   S_mult |   dep0_mult |   mean_old |   mean_new |       err |
|---------:|------------:|-----------:|-----------:|----------:|
|    1.275 |      1.2625 |   0.550521 |   0.529197 | 0.0142759 |

---

## Global sensitivity (top 5 by Morris μ*)

| param   |   mu_star |   sigma |
|:--------|----------:|--------:|
| dep0    |     18.8  |   9.3   |
| S0      |     17.3  |  13.8   |
| eta_a   |     13.5  |   4     |
| dep_x   |      1.08 |   0.633 |
| k_r     |      0.1  |   0.124 |

---

## Correlated robustness (ED proxy 10–90% bands)

|   mean_ed |   p10_ed |   p90_ed | scenario           |
|----------:|---------:|---------:|:-------------------|
|     0.527 |    0.507 |    0.55  | audit_heavy        |
|     0.553 |    0.535 |    0.575 | baseline           |
|     0.57  |    0.561 |    0.581 | capacity_build     |
|     0.563 |    0.55  |    0.572 | governance_package |
|     0.553 |    0.535 |    0.575 | treasury_relax     |

---

## Bargaining outcomes (α=0.5 Nash)

| chosen_tag         |        UC |       US |   alpha |
|:-------------------|----------:|---------:|--------:|
| int_capacity_build | -0.908486 | -3.22036 |     0.5 |

---

## Intervention → policy asks

| scenario           | policy_asks                                                                                                                                                                                                      |
|:-------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| audit_heavy        | Avoid integrity settings that increase compliance burden without throughput gains. | If integrity strengthened, offset with funded admin time + interoperability.                                                |
| baseline           | Continue Schedule-K style supplementation without structural alignment.                                                                                                                                          |
| capacity_build     | Fund middle-tier workforce + discharge pathways as ‘capacity stock’. | Explicitly finance flow/governance overhead for inter-agency discharge.                                                                   |
| governance_package | Regional pooled funding pilots to reduce interface friction. | NEP/indexation realism to shrink the valuation gap. | Integrate UCCs/primary initiatives into LHN clinical governance + digital interoperability. |
| treasury_relax     | Relax constraints that cap upstream effort (effective cap on investment). | Treat ‘45%’ and indexation as contingent on realistic capacity build.                                                                |

---

## Figure index

- Weighted bars:  
  `outputs/v4/v8_v4/v8w_mean_ed.png`  
  `outputs/v4/v8_v4/v8w_mean_capacity.png`  
  `outputs/v4/v8_v4/v8w_mean_occ.png`  
  `outputs/v4/v8_v4/v8w_mean_los.png`  
  `outputs/v4/v8_v4/v8w_mean_offload.png`

- **Policy dashboard (single chart)**:  
  `outputs/v4/v8_v4/v8w_policy_dashboard.png`

- Jurisdiction ED bars:  
  `outputs/v4/v8_v4/v8_metro_mean_ed.png`  
  `outputs/v4/v8_v4/v8_regional_mean_ed.png`  
  `outputs/v4/v8_v4/v8_remote_mean_ed.png`

- Backcast plots:  
  `outputs/v4/backcast_v4/backcast_error_heatmap.png`  
  `outputs/v4/backcast_v4/backcast_timeseries.png`

- Sensitivity:  
  `outputs/v4/sensitivity_v4/morris_mu_star.png`

- Bargaining:  
  `outputs/v4/bargaining_v4/payoff_space.png`  
  `outputs/v4/bargaining_v4/alt_offers_choice_heatmap.png`

- Robustness:  
  `outputs/v4/robustness_corr_v4/v8_corr_robustness_ed_bands.png`
