# System Dynamics & Pressure

The operational layer of the NHRA Game maps strategic choices and demand shocks to hospital performance.

## 1. Pressure Index

The System Pressure Index ($P$) is a non-dimensional metric of operational strain:

$$
P = 0.8 + 0.2 \left( \frac{W_{wait}}{60} \right) + 0.5 \left( \frac{O - 0.8}{0.1} \right)
$$

Where:
- $O$: Occupancy rate.
- $W_{wait}$: Queue wait time.

## 2. Capacity Lags

Capacity does not adjust instantaneously. We model operational inertia using expansion/contraction lags:

$$
C_{t+1} = C_t + \lambda (C_{target} - C_t)
$$

Where:
- $\lambda$: Lag coefficient (Expansion $\lambda_{exp}$ < Contraction $\lambda_{con}$).

## 3. System Modes

The model operates as a state machine with four modes:
- **Normal:** Pressure < 1.25
- **Stress:** 1.25 < Pressure < 1.50
- **Crisis:** Pressure > 1.50
- **Recovery:** Transitioning back to Normal.

## 4. Evidence Grounding
- **Occupancy:** AIHW 88% efficient threshold.
- **Lags:** Stylised based on hiring and infrastructure cycles.
