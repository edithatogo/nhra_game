"""
NHRA Hybrid Simulation (V5): V4 + Integration (Model 6) + Audit-Burden Feedback (Model 7)
---------------------------------------------------------------------------------------
Incremental combination:
  - Adds an "integration state" (I/S) that affects spillover and boundary-risk costs.
  - Adds an audit/burden variable B_t that can reduce effective throughput (e.g., via admin friction),
    creating a reinforcing loop under pressure.

This remains a stylised sensitivity-analysis engine.

Run:
  python nhra_hybrid_v5.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

np.random.seed(42)
OUTDIR="."

# ---------------------------
# Anchors (for scale)
# ---------------------------
NEP_PER_NWAU_2024_25 = 6465.0
HIP_REPLACEMENT_NWAU = 4.0954
E = NEP_PER_NWAU_2024_25 * HIP_REPLACEMENT_NWAU

ED_WITHIN_4H_2024_25 = 0.53
ED_WITHIN_4H_2020_21 = 0.67
GAMMA_WITHIN4_PER_PRESSURE = (ED_WITHIN_4H_2020_21 - ED_WITHIN_4H_2024_25) / 0.10

SCHEDULE_K_ONEOFF = 1.7e9
NHFB_ENTITLEMENT_EST = 32.2e9
O_base = SCHEDULE_K_ONEOFF / NHFB_ENTITLEMENT_EST

# UCC handover metrics (stylised risk)
UCC_HANDOVER_ANY = 0.89
UCC_ELECTRONIC_SUMMARY_TO_GP = 0.68
h_sep = 1.0 - UCC_ELECTRONIC_SUMMARY_TO_GP  # ~0.32
h_int = 1.0 - UCC_HANDOVER_ANY              # ~0.11

# ---------------------------
# Facility scale + flow
# ---------------------------
K = 100
ALOS_EFFECTIVE = 3.2
base_arrivals = float(0.90*(K/ALOS_EFFECTIVE))
spillover_base = 8.0

beta_u = 0.12
k_a = 0.8

T = 240
rng = np.random.default_rng(42)

def pressure_index(N, K):
    return max(0.0, (N/K) - 1.0)

def within4_proxy(p_idx):
    return float(np.clip(ED_WITHIN_4H_2020_21 - GAMMA_WITHIN4_PER_PRESSURE*p_idx, 0.0, 1.0))

# ---------------------------
# Valuation gap
# ---------------------------
g0 = 6000.0
i_realism = 0.20
eps = rng.normal(150, 100, size=T)

alpha_nom = 0.45

def effective_share(alpha_nom, g):
    return (alpha_nom*E)/(E+g)

def state_burden_factor(g):
    a_eff = effective_share(alpha_nom, g)
    return float((1.0 - a_eff) / (1.0 - alpha_nom + 1e-9))

# ---------------------------
# Signalling and bargaining
# ---------------------------
k_sig = 25.0
p0_sig = 0.06
def pr_anchor(p_idx):
    return float(1.0/(1.0 + np.exp(-k_sig*(p_idx - p0_sig))))

def pr_agreement(O, anchor):
    base = 0.85 - 1.6*O
    if anchor:
        base -= 0.25
    return float(np.clip(base, 0.0, 1.0))

# ---------------------------
# Integration game (Model 6)
# ---------------------------
acts = ["I", "S"]
cU, cH = 1.0, 1.0
L = 10.0
shareU = 0.30

def payoffs(cond_penalty=0.0, cond_subsidy=0.0):
    def f(Uact, Hact):
        if Uact=="I" and Hact=="I":
            risk = h_int * L
            U = -(cU) - shareU*risk + cond_subsidy
            H = -(cH) - (1-shareU)*risk
        elif Uact=="I" and Hact=="S":
            risk = h_sep * L
            U = -(cU) - shareU*risk + cond_subsidy
            H = -0.0 - (1-shareU)*risk
        elif Uact=="S" and Hact=="I":
            risk = h_sep * L
            U = -0.0 - shareU*risk - cond_penalty
            H = -(cH) - (1-shareU)*risk
        else:
            risk = h_sep * L
            U = -0.0 - shareU*risk - cond_penalty
            H = -0.0 - (1-shareU)*risk
        return U, H
    return f

def payoff_matrices(f):
    Umat = np.zeros((2,2)); Hmat = np.zeros((2,2))
    for i, ua in enumerate(acts):
        for j, ha in enumerate(acts):
            u, h = f(ua, ha)
            Umat[i,j] = u; Hmat[i,j] = h
    return Umat, Hmat

def nash_eq(Umat, Hmat):
    nash=[]
    for i in range(2):
        for j in range(2):
            if np.isclose(Umat[i,j], np.max(Umat[:,j])) and np.isclose(Hmat[i,j], np.max(Hmat[i,:])):
                nash.append((acts[i], acts[j]))
    return nash

# Policy knob: conditionality penalty for separation (e.g., funding contingent on governance integration)
COND_PENALTY = 1.0
eq = nash_eq(*payoff_matrices(payoffs(cond_penalty=COND_PENALTY)))
# If multiple equilibria, pick the one with more integration
INTEGRATED_EQ = ("I","I") in eq

# Integration effect: if integrated, spillover is reduced (better coordination/continuity)
def spillover_multiplier(integrated: bool):
    return 0.80 if integrated else 1.00

integrated = INTEGRATED_EQ

# ---------------------------
# Audit–burden feedback (Model 7-ish)
# ---------------------------
# We model a burden term B_t that increases with pressure and reduces throughput.
q0 = 1.0
qP = 0.06        # complexity increases with pressure
e0 = 0.5
e_q = 0.25
b_e = 0.9
b_q = 0.6

k_burden_to_throughput = 0.06  # how much burden reduces effective discharge capacity

def burden_from_pressure(p_idx):
    q = q0 + qP*p_idx
    e = e0 + e_q*q
    B = b_e*e + b_q*q
    return float(B), float(q), float(e)

# ---------------------------
# Externality decision rules (myopic)
# ---------------------------
u_grid = np.linspace(0, 20, 81)
a_grid = np.linspace(0, 15, 61)
cu_eff = 0.12
ca_eff = 0.15
wC = 1.0
wS_base = 4.0

def payoff_C(u, p_idx):
    return -(wC*p_idx) - 0.5*cu_eff*(u**2)

def payoff_S(a, p_idx, g):
    wS = wS_base * state_burden_factor(g)
    return -(wS*p_idx) - 0.5*ca_eff*(a**2)

def arrivals(u):
    spill = spillover_base * spillover_multiplier(integrated)
    return base_arrivals + spill*np.exp(-beta_u*u)

def discharge_cap(a):
    return max(0.0, (base_arrivals + spillover_base) + k_a*a)

# ---------------------------
# Simulate
# ---------------------------
N = np.zeros(T+1); P = np.zeros(T+1)
u_t = np.zeros(T+1); a_t = np.zeros(T+1)
g_t = np.zeros(T+1); g_t[0]=g0
anchor_t = np.zeros(T+1)
agree_p = np.zeros(T+1)
within4 = np.zeros(T+1)
B_t = np.zeros(T+1); q_t = np.zeros(T+1); e_t = np.zeros(T+1)

N[0]=0.95*K

for t in range(T):
    g_t[t+1] = max(0.0, (1-i_realism)*g_t[t] + eps[t])

    pa = pr_anchor(P[t])
    anchor = (rng.random() < pa)
    anchor_t[t] = 1.0 if anchor else 0.0

    O = O_base + (0.03 if anchor else 0.0)
    agree_p[t] = pr_agreement(O, anchor)

    # Burden update based on current pressure
    B, q, e = burden_from_pressure(P[t])
    B_t[t] = B; q_t[t] = q; e_t[t] = e

    # Choose efforts myopically
    vals_a = np.array([payoff_S(a, P[t], g_t[t]) for a in a_grid])
    a_choice = float(a_grid[int(np.argmax(vals_a))])
    vals_u = np.array([payoff_C(u, P[t]) for u in u_grid])
    u_choice = float(u_grid[int(np.argmax(vals_u))])
    u_t[t]=u_choice; a_t[t]=a_choice

    # Realise arrivals/discharges
    A = rng.poisson(arrivals(u_choice))

    d_nom = discharge_cap(a_choice)
    # Burden reduces throughput (stylised): effective discharge declines with B
    d_eff = d_nom * np.exp(-k_burden_to_throughput * B)

    D = min(N[t], d_eff)
    N[t+1] = max(0.0, N[t] + A - D)
    P[t+1] = pressure_index(N[t+1], K)
    within4[t+1] = within4_proxy(P[t+1])

# final burden
B_t[T], q_t[T], e_t[T] = burden_from_pressure(P[T])

# ---------------------------
# Plots
# ---------------------------
plt.figure()
plt.plot(P, label="Pressure index")
plt.plot(B_t, label="Burden B_t")
plt.xlabel("Time (days)")
plt.title("V5 Hybrid: Pressure and audit-burden feedback")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/v5_pressure_burden.png", dpi=220)

plt.figure()
plt.plot(within4, label="ED within-4h proxy")
plt.axhline(ED_WITHIN_4H_2024_25, linestyle="--", label="AIHW 2024–25 (0.53)")
plt.xlabel("Time (days)")
plt.title("V5 Hybrid: ED within-4h proxy implied by pressure (with burden loop)")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/v5_within4_proxy.png", dpi=220)

plt.figure()
plt.plot(u_t, label="u_t (Commonwealth)")
plt.plot(a_t, label="a_t (State)")
plt.xlabel("Time (days)")
plt.title("V5 Hybrid: Efforts over time")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/v5_efforts.png", dpi=220)

plt.figure()
plt.plot(g_t, label="g_t (valuation gap)")
plt.plot(agree_p, label="Pr(agreement)")
plt.xlabel("Time (days)")
plt.title("V5 Hybrid: Gap and agreement probability")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/v5_gap_agreement.png", dpi=220)

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
    "p_agree": agree_p,
    "burden": B_t,
    "q": q_t,
    "e": e_t,
    "integrated_equilibrium": int(integrated),
    "cond_penalty": COND_PENALTY
})
df.to_csv(f"{OUTDIR}/v5_hybrid_timeseries.csv", index=False)
print("Integration equilibrium integrated =", integrated)
print("Saved plots + v5_hybrid_timeseries.csv to OUTDIR:", OUTDIR)
