# Methods Appendix: NHRA Game Theory Model (v21/22/23)

## 1. Model Structure
The model is a **Hybrid Agent-Based / System Dynamics** simulation with the following components:
- **Strategic Layer:** 6 concurrent Nash Equilibrium games (Bargaining, Definition, Cost Shifting, Discharge, Governance, Compliance).
- **Operational Layer:** System Dynamics mapping pressure to occupancy, offload delay, and ED performance.
- **Economic Spine:** Calibrated against historical NEP (IHACPA) and WPI (ABS) series.

## 2. Parameter Registry
All parameters are grounded in public evidence where possible.

| parameter                  | default                                                                      | evidence_source            |
|:---------------------------|:-----------------------------------------------------------------------------|:---------------------------|
| nep_to_cost_ratio_metro    | 0.90                                                                         | MODEL_DEFAULT / ASSUMPTION |
| nep_to_cost_ratio_regional | 0.83                                                                         | MODEL_DEFAULT / ASSUMPTION |
| nep_to_cost_ratio_remote   | 0.75                                                                         | MODEL_DEFAULT / ASSUMPTION |
| rurality_weight            | 0.35  # fraction of activity outside metro                                   | MODEL_DEFAULT / ASSUMPTION |
| remote_weight              | 0.07    # subset weight in remote                                            | MODEL_DEFAULT / ASSUMPTION |
| nominal_cth_share_target   | 0.45                                                                         | MODEL_DEFAULT / ASSUMPTION |
| effective_cth_share_base   | 0.38                                                                         | MODEL_DEFAULT / ASSUMPTION |
| cap_growth                 | 0.065  # "hard cap" annual                                                   | MODEL_DEFAULT / ASSUMPTION |
| has_cumulative_cap         | False                                                                        | MODEL_DEFAULT / ASSUMPTION |
| use_equilibrium_bargaining | False  # v14 option                                                          | MODEL_DEFAULT / ASSUMPTION |
| use_stage_game_equilibria  | True  # v15: solve and use all stage-game equilibria                         | MODEL_DEFAULT / ASSUMPTION |
| equilibrium_selection_rule | "payoff_dominant"  # payoff_dominant | row_favourable | random               | MODEL_DEFAULT / ASSUMPTION |
| nep_per_nwau_start         | 1.0  # index units; set to actual $/NWAU if desired                          | MODEL_DEFAULT / ASSUMPTION |
| nep_annual_growth          | 0.03                                                                         | MODEL_DEFAULT / ASSUMPTION |
| representative_nwau        | 1.0  # a single representative activity weight for illustrative calculations | MODEL_DEFAULT / ASSUMPTION |
| input_cost_per_nwau_start  | 1.0                                                                          | MODEL_DEFAULT / ASSUMPTION |
| input_cost_annual_growth   | 0.04                                                                         | MODEL_DEFAULT / ASSUMPTION |
| demand_base                | 1.00                                                                         | MODEL_DEFAULT / ASSUMPTION |
| avoidable_ed_share         | 0.18                                                                         | MODEL_DEFAULT / ASSUMPTION |
| discharge_delay_base       | 1.00  # multiplier                                                           | MODEL_DEFAULT / ASSUMPTION |
| bed_capacity_index         | 1.00    # 1.0 baseline                                                       | MODEL_DEFAULT / ASSUMPTION |
| cost_shifting_intensity    | 0.35  # VFI spillover strength                                               | MODEL_DEFAULT / ASSUMPTION |
| fragmentation_index        | 1.00      # UCC/primary care integration etc                                 | MODEL_DEFAULT / ASSUMPTION |
| audit_pressure             | 0.50           # compliance scrutiny baseline                                | MODEL_DEFAULT / ASSUMPTION |
| admin_burden_weight        | 0.25                                                                         | MODEL_DEFAULT / ASSUMPTION |
| occupancy_base             | 0.88                                                                         | MODEL_DEFAULT / ASSUMPTION |
| offload_base_min           | 18.0  # minutes                                                              | MODEL_DEFAULT / ASSUMPTION |
| within4_base               | 0.53                                                                         | MODEL_DEFAULT / ASSUMPTION |
| rr_beta_pressure           | 0.35                                                                         | MODEL_DEFAULT / ASSUMPTION |
| rr_beta_offload            | 0.015  # per minute above threshold (stylised)                               | MODEL_DEFAULT / ASSUMPTION |
| offload_threshold_min      | 20.0                                                                         | MODEL_DEFAULT / ASSUMPTION |
| tau                        | 0.25  # softmax temperature                                                  | MODEL_DEFAULT / ASSUMPTION |
| bargaining_cost            | 0.12                                                                         | MODEL_DEFAULT / ASSUMPTION |
| political_salience         | 0.30                                                                         | MODEL_DEFAULT / ASSUMPTION |
| noise_sd                   | 0.03                                                                         | MODEL_DEFAULT / ASSUMPTION |

## 3. Equations
### Pressure Index
$$ P_t = 0.8 + 0.8 	imes (0.55 \cdot \sigma(Occ_t) + 0.45 \cdot \sigma(Off_t)) 	imes D_t $$
Where $\sigma$ is a logistic sigmoid function, $Occ_t$ is occupancy, $Off_t$ is offload delay, and $D_t$ is discharge delay.

### Effective Share Drift
$$ Share_{eff} = Share_{nom} 	imes rac{1}{1 + Gap_t} $
Where $Gap_t$ drifts based on the divergence between Input Cost Growth (WPI) and Efficient Price Indexation (NEP).