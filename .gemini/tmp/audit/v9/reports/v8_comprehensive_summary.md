# NHRA game-theory model v8 — comprehensive summary

**Date:** 2025-12-20  
**Version:** v0.8.0  

## Abbreviations
- **NHRA**: National Health Reform Agreement
- **NEP**: National Efficient Price
- **VFI**: Vertical Fiscal Imbalance
- **UCC**: Medicare Urgent Care Clinic
- **RR proxy**: Relative risk proxy (stress indicator only; not a mortality estimate)

## Tables
### bundle_waterfall
*Caption:* Model output table `bundle_waterfall.csv` (CSV).
- File: [bundle_waterfall.csv](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/tables/bundle_waterfall.csv)

### games_centrality
*Caption:* Model output table `games_centrality.csv` (CSV).
- File: [games_centrality.csv](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/tables/games_centrality.csv)

### scenario_deltas_vs_baseline
*Caption:* Model output table `scenario_deltas_vs_baseline.csv` (CSV).
- File: [scenario_deltas_vs_baseline.csv](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/tables/scenario_deltas_vs_baseline.csv)

### scenario_summary
*Caption:* Model output table `scenario_summary.csv` (CSV).
- File: [scenario_summary.csv](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/tables/scenario_summary.csv)

### sensitivity_samples
*Caption:* Model output table `sensitivity_samples.csv` (CSV).
- File: [sensitivity_samples.csv](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/tables/sensitivity_samples.csv)

### strategy_freq_baseline
*Caption:* Model output table `strategy_freq_baseline.csv` (CSV).
- File: [strategy_freq_baseline.csv](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/tables/strategy_freq_baseline.csv)

### strategy_freq_bundle_all
*Caption:* Model output table `strategy_freq_bundle_all.csv` (CSV).
- File: [strategy_freq_bundle_all.csv](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/tables/strategy_freq_bundle_all.csv)

### strategy_freq_discharge_capacity
*Caption:* Model output table `strategy_freq_discharge_capacity.csv` (CSV).
- File: [strategy_freq_discharge_capacity.csv](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/tables/strategy_freq_discharge_capacity.csv)

### strategy_freq_nep_realism
*Caption:* Model output table `strategy_freq_nep_realism.csv` (CSV).
- File: [strategy_freq_nep_realism.csv](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/tables/strategy_freq_nep_realism.csv)

### strategy_freq_pooled_funding
*Caption:* Model output table `strategy_freq_pooled_funding.csv` (CSV).
- File: [strategy_freq_pooled_funding.csv](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/tables/strategy_freq_pooled_funding.csv)

### strategy_freq_ucc_integration
*Caption:* Model output table `strategy_freq_ucc_integration.csv` (CSV).
- File: [strategy_freq_ucc_integration.csv](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/tables/strategy_freq_ucc_integration.csv)

### trajectory_baseline
*Caption:* Model output table `trajectory_baseline.csv` (CSV).
- File: [trajectory_baseline.csv](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/tables/trajectory_baseline.csv)

### trajectory_bundle_all
*Caption:* Model output table `trajectory_bundle_all.csv` (CSV).
- File: [trajectory_bundle_all.csv](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/tables/trajectory_bundle_all.csv)

### trajectory_discharge_capacity
*Caption:* Model output table `trajectory_discharge_capacity.csv` (CSV).
- File: [trajectory_discharge_capacity.csv](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/tables/trajectory_discharge_capacity.csv)

### trajectory_nep_realism
*Caption:* Model output table `trajectory_nep_realism.csv` (CSV).
- File: [trajectory_nep_realism.csv](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/tables/trajectory_nep_realism.csv)

### trajectory_pooled_funding
*Caption:* Model output table `trajectory_pooled_funding.csv` (CSV).
- File: [trajectory_pooled_funding.csv](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/tables/trajectory_pooled_funding.csv)

### trajectory_ucc_integration
*Caption:* Model output table `trajectory_ucc_integration.csv` (CSV).
- File: [trajectory_ucc_integration.csv](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/tables/trajectory_ucc_integration.csv)

## Figures
### baseline_offload
*Caption:* Ambulance offload time trajectory (minutes; mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/baseline_offload.png)

### baseline_pressure
*Caption:* Pressure index trajectory (mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/baseline_pressure.png)

### baseline_rr_proxy
*Caption:* Relative risk proxy trajectory (stress indicator).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/baseline_rr_proxy.png)

### baseline_strategies
*Caption:* Strategy share over time by game node.
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/baseline_strategies.png)

### baseline_within4
*Caption:* ED within-4-hours trajectory (share; mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/baseline_within4.png)

### bundle_all_offload
*Caption:* Ambulance offload time trajectory (minutes; mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/bundle_all_offload.png)

### bundle_all_pressure
*Caption:* Pressure index trajectory (mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/bundle_all_pressure.png)

### bundle_all_rr_proxy
*Caption:* Relative risk proxy trajectory (stress indicator).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/bundle_all_rr_proxy.png)

### bundle_all_strategies
*Caption:* Strategy share over time by game node.
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/bundle_all_strategies.png)

### bundle_all_within4
*Caption:* ED within-4-hours trajectory (share; mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/bundle_all_within4.png)

### bundle_waterfall_within4
*Caption:* ED within-4-hours trajectory (share; mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/bundle_waterfall_within4.png)

### discharge_capacity_offload
*Caption:* Ambulance offload time trajectory (minutes; mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/discharge_capacity_offload.png)

### discharge_capacity_pressure
*Caption:* Pressure index trajectory (mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/discharge_capacity_pressure.png)

### discharge_capacity_rr_proxy
*Caption:* Relative risk proxy trajectory (stress indicator).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/discharge_capacity_rr_proxy.png)

### discharge_capacity_within4
*Caption:* ED within-4-hours trajectory (share; mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/discharge_capacity_within4.png)

### games_centrality
*Caption:* Game-network betweenness centrality (which nodes sit on influence pathways).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/games_centrality.png)

### nep_realism_offload
*Caption:* Ambulance offload time trajectory (minutes; mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/nep_realism_offload.png)

### nep_realism_pressure
*Caption:* Pressure index trajectory (mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/nep_realism_pressure.png)

### nep_realism_rr_proxy
*Caption:* Relative risk proxy trajectory (stress indicator).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/nep_realism_rr_proxy.png)

### nep_realism_within4
*Caption:* ED within-4-hours trajectory (share; mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/nep_realism_within4.png)

### pd_cost_shifting_intensity_within4
*Caption:* ED within-4-hours trajectory (share; mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/pd_cost_shifting_intensity_within4.png)

### pd_discharge_delay_base_within4
*Caption:* ED within-4-hours trajectory (share; mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/pd_discharge_delay_base_within4.png)

### pd_fragmentation_index_within4
*Caption:* ED within-4-hours trajectory (share; mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/pd_fragmentation_index_within4.png)

### pooled_funding_offload
*Caption:* Ambulance offload time trajectory (minutes; mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/pooled_funding_offload.png)

### pooled_funding_pressure
*Caption:* Pressure index trajectory (mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/pooled_funding_pressure.png)

### pooled_funding_rr_proxy
*Caption:* Relative risk proxy trajectory (stress indicator).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/pooled_funding_rr_proxy.png)

### pooled_funding_within4
*Caption:* ED within-4-hours trajectory (share; mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/pooled_funding_within4.png)

### scenario_deltas
*Caption:* Scenario deltas vs baseline (2030), with scaled offload improvement.
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/scenario_deltas.png)

### tornado_effgap_2030
*Caption:* Sensitivity tornado (Spearman rank correlation with 2030 outcome).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/tornado_effgap_2030.png)

### tornado_effshare_effective_2030
*Caption:* Sensitivity tornado (Spearman rank correlation with 2030 outcome).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/tornado_effshare_effective_2030.png)

### tornado_offload_2030
*Caption:* Ambulance offload time trajectory (minutes; mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/tornado_offload_2030.png)

### tornado_pressure_2030
*Caption:* Pressure index trajectory (mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/tornado_pressure_2030.png)

### tornado_rr_2030
*Caption:* Sensitivity tornado (Spearman rank correlation with 2030 outcome).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/tornado_rr_2030.png)

### tornado_within4_2030
*Caption:* ED within-4-hours trajectory (share; mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/tornado_within4_2030.png)

### tradeoff_scatter
*Caption:* Scenario trade-off: effective share vs within4; bubble size approximates pressure.
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/tradeoff_scatter.png)

### ucc_integration_offload
*Caption:* Ambulance offload time trajectory (minutes; mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/ucc_integration_offload.png)

### ucc_integration_pressure
*Caption:* Pressure index trajectory (mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/ucc_integration_pressure.png)

### ucc_integration_rr_proxy
*Caption:* Relative risk proxy trajectory (stress indicator).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/ucc_integration_rr_proxy.png)

### ucc_integration_within4
*Caption:* ED within-4-hours trajectory (share; mean with 10–90% band).
![](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/plots/ucc_integration_within4.png)

## Interactive diagram
- Games network (interactive HTML): [games_network_interactive.html](sandbox:/mnt/data/nhra_game_theory_repo_v8_20251220/outputs/v8/interactive/games_network_interactive.html)

## Mermaid and Graphviz sources
- Your uploaded Mermaid sources are in `diagrams/mermaid_user/` inside the repo zip.
- Existing Graphviz exports are included under `outputs/v8/`.