"""
NHRA Hybrid Simulation (V4): V3 + Signalling + Bargaining + Valuation gap
------------------------------------------------------------------------
Incremental combination (adds two channels):
  - Signalling: higher pressure raises probability of "anchoring rhetoric" (Model 4)
  - Bargaining: anchoring and outside options reduce agreement probability (Model 3 logic)
  - Valuation gap: g_t evolves; higher gap increases effective state burden (Model 2 logic)

This is a stylised dynamical system intended for *insight + sensitivity analysis*, not prediction.

Run:
  python nhra_hybrid_v4.py
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

np.random.seed(42)
OUTDIR="."

# ---------------------------
# Anchors (public metrics used as scaling in V2)
# ---------------------------
NEP_PER_NWAU_2024_25 = 6465.0
HIP_REPLACEMENT_NWAU = 4.0954
E = NEP_PER_NWAU_2024_25 * HIP_REPLACEMENT_NWAU  # ~26,477

ED_WITHIN_4H_2024_25 = 0.53
ED_WITHIN_4H_2020_21 = 0.67
GAMMA_WITHIN4_PER_PRESSURE = (ED_WITHIN_4H_2020_21 - ED_WITHIN_4H_2024_25) / 0.10  # ≈1.4

# Schedule K scaling (outside option)
SCHEDULE_K_ONEOFF = 1.7e9
NHFB_ENTITLEMENT_EST = 32.2e9
O_base = SCHEDULE_K_ONEOFF / NHFB_ENTITLEMENT_EST  # ~0.053

# ---------------------------
# Facility scale + flow dynamics
# ---------------------------
K = 100
ALOS_EFFECTIVE = 3.2
base_arrivals = float(0.90*(K/ALOS_EFFECTIVE))  # ~28/day
spillover = 8.0

beta_u = 0.12
k_a = 0.8

T = 220
rng = np.random.default_rng(42)

def pressure_index(N, K):
    return max(0.0, (N/K) - 1.0)

def within4_proxy(p_idx):
    return float(np.clip(ED_WITHIN_4H_2020_21 - GAMMA_WITHIN4_PER_PRESSURE*p_idx, 0.0, 1.0))

def arrivals(u):
    return base_arrivals + spillover*np.exp(-beta_u*u)

def discharge_cap(a):
    # baseline discharge matches expected arrivals at u=0 (stress-test by multiplying by <1)
    return max(0.0, (base_arrivals + spillover) + k_a*a)

# ---------------------------
# Externality payoffs (myopic decision rule, as in V3)
# ---------------------------
u_grid = np.linspace(0, 20, 81)
a_grid = np.linspace(0, 15, 61)
cu = 0.12
ca = 0.15

# Valuation gap dynamics (Model 2)
g0 = 6000.0
i_realism = 0.20
eps = rng.normal(150, 100, size=T)  # drift/noise

def effective_share(alpha_nom, g):
    return (alpha_nom*E)/(E+g)

alpha_nom = 0.45  # nominal target
# Map gap to "state burden factor"
def state_burden_factor(g):
    # higher gap -> lower effective share -> higher state burden
    a_eff = effective_share(alpha_nom, g)
    return float((1.0 - a_eff) / (1.0 - alpha_nom + 1e-9))

# Signalling: Pr(anchor) increases with pressure (Model 4-style logistic)
k_sig = 25.0
p0_sig = 0.06  # ~6% excess occupancy triggers more anchoring
def pr_anchor(p_idx):
    return float(1.0/(1.0 + np.exp(-k_sig*(p_idx - p0_sig))))

# Bargaining: agreement probability falls as outside option grows and anchor occurs
def pr_agreement(O, anchor):
    # baseline agreement probability is high; anchoring reduces it
    base = 0.85 - 1.6*O
    if anchor:
        base -= 0.25
    return float(np.clip(base, 0.0, 1.0))

# Pressure weights
wC = 1.0
wS_base = 4.0

def payoff_C(u, p_idx):
    return -(wC*p_idx) - 0.5*cu*(u**2)

def payoff_S(a, p_idx, g):
    wS = wS_base * state_burden_factor(g)
    return -(wS*p_idx) - 0.5*ca*(a**2)

# ---------------------------
# Simulate
# ---------------------------
N = np.zeros(T+1); P = np.zeros(T+1)
u_t = np.zeros(T+1); a_t = np.zeros(T+1)
g_t = np.zeros(T+1); g_t[0]=g0
anchor_t = np.zeros(T+1)  # 0/1
agree_p = np.zeros(T+1)
within4 = np.zeros(T+1)

N[0]=0.95*K

for t in range(T):
    # update valuation gap
    g_t[t+1] = max(0.0, (1-i_realism)*g_t[t] + eps[t])

    # signalling draw (based on current pressure)
    pa = pr_anchor(P[t])
    anchor = (rng.random() < pa)
    anchor_t[t] = 1.0 if anchor else 0.0

    # outside option varies with anchoring (stylised: rhetoric hardens positions, raises perceived O)
    O = O_base + (0.03 if anchor else 0.0)
    agree_p[t] = pr_agreement(O, anchor)

    # myopic best-responses (as in V3, but state weight depends on g_t)
    vals_a = np.array([payoff_S(a, P[t], g_t[t]) for a in a_grid])
    a_choice = float(a_grid[int(np.argmax(vals_a))])
    vals_u = np.array([payoff_C(u, P[t]) for u in u_grid])
    u_choice = float(u_grid[int(np.argmax(vals_u))])

    u_t[t]=u_choice; a_t[t]=a_choice

    # Realise arrivals/discharges
    A = rng.poisson(arrivals(u_choice))
    d = discharge_cap(a_choice)
    D = min(N[t], d)
    N[t+1] = max(0.0, N[t] + A - D)
    P[t+1] = pressure_index(N[t+1], K)
    within4[t+1] = within4_proxy(P[t+1])

# ---------------------------
# Plots
# ---------------------------
plt.figure()
plt.plot(P, label="Pressure index")
plt.plot(anchor_t, label="Anchor (0/1)")
plt.xlabel("Time (days)")
plt.title("V4 Hybrid: Pressure and signalling")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/v4_pressure_signalling.png", dpi=220)

plt.figure()
plt.plot(g_t, label="Valuation gap g_t ($)")
plt.xlabel("Time (days)")
plt.title("V4 Hybrid: Valuation gap dynamics")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/v4_gap_dynamics.png", dpi=220)

plt.figure()
plt.plot(within4, label="ED within-4h proxy")
plt.axhline(ED_WITHIN_4H_2024_25, linestyle="--", label="AIHW 2024–25 (0.53)")
plt.xlabel("Time (days)")
plt.title("V4 Hybrid: ED within-4h proxy implied by pressure")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/v4_within4_proxy.png", dpi=220)

plt.figure()
plt.plot(agree_p, label="Pr(agreement)")
plt.xlabel("Time (days)")
plt.title("V4 Hybrid: Agreement probability (outside option + signalling)")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/v4_agreement_probability.png", dpi=220)

# Outputs
df = pd.DataFrame({
    "t": np.arange(T+1),
    "N": N,
    "P": P,
    "within4_proxy": within4,
    "u": u_t,
    "a": a_t,
    "g": g_t,
    "anchor": anchor_t,
    "p_agree": agree_p
})
df.to_csv(f"{OUTDIR}/v4_hybrid_timeseries.csv", index=False)
print("Saved plots + v4_hybrid_timeseries.csv to OUTDIR:", OUTDIR)
