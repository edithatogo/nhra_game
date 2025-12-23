"""
NHRA Game-Theory Mechanism Models (V1)
-------------------------------------
Purpose:
  A set of stylised ("toy") mechanism models representing interacting incentive problems
  relevant to NHRA negotiations and hospital system pressures.

Notes:
  * This is V1: the same modelling logic as previously run, cleaned into a single script.
  * Parameters are illustrative, not calibrated to NHRA data.
  * Outputs: PNG plots + printed tables.

Run:
  python nhra_games_v1.py
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Reproducibility
np.random.seed(42)

OUTDIR = "."  # change to a path if you prefer

# -----------------------------
# Utilities
# -----------------------------
def argmax_grid(f, x_grid, y_grid):
    best = None
    for x in x_grid:
        for y in y_grid:
            val = f(x, y)
            if (best is None) or (val > best[2]):
                best = (x, y, val)
    return best

def nash_best_response_iter(fC, fS, u_grid, a_grid, u0=None, a0=None, iters=30):
    u = u0 if u0 is not None else float(u_grid[len(u_grid)//2])
    a = a0 if a0 is not None else float(a_grid[len(a_grid)//2])
    for _ in range(iters):
        valsS = np.array([fS(u, aa) for aa in a_grid])
        a = float(a_grid[int(np.argmax(valsS))])
        valsC = np.array([fC(uu, a) for uu in u_grid])
        u = float(u_grid[int(np.argmax(valsC))])
    return u, a

# ============================================================
# Model 1: Externality / cost-shifting (VFI spillover)
# ============================================================
theta = 20.0   # baseline upstream "demand pressure"
D0 = 1.0
beta = 0.35    # how upstream effort reduces pressure (diminishing returns)
lam = 1.0      # how acute/placement effort reduces pressure
cu = 0.9       # cost of upstream effort
ca = 0.8       # cost of acute/placement effort

def pressure(u, a):
    return max(0.0, theta * D0 * np.exp(-beta * u) - lam * a)

def make_payoffs(wC=1.0, wS=5.0):
    def UC(u, a):
        P = pressure(u, a)
        return -(wC * P) - 0.5 * cu * (u**2)
    def US(u, a):
        P = pressure(u, a)
        return -(wS * P) - 0.5 * ca * (a**2)
    return UC, US

u_grid = np.linspace(0, 20, 401)
a_grid = np.linspace(0, 25, 501)

UC_base, US_base = make_payoffs(wC=1.0, wS=5.0)
u_nash, a_nash = nash_best_response_iter(UC_base, US_base, u_grid, a_grid)

def U_social(u, a):
    return UC_base(u, a) + US_base(u, a)

u_soc, a_soc, _ = argmax_grid(lambda u,a: U_social(u,a), np.linspace(0,20,121), np.linspace(0,25,151))

UC_pool, US_pool = make_payoffs(wC=4.0, wS=5.0)
u_nash_pool, a_nash_pool = nash_best_response_iter(UC_pool, US_pool, u_grid, a_grid)

summary_m1 = pd.DataFrame([
    {"Scenario":"Nash (baseline)", "u_upstream":u_nash, "a_acute":a_nash, "Pressure P":pressure(u_nash, a_nash)},
    {"Scenario":"Social optimum", "u_upstream":u_soc, "a_acute":a_soc, "Pressure P":pressure(u_soc, a_soc)},
    {"Scenario":"Nash (more C internalisation)", "u_upstream":u_nash_pool, "a_acute":a_nash_pool, "Pressure P":pressure(u_nash_pool, a_nash_pool)},
])

# Best response curve for a(u)
best_a_given_u = []
for u in u_grid[::10]:
    valsS = np.array([US_base(u, aa) for aa in a_grid])
    best_a_given_u.append((u, float(a_grid[int(np.argmax(valsS))])))
best_a_given_u = np.array(best_a_given_u)

plt.figure()
plt.plot(best_a_given_u[:,0], best_a_given_u[:,1], label="State best response a(u)")
plt.scatter([u_nash],[a_nash], label="Nash")
plt.scatter([u_soc],[a_soc], label="Social optimum")
plt.scatter([u_nash_pool],[a_nash_pool], label="Nash (C internalises more)")
plt.xlabel("Commonwealth upstream effort u")
plt.ylabel("State acute/subacute effort a")
plt.title("Model 1: Externality game — best response and equilibria")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/model1_externality_equilibria_v1.png", dpi=200)

print("\nMODEL 1 SUMMARY\n", summary_m1.to_string(index=False))

# ============================================================
# Model 2: Nominal vs effective share (valuation gap)
# ============================================================
E = 30000.0
g = np.linspace(0, 20000, 301)
alphas = [0.45, 0.40, 0.38]

plt.figure()
for a in alphas:
    plt.plot(g, (a*E)/(E+g), label=f"α={a:.2f}")
plt.xlabel("Valuation gap g ($)")
plt.ylabel("Effective share α_eff")
plt.title("Model 2: Nominal vs effective share (valuation gap)")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/model2_effective_share_v1.png", dpi=200)

# gap dynamics under different indexation realism i
T = 24
g0 = 6000.0
eps = np.random.normal(150, 100, size=T)  # drift/noise
i_vals = [0.05, 0.20, 0.40]

plt.figure()
for i in i_vals:
    gt = np.zeros(T+1); gt[0]=g0
    for t in range(T):
        gt[t+1]=max(0.0,(1-i)*gt[t]+eps[t])
    plt.plot(np.arange(T+1), gt, label=f"i={i:.2f}")
plt.xlabel("Time (t)")
plt.ylabel("Gap g_t ($)")
plt.title("Model 2: Gap evolution under indexation realism")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/model2_gap_dynamics_v1.png", dpi=200)

# ============================================================
# Model 3: Bargaining under outside options (extension/top-up)
# ============================================================
V = 1.0
w = 0.5
O = np.linspace(0, 0.95, 191)
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
plt.axhline(0, linewidth=1)
plt.xlabel("Outside option strength O")
plt.ylabel("Normalised value")
plt.title("Model 3: Outside option shrinks surplus; beyond threshold, agreement infeasible")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/model3_outside_option_v1.png", dpi=200)

# ============================================================
# Model 4: Signalling/anchoring under pressure
# ============================================================
P = np.linspace(0, 50, 251)
k = 0.18
P0 = 18.0
p_anchor = 1/(1+np.exp(-k*(P-P0)))

plt.figure()
plt.plot(P, p_anchor)
plt.xlabel("Pressure P")
plt.ylabel("Pr(anchor rhetoric)")
plt.title("Model 4: Signalling under pressure — anchor probability")
plt.tight_layout()
plt.savefig(f"{OUTDIR}/model4_signalling_v1.png", dpi=200)

# ============================================================
# Model 5: Flow constraint / exit block (pressure generator)
# ============================================================
np.random.seed(42)
T = 200
K = 100
phi = 0.6
arrival_rate = 9.0

def simulate_flow(d, seed=1):
    rng = np.random.default_rng(seed)
    N = np.zeros(T+1)
    P = np.zeros(T+1)
    N[0] = 90
    for t in range(T):
        A = rng.poisson(arrival_rate)
        D = min(N[t], d)
        N[t+1] = max(0.0, N[t] + A - D)
        P[t+1] = phi * max(0.0, N[t+1] - K)
    return N, P

d_vals = [6, 8, 10, 12]
plt.figure()
for d in d_vals:
    _, Psim = simulate_flow(d, seed=42)
    plt.plot(Psim, label=f"d={d}")
plt.xlabel("Time")
plt.ylabel("Pressure P_t")
plt.title("Model 5: Flow constraint — pressure trajectories by discharge cap d")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/model5_pressure_trajectories_v1.png", dpi=200)

d_scan = np.arange(4, 16, 1)
avgP = []
for d in d_scan:
    _, Psim = simulate_flow(d, seed=7)
    avgP.append(float(np.mean(Psim[50:])))

plt.figure()
plt.plot(d_scan, avgP, marker="o")
plt.xlabel("Discharge cap d")
plt.ylabel("Average pressure (post burn-in)")
plt.title("Model 5: Threshold-like response — avg pressure vs discharge capacity")
plt.tight_layout()
plt.savefig(f"{OUTDIR}/model5_avg_pressure_vs_d_v1.png", dpi=200)

# ============================================================
# Model 6: Integration coordination game (UCC–LHN governance)
# ============================================================
cU, cH = 2.0, 2.5
h_sep = 0.25
h_int = 0.08
L = 20.0
shareU = 0.25
acts = ["I", "S"]  # Integrate, Separate

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
        else:  # S,S
            risk = h_sep * L
            U = -0.0 - shareU*risk - cond_penalty
            H = -0.0 - (1-shareU)*risk
        return U, H
    return f

def payoff_matrices(f):
    Umat = np.zeros((2,2))
    Hmat = np.zeros((2,2))
    for i, ua in enumerate(acts):
        for j, ha in enumerate(acts):
            u, h = f(ua, ha)
            Umat[i,j] = u
            Hmat[i,j] = h
    return Umat, Hmat

def nash_eq(Umat, Hmat):
    nash=[]
    for i in range(2):
        for j in range(2):
            if np.isclose(Umat[i,j], np.max(Umat[:,j])) and np.isclose(Hmat[i,j], np.max(Hmat[i,:])):
                nash.append((acts[i], acts[j]))
    return nash

def matrix_to_df(Umat, Hmat):
    df = pd.DataFrame(index=[f"U:{a}" for a in acts], columns=[f"H:{a}" for a in acts])
    for i in range(2):
        for j in range(2):
            df.iloc[i,j] = f"{Umat[i,j]:.1f}, {Hmat[i,j]:.1f}"
    return df

U0, H0 = payoff_matrices(payoffs())
UP, HP = payoff_matrices(payoffs(cond_penalty=2.5))
US, HS = payoff_matrices(payoffs(cond_subsidy=2.5))

print("\nMODEL 6 PAYOFFS (U payoff, H payoff)\nBaseline\n", matrix_to_df(U0,H0))
print("\nPenalty for Separate (U)\n", matrix_to_df(UP,HP))
print("\nSubsidy for Integrate (U)\n", matrix_to_df(US,HS))
print("\nMODEL 6 NASH EQUILIBRIA\nBaseline:", nash_eq(U0,H0), "\nPenalty:", nash_eq(UP,HP), "\nSubsidy:", nash_eq(US,HS))

# ============================================================
# Model 7: Audit–burden feedback
# ============================================================
np.random.seed(42)
T = 80
p_base = 5.0
rho = 0.65
q0 = 1.0
e0 = 0.5
e_q = 0.25
b_e = 0.9
b_q = 0.6
eta = 0.35
k_red = 1.2

def simulate_feedback(qP, rho=0.65, eta=0.35, k_red=1.2, seed=0):
    rng = np.random.default_rng(seed)
    P = np.zeros(T+1); q = np.zeros(T+1); e = np.zeros(T+1); B = np.zeros(T+1)
    P[0] = 8.0
    for t in range(T):
        q[t] = q0 + qP*P[t]
        e[t] = e0 + e_q*q[t]
        B[t] = b_e*e[t] + b_q*q[t]
        shock = rng.normal(0, 0.4)
        P[t+1] = max(0.0, p_base + rho*P[t] + eta*B[t] - k_red*e[t] + shock)
    q[T] = q0 + qP*P[T]
    e[T] = e0 + e_q*q[T]
    B[T] = b_e*e[T] + b_q*q[T]
    return P, q, e, B

qP_vals = [0.02, 0.05, 0.08]
plt.figure()
for qP in qP_vals:
    Psim, *_ = simulate_feedback(qP, seed=42)
    plt.plot(Psim, label=f"qP={qP:.2f}")
plt.xlabel("Time")
plt.ylabel("Pressure P_t")
plt.title("Model 7: Audit–burden feedback — pressure trajectories")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/model7_pressure_feedback_v1.png", dpi=200)

# Stress test
qP_vals = [0.05, 0.12, 0.20]
plt.figure()
for qP in qP_vals:
    Psim, *_ = simulate_feedback(qP, rho=0.80, eta=0.75, k_red=0.8, seed=42)
    plt.plot(Psim, label=f"qP={qP:.2f}")
plt.xlabel("Time")
plt.ylabel("Pressure P_t")
plt.title("Model 7 (stress): stronger feedback can create escalating pressure")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTDIR}/model7_stress_test_v1.png", dpi=200)

print("\nDone. Plots saved to OUTDIR:", OUTDIR)
