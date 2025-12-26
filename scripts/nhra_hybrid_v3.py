import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

"""
NHRA Hybrid Simulation (V3): Externality game + Flow pressure generator
---------------------------------------------------------------------
Incremental combination:
  - Model 1 (externality/cost-shifting) determines upstream effort u_t and acute effort a_t
    via myopic best-responses each period.
  - Model 5 (flow) converts these choices into occupancy and a pressure index.

Interpretation:
  u_t: Commonwealth-controlled upstream levers that reduce spillover demand into hospital
  a_t: State-controlled acute/subacute/discharge levers that increase discharge capacity

Run:
  python nhra_hybrid_v3.py
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

np.random.seed(42)
OUTDIR="."

# Representative facility scale
K = 100
ALOS_EFFECTIVE = 3.2
base_arrivals = 0.90 * (K / ALOS_EFFECTIVE)   # ~28/day
base_arrivals = float(base_arrivals)

# Spillover demand component (e.g., aged care / primary care constraints)
spillover = 8.0

# Decision grids
u_grid = np.linspace(0, 20, 81)   # upstream effort
a_grid = np.linspace(0, 15, 61)   # acute effort

# Effort costs
cu = 0.12
ca = 0.15

# How decisions influence arrivals/discharges
beta_u = 0.12      # marginal effect of u on spillover arrivals (exp decay)
k_a = 1.0          # how much discharge capacity increases per unit a

# Pressure weighting (utility importance)
wC = 1.0
wS = 4.0

T = 180  # days
rng = np.random.default_rng(42)

def pressure_index_from_occupancy(N, K):
    return max(0.0, (N / K) - 1.0)

def arrivals(u):
    return base_arrivals + spillover * np.exp(-beta_u*u)

def discharge_cap(a):
    return max(0.0, (base_arrivals + spillover) + k_a*a)  # generous baseline, stress-test by reducing baseline

def payoff_C(u, p_idx):
    return -(wC*p_idx) - 0.5*cu*(u**2)

def payoff_S(a, p_idx):
    return -(wS*p_idx) - 0.5*ca*(a**2)

# State variables
N = np.zeros(T+1)      # occupancy
P = np.zeros(T+1)      # pressure index
u_t = np.zeros(T+1)
a_t = np.zeros(T+1)

N[0] = 0.95*K

for t in range(T):
    # Myopic best-responses to last period pressure (simple behavioural rule)
    # State chooses a to reduce pressure; Commonwealth chooses u similarly.
    # In richer versions, each anticipates how choice affects next state.
    p_last = P[t]

    # Best response for a (State): choose a maximizing payoff_S given p_last (myopic)
    vals_a = np.array([payoff_S(a, p_last) for a in a_grid])
    a_choice = float(a_grid[int(np.argmax(vals_a))])

    # Best response for u (Commonwealth): choose u maximizing payoff_C given p_last (myopic)
    vals_u = np.array([payoff_C(u, p_last) for u in u_grid])
    u_choice = float(u_grid[int(np.argmax(vals_u))])

    u_t[t] = u_choice
    a_t[t] = a_choice

    # Realise arrivals/discharges
    A = rng.poisson(arrivals(u_choice))
    d = discharge_cap(a_choice)
    D = min(N[t], d)

    # Update occupancy and pressure
    N[t+1] = max(0.0, N[t] + A - D)
    P[t+1] = pressure_index_from_occupancy(N[t+1], K)

# Plots
plt.figure()
plt.plot(N, label="Occupancy N_t")
plt.axhline(K, linestyle="--", label="Capacity K")
plt.xlabel("Time (days)")
plt.ylabel("Beds occupied")
plt.title("V3 Hybrid: Occupancy trajectory (externality choices drive flow)")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/v3_hybrid_occupancy.png", dpi=220)

plt.figure()
plt.plot(P, label="Pressure index P_t")
plt.xlabel("Time (days)")
plt.ylabel("Excess occupancy ratio")
plt.title("V3 Hybrid: Pressure index trajectory")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/v3_hybrid_pressure.png", dpi=220)

plt.figure()
plt.plot(u_t, label="Commonwealth effort u_t")
plt.plot(a_t, label="State effort a_t")
plt.xlabel("Time (days)")
plt.ylabel("Effort level")
plt.title("V3 Hybrid: Myopic efforts over time")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/v3_hybrid_efforts.png", dpi=220)

# Summary table
df = pd.DataFrame({
    "t": np.arange(T+1),
    "N": N,
    "P": P,
    "u": u_t,
    "a": a_t
})
df.to_csv(f"{OUTDIR}/v3_hybrid_timeseries.csv", index=False)
print("Saved plots + v3_hybrid_timeseries.csv to OUTDIR:", OUTDIR)
