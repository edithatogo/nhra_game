# Models

## v8 hybrid model
The v8 hybrid model combines:
- valuation divergence (NEP vs actual)

**Note:** In IHACPA’s ABF architecture, the **NEP** is an annual **$ per NWAU** price. Payments are derived by applying NEP to **activity weights (NWAU)** (plus adjustments). In this repo, NEP is used mainly to frame the *efficient vs actual* cost debate; many simulations run on normalised indices (NEP=1).

- strategic games (bargain/define/cap/shift/govern/signal)
- patient-flow proxies (occupancy, offload, ED≤4h)
- a conservative harm index (comparative proxy only)

See: `src/nhra_game_theory/legacy_engine.py` and `scripts/run_v8_all.py`.
