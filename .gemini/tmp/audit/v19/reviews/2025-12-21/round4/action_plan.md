# Round 4 peer-review simulation (v19)

Date: 2025-12-21

## Action plan implemented in v19

1. **NEP/NWAU interpretation strengthened**
   - Report explicitly states payment = NEP × NWAU and treats NEP and costs as indices for incentive dynamics (not a claim about any DRG dollar value).

2. **Equilibria fully enumerated and reported**
   - New v19 pipeline produces `equilibria_by_year.csv` and per-game equilibrium grids; report includes tables and heatmaps.

3. **Scenario framing improved**
   - Adds “integration”, “macro alignment”, and “full” packages; adds time-series overlays and 2030 endpoint comparisons.

4. **Dynamic / interactive visualisation**
   - Adds `nhra_game_network_v19.html` driven by scenario time-series outputs (scenario and year controls).

5. **Packaging and CI quality polish**
   - Adds Hatch environment definitions to complement existing tooling and provide a clean entry-point for reproducible runs in external environments.

### Remaining future work (explicitly out-of-scope for v19)
- Optional integration of IHACPA classification calculators as a plug-in module.
- Formal optimisation (e.g., Optuna) as a policy design tool once objective functions and constraints are specified.
