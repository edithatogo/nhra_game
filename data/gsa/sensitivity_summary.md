# Global Sensitivity Analysis Summary (v21)

This report summarizes the findings from the Morris screening and Sobol variance decomposition.

## 1. Morris Screening (Influence & Non-linearity)

The Morris method identifies parameters with the greatest overall influence (mu_star) and those with non-linear or interactive effects (sigma).

|                         |   mu_star |     sigma |
|:------------------------|----------:|----------:|
| discharge_delay_base    | 0.0559439 | 0.0589701 |
| rurality_weight         | 0         | 0         |
| cost_shifting_intensity | 0         | 0         |
| fragmentation_index     | 0         | 0         |
| admin_burden_weight     | 0         | 0         |

## 2. Sobol Analysis (Variance Decomposition)

The Sobol method quantifies the percentage of output variance attributable to each parameter (S1) and its total effect including interactions (ST).

|    | Parameter               |      S1 |      ST |
|---:|:------------------------|--------:|--------:|
|  3 | discharge_delay_base    | 1.04963 | 1.04963 |
|  0 | rurality_weight         | 0       | 0       |
|  1 | cost_shifting_intensity | 0       | 0       |
|  2 | fragmentation_index     | 0       | 0       |
|  4 | admin_burden_weight     | 0       | 0       |

## 3. Key Findings

- **Primary Driver:** The most influential parameter in the system is **discharge_delay_base**.
- **Interactions:** High sigma values in Morris or gaps between ST and S1 in Sobol indicate strong parameter interactions.
