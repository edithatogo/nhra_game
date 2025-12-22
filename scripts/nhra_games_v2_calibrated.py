"""
NHRA Game-Theory Mechanism Models (V2: "Plausibly Calibrated")
-------------------------------------------------------------
Purpose:
  Same mechanisms as V1, but with parameters anchored to publicly reported
  Australian system metrics (NEP, ED LOS within 4 hours, admitted ALOS, UCC handover rates,
  Schedule K one-off supplement, beds/availability, aged care occupancy).

Important:
  * Still a stylised model (not a fitted econometric model).
  * Calibration aims to put parameters on plausible scales and support sensitivity analysis.

Sources (in-code notes correspond to public documents/pages):
  - IHACPA NEP 2024–25: NEP = $6,465 per NWAU; hip replacement weight ~4.0954 NWAU.
  - AIHW ED time spent: 53% completed within 4h (2024–25); 67% in 2020–21.
  - AIHW admitted ALOS: overall 2.7 days; overnight public ALOS ~5.8 days.
  - AIHW hospital resources: 65,900 available public beds (2023–24).
  - Schedule K / NHRA extension: one-off $1.7b in 2025–26; extension operational to 30 June 2026.
  - Medicare UCC interim evaluation: ~89% handover by at least one method; ~68% electronic summary to usual GP.
  - AIHW aged care data: residential care occupancy ~88% (2023–24).
  - AMA exit block report: reported separations and patient days attributed to waiting for aged care.

Run:
  python nhra_games_v2_calibrated.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

np.random.seed(42)
OUTDIR = "."

# ------------------------------------------------------------
# Calibration anchors (public metrics)
# ------------------------------------------------------------

# IHACPA NEP 2024–25 (NEP = 6465 per NWAU)
NEP_PER_NWAU_2024_25 = 6465.0
HIP_REPLACEMENT_NWAU = 4.0954
HIP_REPLACEMENT_EFFICIENT_PRICE = NEP_PER_NWAU_2024_25 * HIP_REPLACEMENT_NWAU  # ≈ 26,477

# AIHW ED LOS within 4 hours
ED_WITHIN_4H_2024_25 = 0.53
ED_WITHIN_4H_2020_21 = 0.67  # for scaling "pressure" effects

# AIHW admitted ALOS
ALOS_ALL = 2.7
ALOS_PUBLIC_OVERNIGHT = 5.8

# AIHW hospital resources (public beds)
PUBLIC_BEDS_TOTAL = 65900  # Australia-wide; we model a representative facility instead of the system

# NHRA Schedule K one-off supplement
SCHEDULE_K_ONEOFF = 1.7e9

# NHFB corporate plan notes ~32.2b entitlement (excludes one-off); used only for scaling O in Model 3
NHFB_ENTITLEMENT_EST = 32.2e9
OUTSIDE_OPTION_RATIO = SCHEDULE_K_ONEOFF / NHFB_ENTITLEMENT_EST  # ~0.053

# Medicare UCC program evaluation / handover proxy
UCC_HANDOVER_ANY = 0.89
UCC_ELECTRONIC_SUMMARY_TO_GP = 0.68
UCC_HANDOVER_GAP = 1.0 - UCC_ELECTRONIC_SUMMARY_TO_GP  # ~0.32 (stylised boundary-risk proxy)

# AIHW aged care occupancy (proxy for downstream capacity constraint)
AGED_CARE_OCCUPANCY = 0.88

# ------------------------------------------------------------
# Shared helper / scaling: convert occupancy pressure to "ED within 4h"
# ------------------------------------------------------------
def pressure_index_from_occupancy(N, K):
    # pressure index is proportional to excess occupancy above nominal capacity
    return max(0.0, (N / K) - 1.0)

# Calibrate a linear mapping such that:
#  - at low pressure (index ~0) we recover ~2020–21 within-4h level (0.67)
#  - at moderate pressure (index ~0.10, ~110% occupancy) we hit ~2024–25 within-4h (0.53)
# This is purely a scaling device; do sensitivity analysis.
GAMMA_WITHIN4_PER_PRESSURE = (ED_WITHIN_4H_2020_21 - ED_WITHIN_4H_2024_25) / 0.10  # ≈ 1.4

def within4_from_pressure_index(p_idx):
    return float(np.clip(ED_WITHIN_4H_2020_21 - GAMMA_WITHIN4_PER_PRESSURE * p_idx, 0.0, 1.0))

# ============================================================
# Model 2 (re-calibrated): nominal vs effective share
# ============================================================
E = HIP_REPLACEMENT_EFFICIENT_PRICE  # anchor to NEP-weighted hip replacement efficient price
g = np.linspace(0, 20000, 301)       # gap range: $0–$20k (sensitivity)
alphas = [0.45, 0.40, 0.38]

plt.figure()
for a in alphas:
    plt.plot(g, (a*E)/(E+g), label=f"α={a:.2f}")
plt.xlabel("Valuation gap g ($)")
plt.ylabel("Effective share α_eff")
plt.title("V2 Model 2: Nominal vs effective share (NEP-anchored)")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/v2_model2_effective_share.png", dpi=220)

# ============================================================
# Model 3 (scaled): outside option strength
# ============================================================
V = 1.0
w = 0.5
# Outside option range anchored around Schedule K ratio (~0.05), but we explore wider for stress tests
O = np.linspace(0, 0.20, 201)  # 0–20% of "value"
dC = 0.4 * O
dS = 0.7 * O
surplus = V - dC - dS
feasible = surplus >= 0

UC = np.where(feasible, dC + w*surplus, np.nan)
US = np.where(feasible, dS + (1-w)*surplus, np.nan)

plt.figure()
plt.plot(O, surplus, label="Cooperative surplus")
plt.plot(O, UC, label="Agreement payoff: C")
plt.plot(O, US, label="Agreement payoff: S")
plt.axvline(OUTSIDE_OPTION_RATIO, linestyle="--", label="Schedule K ratio (~0.05)")
plt.axhline(0, linewidth=1)
plt.xlabel("Outside option strength O")
plt.ylabel("Normalised value")
plt.title("V2 Model 3: Outside option strength (Schedule K-anchored)")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/v2_model3_outside_option.png", dpi=220)

# ============================================================
# Model 5 (re-scaled): flow pressure generator
# ============================================================
# Choose a representative facility scale:
# - K=100 beds (representative), set arrival_rate to roughly match steady-state given ALOS (stylised).
#   Equilibrium for inpatient system: arrivals ≈ discharges ≈ K / ALOS_effective.
#   Use a blended ALOS_effective ~3.2 days as a compromise between overall ALOS (2.7) and public overnight (5.8).
ALOS_EFFECTIVE = 3.2
K = 100
arrival_rate = 0.90 * (K / ALOS_EFFECTIVE)  # 90% utilisation target ~28/day
arrival_rate = float(arrival_rate)

T = 200

def simulate_flow(d, seed=1):
    rng = np.random.default_rng(seed)
    N = np.zeros(T+1)
    p_idx = np.zeros(T+1)
    within4 = np.zeros(T+1)
    N[0] = 0.90 * K  # start near 90% occupancy
    for t in range(T):
        A = rng.poisson(arrival_rate)
        D = min(N[t], d)
        N[t+1] = max(0.0, N[t] + A - D)
        p_idx[t+1] = pressure_index_from_occupancy(N[t+1], K)
        within4[t+1] = within4_from_pressure_index(p_idx[t+1])
    return N, p_idx, within4

# Downstream constraint proxy: higher aged care occupancy reduces effective discharge capacity.
# Simple scalar: availability = 1 - occupancy; then scale a baseline discharge cap.
agedcare_availability = max(0.0, 1.0 - AGED_CARE_OCCUPANCY)  # ~0.12
d_base = arrival_rate  # at equilibrium
d_exitblock = d_base * (0.12 / max(0.12, agedcare_availability))  # becomes d_base here; tweak for sensitivity
# For exploration: vary d around base +/- 20%
d_vals = [0.80*d_base, 0.90*d_base, 1.00*d_base, 1.10*d_base]

plt.figure()
for d in d_vals:
    _, p, _ = simulate_flow(d, seed=42)
    plt.plot(p, label=f"d={d:.1f}")
plt.xlabel("Time (days)")
plt.ylabel("Pressure index (excess occupancy ratio)")
plt.title("V2 Model 5: Pressure index trajectories vs discharge capacity")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/v2_model5_pressure_trajectories.png", dpi=220)

# Map to ED within-4h proxy
plt.figure()
for d in d_vals:
    _, _, w4 = simulate_flow(d, seed=42)
    plt.plot(w4, label=f"d={d:.1f}")
plt.xlabel("Time (days)")
plt.ylabel("Estimated ED within 4h (proxy)")
plt.title("V2 Model 5: ED within-4h proxy implied by occupancy pressure")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/v2_model5_within4_proxy.png", dpi=220)

# ============================================================
# Model 6 (re-parameterised): integration coordination
# ============================================================
# Use UCC handover gaps as a *stylised* boundary risk proxy:
#   - Separate risk ~ electronic summary gap (~0.32)
#   - Integrated risk ~ (1 - handover-any) (~0.11) or lower.
h_sep = UCC_HANDOVER_GAP        # ~0.32
h_int = 1.0 - UCC_HANDOVER_ANY  # ~0.11
L = 10.0                        # scale of boundary-loss (arbitrary utility units)
cU, cH = 1.0, 1.0               # integration effort costs (utility units)
shareU = 0.30                   # who bears boundary-risk cost

acts = ["I","S"]

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

U0, H0 = payoff_matrices(payoffs())
UP, HP = payoff_matrices(payoffs(cond_penalty=1.0))
US, HS = payoff_matrices(payoffs(cond_subsidy=1.0))

print("\nV2 MODEL 6 Nash equilibria")
print("Baseline:", nash_eq(U0,H0))
print("Penalty for Separate:", nash_eq(UP,HP))
print("Subsidy for Integrate:", nash_eq(US,HS))

print("\nDone. V2 plots saved to OUTDIR:", OUTDIR)
