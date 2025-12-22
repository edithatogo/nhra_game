# Model overview

## What the models are
These models are **stylised mechanism models** that combine:
- a **system dynamics backbone** (pressure → occupancy/offload/ED≤4h), and
- a layer of interacting **stage games** (bargaining/definition/cost-shifting/discharge/governance/compliance/signalling).

They are designed for *scenario comparison* and *mechanism explanation*.

## What the models are not
- Not a forecast, not an econometric model, not a clinical-outcomes model.
- Not suitable for estimating real-world morbidity/mortality.

## Core state variables
- **Pressure (index):** composite of demand, discharge delay, and valuation divergence.
- **Occupancy:** proxy for access block.
- **Ambulance offload minutes:** proxy for ED access block.
- **ED≤4h:** throughput proxy.
- **Risk proxy:** comparative index derived from pressure/offload/ED≤4h.

## Parameterisation philosophy
All parameters must be either:
1) backed by a **publicly retrievable source**, or
2) explicitly labelled as an **assumption/calibration**, with a written rationale and a plausible range for sensitivity analysis.

The canonical record is `context/04_parameter_registry.csv`.
