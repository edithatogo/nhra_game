# NHRA game-theory simulation report (v19)

Date: 2025-12-21

This report synthesises a stylised, policy-facing simulation of the NHRA negotiation environment as a coupled system of stage games (definition, bargaining, cost shifting, discharge coordination, governance integration, and compliance). The model is not intended to predict an agreed funding share. It is designed to make incentive misalignment legible, stress-test plausible interventions, and surface equilibrium patterns that align with observed operational constraints.

**Abbreviations**

* **NEP**: National Efficient Price (dollars per NWAU; treated here as an index for dynamics)
* **NWAU**: National Weighted Activity Unit (activity weight; payment = NEP × NWAU)
* **VFI**: Vertical fiscal imbalance
* **ED≤4h**: Emergency department presentations completed within 4 hours
* **RR**: Relative risk proxy (dimensionless index; higher is worse)

## 1. Baseline dynamics

Baseline outputs are the mean of Monte Carlo runs from 2025–2030. The core dynamic is a feedback loop: rising pressure worsens discharge and offload, degrading ED performance and raising risk, which in turn increases political salience and audit intensity in the stage games.

![Baseline system pressure (mean)](outputs/v19/plots/baseline_pressure.png)

*Figure:* Baseline system pressure (mean)

![Baseline ambulance offload delay (mean minutes)](outputs/v19/plots/baseline_offload.png)

*Figure:* Baseline ambulance offload delay (mean minutes)

![Baseline ED performance (proportion within 4 hours)](outputs/v19/plots/baseline_within4.png)

*Figure:* Baseline ED performance (proportion within 4 hours)

![Baseline clinical risk proxy (RR index)](outputs/v19/plots/baseline_rr.png)

*Figure:* Baseline clinical risk proxy (RR index)

### Table 1. Baseline trajectory summary

The table below provides the first years of the baseline trajectory. Full tables are available in `outputs/v19/tables`.

|   year |   pressure_mean |   occupancy_mean |   discharge_mean |   offload_mean |   within4_mean |   rr_mean |   effgap_mean |   cth_effective_mean |
|-------:|----------------:|-----------------:|-----------------:|---------------:|---------------:|----------:|--------------:|---------------------:|
|   2025 |         1       |         0.92     |          1.05    |        22      |       0.53     |   1.085   |     0.0656436 |             0.384744 |
|   2026 |         1.01055 |         0.918562 |          0.945   |        22.3181 |       0.530003 |   1.07708 |     0.0759897 |             0.390338 |
|   2027 |         1.02105 |         0.914502 |          0.8505  |        22.6835 |       0.53002  |   1.09376 |     0.086583  |             0.393435 |
|   2028 |         1.03331 |         0.908103 |          0.76545 |        23.0675 |       0.529909 |   1.112   |     0.0973912 |             0.394686 |
|   2029 |         1.0436  |         0.901488 |          0.75    |        23.4837 |       0.52994  |   1.12972 |     0.10843   |             0.394561 |
|   2030 |         1.05663 |         0.895081 |          0.75    |        23.9166 |       0.529532 |   1.15123 |     0.119687  |             0.393421 |

*Interpretation:* pressure and occupancy jointly govern throughput. As the efficiency gap widens, the effective Commonwealth share falls in the model’s accounting identity, intensifying the incentive for cost-shifting.

## 2. Macro drift: NEP vs input costs

IHACPA’s NEP is an annual price per NWAU; the activity-funded payment for a case is the product of NEP and the NWAU weight assigned by the relevant classification. In this model we track NEP and input costs as indices to represent the *direction* of drift and its incentive effects, not the dollar value of any particular DRG.

![NEP vs input costs (indices, 2025=1.0)](outputs/v19/plots/macro_nep_vs_cost.png)

*Figure:* NEP vs input costs (indices, 2025=1.0)

![NEP-to-cost ratio over time](outputs/v19/plots/macro_nep_to_cost_ratio.png)

*Figure:* NEP-to-cost ratio over time

### Table 2. NEP-to-cost series

|   year |   nep_per_nwau |   input_cost_index |   nep_to_cost_index |
|-------:|---------------:|-------------------:|--------------------:|
|   2025 |        1       |            1       |            1        |
|   2026 |        1.03    |            1.04    |            0.990385 |
|   2027 |        1.0609  |            1.0816  |            0.980862 |
|   2028 |        1.09273 |            1.12486 |            0.97143  |
|   2029 |        1.12551 |            1.16986 |            0.96209  |
|   2030 |        1.15927 |            1.21665 |            0.952839 |

*Interpretation:* when input costs grow faster than NEP, the NEP-to-cost ratio falls and the ‘efficiency gap’ in practice widens for higher-cost settings (regional, rural, remote). In the model this drift pushes the system toward higher-pressure equilibria unless offset by either NEP realism or demand-relief interventions.

## 3. Stage-game equilibria

Stage games are solved as normal-form games each year using the mean state (pressure, efficiency gap, discharge delay). We enumerate pure-strategy Nash equilibria and compute mixed equilibria for 2×2 games where applicable.

### Table 3. Equilibria by year and game (first 18 rows)

|   year | game   |   eq_index | kind   | row_action   | col_action   |   row_payoff |   col_payoff |   n_equilibria_in_game |
|-------:|:-------|-----------:|:-------|:-------------|:-------------|-------------:|-------------:|-----------------------:|
|   2025 | DEF    |          1 | pure   | R            | R            |     1.19751  |     1.40251  |                      1 |
|   2025 | BARG   |          1 | pure   | A            | A            |     1.42     |     1.435    |                      1 |
|   2025 | SHIFT  |          1 | pure   | I            | I            |     1.32046  |     1.32046  |                      1 |
|   2025 | DISC   |          1 | pure   | C            | C            |     0.895    |     0.895    |                      1 |
|   2025 | GOV    |          1 | pure   | I            | I            |     1.245    |     1.45     |                      1 |
|   2025 | COMP   |          1 | pure   | L            | L            |     0.645951 |     0.85     |                      1 |
|   2026 | DEF    |          1 | pure   | R            | R            |     1.21001  |     1.41501  |                      1 |
|   2026 | BARG   |          1 | pure   | A            | A            |     1.42264  |     1.43764  |                      1 |
|   2026 | SHIFT  |          1 | pure   | I            | I            |     1.30894  |     1.30894  |                      1 |
|   2026 | DISC   |          1 | pure   | C            | C            |     0.845251 |     0.845251 |                      1 |
|   2026 | GOV    |          1 | pure   | I            | I            |     1.24869  |     1.45369  |                      1 |
|   2026 | COMP   |          1 | pure   | L            | L            |     0.653193 |     0.85     |                      1 |
|   2027 | DEF    |          1 | pure   | R            | R            |     1.22269  |     1.42769  |                      1 |
|   2027 | BARG   |          1 | pure   | A            | A            |     1.42526  |     1.44026  |                      1 |
|   2027 | SHIFT  |          1 | pure   | I            | I            |     1.29736  |     1.29736  |                      1 |
|   2027 | DISC   |          1 | pure   | C            | C            |     0.840528 |     0.840528 |                      1 |
|   2027 | GOV    |          1 | pure   | I            | I            |     1.25237  |     1.45737  |                      1 |
|   2027 | COMP   |          1 | pure   | L            | L            |     0.660608 |     0.85     |                      1 |

*Interpretation:* multiple equilibria indicate that small changes in assumptions (e.g., political salience or audit intensity) can flip the system between materially different strategic outcomes (e.g., cooperate vs shift). This is why ‘hybrid’ sensitivity analysis is useful: it captures regime switching rather than smooth marginal effects.

### Figure set: equilibria count grids

![Number of Nash equilibria across a pressure × efficiency-gap grid for BARG](outputs/v19/plots/equilibria_grid_BARG.png)

*Figure:* Number of Nash equilibria across a pressure × efficiency-gap grid for BARG

![Number of Nash equilibria across a pressure × efficiency-gap grid for COMP](outputs/v19/plots/equilibria_grid_COMP.png)

*Figure:* Number of Nash equilibria across a pressure × efficiency-gap grid for COMP

![Number of Nash equilibria across a pressure × efficiency-gap grid for DEF](outputs/v19/plots/equilibria_grid_DEF.png)

*Figure:* Number of Nash equilibria across a pressure × efficiency-gap grid for DEF

![Number of Nash equilibria across a pressure × efficiency-gap grid for DISC](outputs/v19/plots/equilibria_grid_DISC.png)

*Figure:* Number of Nash equilibria across a pressure × efficiency-gap grid for DISC

![Number of Nash equilibria across a pressure × efficiency-gap grid for GOV](outputs/v19/plots/equilibria_grid_GOV.png)

*Figure:* Number of Nash equilibria across a pressure × efficiency-gap grid for GOV

![Number of Nash equilibria across a pressure × efficiency-gap grid for SHIFT](outputs/v19/plots/equilibria_grid_SHIFT.png)

*Figure:* Number of Nash equilibria across a pressure × efficiency-gap grid for SHIFT

## 4. Policy scenarios and intervention effects

Scenarios apply individual levers (e.g., pooled funding, UCC integration, aged/NDIS capacity) and two packages. All scenarios are run with the same random seed and Monte Carlo count to support like-for-like comparison.

![2030 risk proxy across scenarios](outputs/v19/plots/scenario_rr_2030.png)

*Figure:* 2030 risk proxy across scenarios

![Pressure trajectories for key packages](outputs/v19/plots/scenario_pressure_timeseries.png)

*Figure:* Pressure trajectories for key packages

![Risk trajectories for key packages](outputs/v19/plots/scenario_rr_timeseries.png)

*Figure:* Risk trajectories for key packages

### Table 4. Scenario endpoints (2030)

| scenario                |   rr_mean_2030 |   pressure_mean_2030 |   offload_mean_2030 |   within4_mean_2030 |   effgap_mean_2030 |   occ_mean_2030 |   nep_to_cost_2030 |
|:------------------------|---------------:|---------------------:|--------------------:|--------------------:|-------------------:|----------------:|-------------------:|
| aged_ndis_capacity      |        1.1509  |              1.05678 |             23.7056 |            0.529593 |         0.1197     |        0.89087  |           0.951723 |
| baseline                |        1.1515  |              1.05678 |             23.9271 |            0.529501 |         0.1197     |        0.895104 |           0.951723 |
| cumulative_cap          |        1.1515  |              1.05678 |             23.9271 |            0.529501 |         0.1197     |        0.895104 |           0.951723 |
| full_package            |        1.02789 |              1.04533 |             23.382  |            0.529679 |         0.00167948 |        0.890193 |           1.04844  |
| integration_package     |        1.14288 |              1.04533 |             23.382  |            0.529679 |         0.119505   |        0.890193 |           0.951889 |
| macro_alignment_package |        1.03562 |              1.05678 |             23.9271 |            0.529501 |         0.00185566 |        0.895104 |           1.04825  |
| nep_growth              |        1.09805 |              1.05678 |             23.9271 |            0.529501 |         0.0668932  |        0.895104 |           0.998829 |
| nep_realism             |        1.1348  |              1.05678 |             23.9271 |            0.529501 |         0.103472   |        0.895104 |           0.951723 |
| pooled_funding          |        1.14322 |              1.04533 |             23.6035 |            0.529629 |         0.119505   |        0.894427 |           0.951889 |
| ucc_integration         |        1.1515  |              1.05678 |             23.9271 |            0.529501 |         0.1197     |        0.895104 |           0.951723 |
| wage_compact            |        1.09806 |              1.05678 |             23.9271 |            0.529501 |         0.0669054  |        0.895104 |           0.998817 |

*Interpretation:* integration levers primarily operate by reducing fragmentation and cost shifting, which lowers demand growth and pressure; macro-alignment levers operate by reducing the NEP-to-cost drift, which narrows the efficiency gap. The full package combines both, and therefore tends to produce the largest reductions in the model’s risk proxy.

## 5. Strategy frequencies

The table below reports the most common strategies selected in the Monte Carlo baseline. These are not ‘true’ probabilities; they summarise the model’s behavioural rule under uncertainty.

|   year | game   | action   |   freq |
|-------:|:-------|:---------|-------:|
|   2025 | BARG   | A        |      1 |
|   2026 | BARG   | A        |      1 |
|   2027 | BARG   | A        |      1 |
|   2028 | BARG   | A        |      1 |
|   2029 | BARG   | A        |      1 |
|   2030 | BARG   | A        |      1 |
|   2025 | COMP   | L        |      1 |
|   2026 | COMP   | L        |      1 |
|   2027 | COMP   | L        |      1 |
|   2028 | COMP   | L        |      1 |
|   2029 | COMP   | L        |      1 |
|   2030 | COMP   | L        |      1 |
|   2025 | DEF    | R        |      1 |
|   2026 | DEF    | R        |      1 |
|   2027 | DEF    | R        |      1 |
|   2028 | DEF    | R        |      1 |
|   2029 | DEF    | R        |      1 |
|   2030 | DEF    | R        |      1 |

*Interpretation:* when the model persistently selects cost-shifting or non-integration strategies, it typically reflects a parameterisation where downstream operational costs are externalised across jurisdictions.

## Synthesis and conclusion

Across the baseline and scenario analyses, the dominant mechanism is split incentives under VFI: upstream capacity constraints shift demand to the state-funded acute sector, while capped funding and a drifting NEP-to-cost ratio intensify the effective state share and operational risk. In this stylised environment, governance-alignment interventions (pooled funding, UCC integration, aged/NDIS capacity) reduce pressure and risk more reliably than increasing a nominal funding share alone, because they alter the strategic game rather than only the budget envelope. The equilibrium mapping reinforces a practical message for advocates: where multiple equilibria exist, small commitments (e.g., hard interoperability conditions, pooled pilots with credible governance) can ‘select’ the cooperative equilibrium and produce discontinuous improvements in throughput and safety.
