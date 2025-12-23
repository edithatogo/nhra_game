# NHRA Model Technical Validation Report
**Date:** 2025-12-24 05:49:09

## 1. Executive Summary
Model Status: **STABLE**

## 2. Recursive Backtesting Metrics (2011–2024)
| Metric | RMSE | MAPE | Theil U | Hit Rate |
| :--- | :--- | :--- | :--- | :--- |
| within4 | 0.115 | 15.6% | 0.099 | 0.000 |
| occupancy | 0.023 | 2.1% | 0.013 | 0.000 |

## 3. Error Decomposition (Theil)
![Theil Decomposition](../outputs/validation/theil_decomposition.png)

## 4. Mechanism Integrity (GSA)
Top mechanistic driver (mu_star): **fragmentation_index**

| Parameter | mu_star | Rank |
| :--- | :--- | :--- |
| fragmentation_index | 0.0386 | 1 |
| discharge_delay_base | 0.0263 | 2 |
| admin_burden_weight | 0.0023 | 3 |
| rurality_weight | 0.0014 | 4 |
| cost_shifting_intensity | 0.0000 | 5 |
| political_salience | 0.0000 | 5 |

## 5. Compliance Notes
- [x] STRESS Guidelines: Model structure and equations documented.
- [x] CHEERS Checklist: Economic parameters sourced from AIHW/ABS.
- [ ] Peer Review: Pending.