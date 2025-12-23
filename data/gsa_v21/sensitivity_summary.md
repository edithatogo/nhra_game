# Global Sensitivity Analysis Summary (v21)

This report summarizes the findings from the Morris screening and Sobol variance decomposition.

## 1. Morris Screening (Influence & Non-linearity)
The Morris method identifies parameters with the greatest overall influence (mu_star) and those with non-linear or interactive effects (sigma).

|                         |    mu_star |       sigma |
|:------------------------|-----------:|------------:|
| fragmentation_index     | 0.038558   | 0.000981908 |
| discharge_delay_base    | 0.0263312  | 0.00812917  |
| admin_burden_weight     | 0.00229423 | 0.000165739 |
| rurality_weight         | 0.00140149 | 7.6759e-05  |
| cost_shifting_intensity | 0          | 0           |

## 2. Sobol Analysis (Variance Decomposition)
The Sobol method quantifies the percentage of output variance attributable to each parameter (S1) and its total effect including interactions (ST).

|    | Parameter               |         S1 |          ST |
|---:|:------------------------|-----------:|------------:|
|  2 | fragmentation_index     | 0.576689   | 0.592031    |
|  3 | discharge_delay_base    | 0.390717   | 0.335774    |
|  4 | admin_burden_weight     | 0.030455   | 0.00208197  |
|  0 | rurality_weight         | 0.00132255 | 0.000788106 |
|  1 | cost_shifting_intensity | 0          | 0           |

## 3. Key Findings
- **Primary Driver:** The most influential parameter in the system is **fragmentation_index**.
- **Interactions:** High sigma values in Morris or gaps between ST and S1 in Sobol indicate strong parameter interactions.
