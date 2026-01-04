# Parameter glossary (stylised)

This glossary describes the **interpretation** of parameters used in the MPE extensions (V7.2/V8).  
Values are *anchors for mechanism exploration* (not estimates).

| Symbol / name | Meaning | Directional effect |
|---|---|---|
| `x` | System pressure / congestion proxy | Higher `x` → lower ED≤4h proxy |
| `g` | Valuation gap (NEP vs actual cost proxy) | Higher `g` amplifies upstream pressure injection |
| `c` | Capacity / slack (slow-moving) | Higher `c` → better ED proxy; enables higher feasible Commonwealth effort under cap |
| `S0` | Upstream pressure injection baseline | Higher `S0` increases pressure |
| `beta` | Responsiveness of injection to Commonwealth effort `u` | Higher `beta` makes `u` more effective in reducing injection |
| `phi_g` | Gap amplification of injection | Higher `phi_g` strengthens cost/valuation gap → pressure coupling |
| `rho` | Persistence of pressure (`x`) | Higher `rho` = more inertia |
| `sigma_x` | Unmodelled shocks to pressure | Higher `sigma_x` = more volatility |
| `mu_g` | Persistence of gap (`g`) | Higher `mu_g` = slower gap mean-reversion |
| `spill_g` | Spillover from pressure to gap | Higher = congestion worsens cost divergence |
| `k_r` | “Realism” action effectiveness at reducing gap | Higher = faster reduction in `g` for given `r` |
| `k_a` | State mitigation effectiveness | Higher = stronger pressure reduction via `a` |
| `eta_a`, `eta_u` | Capacity build rates | Higher = actions create slack/capacity faster |
| `dep0`, `dep_x` | Capacity depreciation | Higher = slack erodes faster (baseline and under pressure) |
| `treasury_cap` | Feasibility constraint linking effort to slack | If on: low `c` limits max `u` |

## Outcome mapping

We use an ED≤4h **proxy**:

- V7.2: `ED = clamp(0.67 - γ x, 0, 1)`
- V8: `ED = clamp(0.67 - γ x - λ(1-c), 0, 1)`

Anchoring: γ is chosen so that `x≈0.10` corresponds to 0.53 (stylised 2024–25 level).
