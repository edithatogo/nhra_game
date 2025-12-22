"""
MPE extensions for NHRA stylised games (V7.2 and V8).

V7.2: 2-state Markov game with
  x = pressure (system congestion proxy)
  g = valuation gap (NEP vs actual cost proxy)

V8: Adds a slow-moving constraint
  c = capacity / slack

This file is intentionally self-contained (numpy/matplotlib/pandas only).
All randomness uses a fixed seed by default for reproducibility.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# -----------------------------
# Helpers
# -----------------------------
ED_2024_25 = 0.53
ED_2020_21 = 0.67

def _gamma_from_anchor() -> float:
    # If x rises by 0.10, ED proxy drops from 0.67 to 0.53 (stylised anchor).
    return (ED_2020_21 - ED_2024_25) / 0.10

GAMMA = _gamma_from_anchor()

def ed_proxy_from_x(x: np.ndarray) -> np.ndarray:
    return np.clip(ED_2020_21 - GAMMA * np.asarray(x), 0.0, 1.0)

def ed_proxy_from_xc(x: np.ndarray, c: np.ndarray, lam: float = 0.15) -> np.ndarray:
    x = np.asarray(x)
    c = np.asarray(c)
    return np.clip(ED_2020_21 - GAMMA * x - lam * (1.0 - c), 0.0, 1.0)

def acf1(x: np.ndarray) -> float:
    x = np.asarray(x)
    x = x - np.mean(x)
    if len(x) < 3:
        return float("nan")
    return float(np.corrcoef(x[:-1], x[1:])[0, 1])


# -----------------------------
# Parameter factories (fast configs for CI and local runs)
# -----------------------------
def v72_params_fast() -> Dict:
    return dict(
        XMAX=2.5, GMAX=1.0, nx=19, ng=9,
        u_actions=np.linspace(0, 20, 5),      # 0,5,10,15,20
        r_actions=np.linspace(0, 1.0, 3),     # 0,0.5,1
        a_actions=np.linspace(0, 15, 5),      # 0,3.75,7.5,11.25,15
        rho=0.86, beta=0.18, sigma_x=0.035,
        mu_g=0.82, k_r=0.12, spill_g=0.24, g_drift=0.02,
        S0=0.020, k_a=0.030, phi_g=0.95,
        delta=0.965,
        wC_x=1.0, wC_g=0.8,
        wS_x=2.2, wS_g=0.3,
        c_u=0.030, c_r=1.00, c_a=0.12,
        burden_u=0.0, burden_a=0.0
    )

def v8_params_fast() -> Dict:
    p = v72_params_fast()
    p.update(dict(
        nx=15, ng=9, nc=7,
        CMAX=1.0,
        eta_a=0.018,
        eta_u=0.004,
        dep0=0.012,
        dep_x=0.014,
        u_max_base=20.0,
        treasury_cap=True,
        ed_lambda_c=0.15
    ))
    return p


# -----------------------------
# V7.2: solve + simulate
# -----------------------------
def v72_solve(p: Dict, continuation: Optional[Dict] = None,
             max_outer: int = 10, max_vi: int = 30, tol: float = 1e-6) -> Dict:
    XMAX, GMAX = float(p["XMAX"]), float(p["GMAX"])
    nx, ng = int(p["nx"]), int(p["ng"])
    xg = np.linspace(0.0, XMAX, nx)
    gg = np.linspace(0.0, GMAX, ng)
    dx = xg[1] - xg[0]
    dg = gg[1] - gg[0]

    uA = np.asarray(p["u_actions"])
    rA = np.asarray(p["r_actions"])
    aA = np.asarray(p["a_actions"])
    nu, nr, na = len(uA), len(rA), len(aA)
    nC = nu * nr

    X, G = np.meshgrid(xg, gg, indexing="ij")
    xs = X.reshape(-1)
    gs = G.reshape(-1)
    nS = xs.size

    uC = np.repeat(uA, nr)
    rC = np.tile(rA, nu)

    c_u_eff = float(p["c_u"]) * (1.0 + float(p["burden_u"]))
    c_a_eff = float(p["c_a"]) * (1.0 + float(p["burden_a"]))

    u_cost = 0.5 * c_u_eff * (uA ** 2)
    r_cost = 0.5 * float(p["c_r"]) * (rA ** 2)
    a_cost = 0.5 * c_a_eff * (aA ** 2)
    cC = np.repeat(u_cost, nr) + np.tile(r_cost, nu)

    noise_vals = np.array([-float(p["sigma_x"]), 0.0, +float(p["sigma_x"])])
    noise_probs = np.array([0.25, 0.50, 0.25])

    def ix(x):
        return np.clip(np.rint((x - xg[0]) / dx).astype(np.int32), 0, nx - 1)

    def ig(g):
        return np.clip(np.rint((g - gg[0]) / dg).astype(np.int32), 0, ng - 1)

    Xs = xs[:, None, None, None]
    Gs = gs[:, None, None, None]
    U = uC[None, :, None, None]
    R = rC[None, :, None, None]
    A = aA[None, None, :, None]
    EPS = noise_vals[None, None, None, :]

    gp = float(p["mu_g"]) * Gs + float(p["spill_g"]) * Xs - float(p["k_r"]) * R + float(p["g_drift"])
    gp = np.clip(gp, 0.0, GMAX)

    inj = float(p["S0"]) * np.exp(-float(p["beta"]) * U) * (1.0 + float(p["phi_g"]) * Gs)
    xp = float(p["rho"]) * Xs + inj - float(p["k_a"]) * A + EPS
    xp = np.clip(xp, 0.0, XMAX)

    j = ix(xp)
    k = ig(gp)
    k = np.broadcast_to(k, j.shape)
    next_idx = (j * ng + k).astype(np.int32)

    delta = float(p["delta"])
    wC_x, wC_g = float(p["wC_x"]), float(p["wC_g"])
    wS_x, wS_g = float(p["wS_x"]), float(p["wS_g"])

    def br_C(piS: np.ndarray, V: np.ndarray):
        idxs = next_idx[np.arange(nS)[:, None], np.arange(nC)[None, :], piS[:, None], :]
        ev = (V[idxs] * noise_probs).sum(axis=-1)
        costs = (wC_x * xs + wC_g * gs)[:, None] + cC[None, :] + delta * ev
        piC = np.argmin(costs, axis=1).astype(np.int32)
        return piC, np.min(costs, axis=1)

    def br_S(piC: np.ndarray, V: np.ndarray):
        idxs = next_idx[np.arange(nS)[:, None], piC[:, None], np.arange(na)[None, :], :]
        ev = (V[idxs] * noise_probs).sum(axis=-1)
        costs = (wS_x * xs + wS_g * gs)[:, None] + a_cost[None, :] + delta * ev
        piS = np.argmin(costs, axis=1).astype(np.int32)
        return piS, np.min(costs, axis=1)

    if continuation is not None and len(continuation["piC"]) == nS and len(continuation["piS"]) == nS:
        piC = np.array(continuation["piC"], dtype=np.int32).copy()
        piS = np.array(continuation["piS"], dtype=np.int32).copy()
    else:
        piC = np.zeros(nS, dtype=np.int32)
        piS = np.zeros(nS, dtype=np.int32)

    for _ in range(max_outer):
        V = np.zeros(nS)
        for __ in range(max_vi):
            piC_new, V_new = br_C(piS, V)
            if np.max(np.abs(V_new - V)) < tol:
                piC = piC_new
                break
            V = V_new
        else:
            piC = piC_new

        V = np.zeros(nS)
        for __ in range(max_vi):
            piS_new, V_new = br_S(piC, V)
            if np.max(np.abs(V_new - V)) < tol:
                piS = piS_new
                break
            V = V_new
        else:
            piS = piS_new

    return dict(x_grid=xg, g_grid=gg, piC=piC, piS=piS, uC=uC, rC=rC, a_actions=aA, params=p)

def v72_sim(sol: Dict, T: int = 240, seed: int = 42, x0: float = 0.12, g0: float = 0.40):
    p = sol["params"]
    xg, gg = sol["x_grid"], sol["g_grid"]
    dx = xg[1] - xg[0]
    dg = gg[1] - gg[0]
    nx, ng = len(xg), len(gg)

    rng = np.random.default_rng(seed)
    noise_vals = np.array([-float(p["sigma_x"]), 0.0, +float(p["sigma_x"])])
    noise_probs = np.array([0.25, 0.50, 0.25])

    x = np.zeros(T + 1)
    g = np.zeros(T + 1)
    u = np.zeros(T + 1)
    r = np.zeros(T + 1)
    a = np.zeros(T + 1)
    x[0] = float(np.clip(x0, 0.0, float(p["XMAX"])))
    g[0] = float(np.clip(g0, 0.0, float(p["GMAX"])))

    for t in range(T):
        ix0 = int(np.clip(int(np.rint((x[t] - xg[0]) / dx)), 0, nx - 1))
        ig0 = int(np.clip(int(np.rint((g[t] - gg[0]) / dg)), 0, ng - 1))
        s = ix0 * ng + ig0

        ic = int(sol["piC"][s])
        ia = int(sol["piS"][s])

        u[t] = float(sol["uC"][ic])
        r[t] = float(sol["rC"][ic])
        a[t] = float(sol["a_actions"][ia])

        eps = float(rng.choice(noise_vals, p=noise_probs))
        inj = float(p["S0"]) * np.exp(-float(p["beta"]) * u[t]) * (1.0 + float(p["phi_g"]) * g[t])
        x[t + 1] = float(np.clip(float(p["rho"]) * x[t] + inj - float(p["k_a"]) * a[t] + eps, 0.0, float(p["XMAX"])))
        g[t + 1] = float(np.clip(float(p["mu_g"]) * g[t] + float(p["spill_g"]) * x[t] - float(p["k_r"]) * r[t] + float(p["g_drift"],), 0.0, float(p["GMAX"])))

    return x, g, u, r, a

def v72_interventions(base_p: Dict) -> Dict[str, Dict]:
    sc = {}
    sc["baseline"] = base_p.copy()

    p = base_p.copy()
    p["S0"] = base_p["S0"] * 0.90
    p["spill_g"] = base_p["spill_g"] * 0.90
    sc["upstream_fix"] = p

    p = base_p.copy()
    p["phi_g"] = base_p["phi_g"] * 0.75
    p["k_r"] = base_p["k_r"] * 1.25
    sc["indexation_reform"] = p

    p = base_p.copy()
    p["k_a"] = base_p["k_a"] * 1.25
    p["burden_a"] = 0.15
    sc["pooled_funding"] = p

    p = base_p.copy()
    p["burden_u"] = 0.35
    p["burden_a"] = 0.35
    sc["audit_heavy"] = p

    p = base_p.copy()
    p["c_u"] = base_p["c_u"] * 0.6
    sc["fiscal_shift"] = p

    p = base_p.copy()
    p["S0"] = base_p["S0"] * 0.90
    p["spill_g"] = base_p["spill_g"] * 0.90
    p["phi_g"] = base_p["phi_g"] * 0.75
    p["k_r"] = base_p["k_r"] * 1.25
    p["k_a"] = base_p["k_a"] * 1.25
    p["burden_a"] = 0.10
    sc["governance_package"] = p

    return sc

def v72_write_bundle(outdir: str, fast: bool = True) -> pd.DataFrame:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    p0 = v72_params_fast()
    sol0 = v72_solve(p0, continuation=None)
    sim0 = v72_sim(sol0, T=180, seed=42)
    df0 = v72_summarize_and_save(out, "int_baseline", sol0, sim0, save_policy=True)

    rows = [df0]
    cont = {"piC": sol0["piC"], "piS": sol0["piS"]}

    for name, p in v72_interventions(p0).items():
        if name == "baseline":
            continue
        sol = v72_solve(p, continuation=cont)
        sim = v72_sim(sol, T=180, seed=42)
        s = v72_summarize_and_save(out, f"int_{name}", sol, sim, save_policy=(name == "governance_package"))
        rows.append(s)
        cont = {"piC": sol["piC"], "piS": sol["piS"]}

    df = pd.DataFrame(rows)
    df.to_csv(out / "v72_interventions_summary.csv", index=False)

    _barplot(df, "mean_ed", out / "v72_interventions_mean_ed.png", "V7.2 interventions (mean ED proxy)")
    _barplot(df, "mean_x", out / "v72_interventions_mean_x.png", "V7.2 interventions (mean pressure)")
    _barplot(df, "mean_g", out / "v72_interventions_mean_g.png", "V7.2 interventions (mean valuation gap)")

    plt.figure(figsize=(6.6, 4.2))
    plt.scatter(df["mean_g"], df["mean_ed"])
    for _, row in df.iterrows():
        plt.text(row["mean_g"], row["mean_ed"], str(row["tag"]).replace("int_", ""), fontsize=7)
    plt.axhline(ED_2024_25, linestyle="--")
    plt.xlabel("mean gap g")
    plt.ylabel("mean ED proxy")
    plt.title("V7.2: ED proxy vs valuation gap")
    plt.tight_layout()
    plt.savefig(out / "v72_scatter_ed_vs_gap.png", dpi=220)
    plt.close()

    # tornado (fast)
    sens = v72_tornado_fast(out, p0, continuation={"piC": sol0["piC"], "piS": sol0["piS"]})
    return df

def _barplot(df: pd.DataFrame, metric: str, path: Path, title: str):
    d = df.sort_values(metric, ascending=False)
    plt.figure(figsize=(9.0, 3.8))
    plt.bar(np.arange(len(d)), d[metric].to_numpy())
    plt.xticks(np.arange(len(d)), d["tag"].to_numpy(), rotation=45, ha="right", fontsize=8)
    if metric == "mean_ed":
        plt.axhline(ED_2024_25, linestyle="--")
    plt.title(title)
    plt.ylabel(metric)
    plt.tight_layout()
    plt.savefig(path, dpi=220)
    plt.close()

def v72_summarize_and_save(out: Path, tag: str, sol: Dict, sim, burn: int = 35, save_policy: bool = False) -> Dict:
    x, g, u, r, a = sim
    ed = ed_proxy_from_x(x)
    summ = dict(
        tag=tag,
        mean_x=float(np.mean(x[burn:])),
        sd_x=float(np.std(x[burn:])),
        acf1_x=acf1(x[burn:]),
        mean_g=float(np.mean(g[burn:])),
        sd_g=float(np.std(g[burn:])),
        acf1_g=acf1(g[burn:]),
        mean_ed=float(np.mean(ed[burn:])),
        mean_u=float(np.mean(u[burn:-1])),
        mean_r=float(np.mean(r[burn:-1])),
        mean_a=float(np.mean(a[burn:-1])),
    )

    plt.figure(figsize=(6.8, 3.6))
    plt.plot(x)
    plt.axhline(0.10, linestyle="--")
    plt.title(f"V7.2 {tag}: pressure x")
    plt.xlabel("t")
    plt.ylabel("x")
    plt.tight_layout()
    plt.savefig(out / f"v72_{tag}_pressure.png", dpi=220)
    plt.close()

    plt.figure(figsize=(6.8, 3.6))
    plt.plot(g)
    plt.title(f"V7.2 {tag}: gap g")
    plt.xlabel("t")
    plt.ylabel("g")
    plt.tight_layout()
    plt.savefig(out / f"v72_{tag}_gap.png", dpi=220)
    plt.close()

    plt.figure(figsize=(6.8, 3.6))
    plt.plot(ed)
    plt.axhline(ED_2024_25, linestyle="--")
    plt.title(f"V7.2 {tag}: ED proxy")
    plt.xlabel("t")
    plt.ylabel("ED≤4h")
    plt.tight_layout()
    plt.savefig(out / f"v72_{tag}_edproxy.png", dpi=220)
    plt.close()

    pd.DataFrame({"t": np.arange(len(x)), "x": x, "g": g, "u": u, "r": r, "a": a, "ed_proxy": ed}).to_csv(
        out / f"v72_{tag}_timeseries.csv", index=False
    )

    if save_policy:
        nx, ng = len(sol["x_grid"]), len(sol["g_grid"])
        U = sol["uC"][sol["piC"]].reshape(nx, ng)
        R = sol["rC"][sol["piC"]].reshape(nx, ng)
        A = sol["a_actions"][sol["piS"]].reshape(nx, ng)
        _policy_heat(out, sol, U, f"V7.2 {tag}: u(x,g)", f"v72_{tag}_policy_u.png")
        _policy_heat(out, sol, R, f"V7.2 {tag}: r(x,g)", f"v72_{tag}_policy_r.png")
        _policy_heat(out, sol, A, f"V7.2 {tag}: a(x,g)", f"v72_{tag}_policy_a.png")

        pol = []
        for i, xv in enumerate(sol["x_grid"]):
            for j, gv in enumerate(sol["g_grid"]):
                pol.append({"x": float(xv), "g": float(gv), "u": float(U[i, j]), "r": float(R[i, j]), "a": float(A[i, j])})
        pd.DataFrame(pol).to_csv(out / f"v72_{tag}_policy_grid.csv", index=False)

    return summ

def _policy_heat(out: Path, sol: Dict, Z: np.ndarray, title: str, fname: str):
    nx, ng = Z.shape
    plt.figure(figsize=(6.8, 4.8))
    plt.imshow(Z, origin="lower", aspect="auto")
    plt.xticks(np.arange(ng), [f"{v:.1f}" for v in sol["g_grid"]], rotation=45, fontsize=7)
    plt.yticks(np.arange(nx)[::2], [f"{v:.1f}" for v in sol["x_grid"][::2]], fontsize=7)
    plt.xlabel("g")
    plt.ylabel("x")
    plt.title(title)
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(out / fname, dpi=220)
    plt.close()

def v72_tornado_fast(out: Path, p0: Dict, continuation: Optional[Dict]) -> pd.DataFrame:
    key_params = ["S0", "k_a", "phi_g", "k_r", "c_r"]

    # baseline
    sol0 = v72_solve(p0, continuation=continuation)
    sim0 = v72_sim(sol0, T=220, seed=42)
    base = v72_summarize_and_save(out, "sens_baseline", sol0, sim0, save_policy=False)
    rows = [{"case": "baseline", "param": "-", "mult": 1.0, **base}]

    cont = {"piC": sol0["piC"], "piS": sol0["piS"]}
    for par in key_params:
        for mult in [0.8, 1.2]:
            p = p0.copy()
            p[par] = float(p0[par] * mult)
            sol = v72_solve(p, continuation=cont)
            sim = v72_sim(sol, T=220, seed=42)
            s = v72_summarize_and_save(out, f"sens_{par}_{mult:.1f}", sol, sim, save_policy=False)
            rows.append({"case": f"{par}_{mult:.1f}", "param": par, "mult": mult, **s})
            cont = {"piC": sol["piC"], "piS": sol["piS"]}

    df = pd.DataFrame(rows)
    df.to_csv(out / "v72_sensitivity_tornado_fast.csv", index=False)

    base_ed = float(df.loc[df["case"] == "baseline", "mean_ed"].iloc[0])
    tor_rows = []
    for par in key_params:
        low = float(df.loc[df["case"] == f"{par}_0.8", "mean_ed"].iloc[0]) - base_ed
        high = float(df.loc[df["case"] == f"{par}_1.2", "mean_ed"].iloc[0]) - base_ed
        tor_rows.append({"param": par, "low": low, "high": high, "span": abs(high - low)})
    tor = pd.DataFrame(tor_rows).sort_values("span", ascending=False)

    plt.figure(figsize=(7.4, 3.9))
    y = np.arange(len(tor))
    plt.hlines(y, tor["low"], tor["high"])
    plt.plot(tor["low"], y, "o")
    plt.plot(tor["high"], y, "o")
    plt.yticks(y, tor["param"])
    plt.axvline(0.0, linestyle="--")
    plt.xlabel("Δ mean ED proxy (vs baseline)")
    plt.title("V7.2 sensitivity (fast tornado)")
    plt.tight_layout()
    plt.savefig(out / "v72_sensitivity_tornado_fast.png", dpi=220)
    plt.close()

    return tor


# -----------------------------
# V8: solve + simulate (x,g,c)
# -----------------------------
def v8_solve(p: Dict, continuation: Optional[Dict] = None,
             max_outer: int = 10, max_vi: int = 30, tol: float = 1e-6) -> Dict:
    XMAX, GMAX = float(p["XMAX"]), float(p["GMAX"])
    nx, ng, nc = int(p["nx"]), int(p["ng"]), int(p["nc"])
    xg = np.linspace(0.0, XMAX, nx)
    gg = np.linspace(0.0, GMAX, ng)
    cg = np.linspace(0.0, float(p["CMAX"]), nc)
    dx = xg[1] - xg[0]
    dg = gg[1] - gg[0]
    dc = cg[1] - cg[0]

    uA = np.asarray(p["u_actions"])
    rA = np.asarray(p["r_actions"])
    aA = np.asarray(p["a_actions"])
    nu, nr, na = len(uA), len(rA), len(aA)
    nC = nu * nr

    X, G, C = np.meshgrid(xg, gg, cg, indexing="ij")
    xs = X.reshape(-1)
    gs = G.reshape(-1)
    cs = C.reshape(-1)
    nS = xs.size

    uC = np.repeat(uA, nr)
    rC = np.tile(rA, nu)

    c_u_eff = float(p["c_u"]) * (1.0 + float(p["burden_u"]))
    c_a_eff = float(p["c_a"]) * (1.0 + float(p["burden_a"]))
    u_cost = 0.5 * c_u_eff * (uA ** 2)
    r_cost = 0.5 * float(p["c_r"]) * (rA ** 2)
    a_cost = 0.5 * c_a_eff * (aA ** 2)
    cC = np.repeat(u_cost, nr) + np.tile(r_cost, nu)

    # Treasury feasibility by c
    if bool(p.get("treasury_cap", True)):
        u_cap = float(p["u_max_base"]) * cg
    else:
        u_cap = np.full_like(cg, float(p["u_max_base"]))
    feasible_u = (uA[None, :] <= u_cap[:, None] + 1e-9)
    feasible_C = np.zeros((nc, nC), dtype=bool)
    for iu in range(nu):
        feasible_C[:, iu * nr:(iu + 1) * nr] = feasible_u[:, iu:iu + 1]

    noise_vals = np.array([-float(p["sigma_x"]), 0.0, +float(p["sigma_x"])])
    noise_probs = np.array([0.25, 0.50, 0.25])

    def ix(x):
        return np.clip(np.rint((x - xg[0]) / dx).astype(np.int32), 0, nx - 1)

    def ig(g):
        return np.clip(np.rint((g - gg[0]) / dg).astype(np.int32), 0, ng - 1)

    def ic(c):
        return np.clip(np.rint((c - cg[0]) / dc).astype(np.int32), 0, nc - 1)

    Xs = xs[:, None, None, None]
    Gs = gs[:, None, None, None]
    Cs = cs[:, None, None, None]
    U = uC[None, :, None, None]
    R = rC[None, :, None, None]
    A = aA[None, None, :, None]
    EPS = noise_vals[None, None, None, :]

    gp = float(p["mu_g"]) * Gs + float(p["spill_g"]) * Xs - float(p["k_r"]) * R + float(p["g_drift"])
    gp = np.clip(gp, 0.0, GMAX)

    inj = float(p["S0"]) * np.exp(-float(p["beta"]) * U) * (1.0 + float(p["phi_g"]) * Gs)
    xp = float(p["rho"]) * Xs + inj - float(p["k_a"]) * A + EPS
    xp = np.clip(xp, 0.0, XMAX)

    dep = float(p["dep0"]) + float(p["dep_x"]) * Xs
    cp = Cs + float(p["eta_a"]) * A + float(p["eta_u"]) * U - dep
    cp = np.clip(cp, 0.0, float(p["CMAX"]))

    j = ix(xp)
    k = ig(gp)
    m = ic(cp)
    k = np.broadcast_to(k, j.shape)
    m = np.broadcast_to(m, j.shape)
    next_idx = ((j * ng + k) * nc + m).astype(np.int32)

    delta = float(p["delta"])
    wC_x, wC_g = float(p["wC_x"]), float(p["wC_g"])
    wS_x, wS_g = float(p["wS_x"]), float(p["wS_g"])

    c_ind = np.clip(np.rint((cs - cg[0]) / dc).astype(np.int32), 0, nc - 1)

    def br_C(piS: np.ndarray, V: np.ndarray):
        idxs = next_idx[np.arange(nS)[:, None], np.arange(nC)[None, :], piS[:, None], :]
        ev = (V[idxs] * noise_probs).sum(axis=-1)
        base = (wC_x * xs + wC_g * gs)[:, None] + cC[None, :] + delta * ev
        feas = feasible_C[c_ind, :]
        costs = np.where(feas, base, base + 1e6)
        piC = np.argmin(costs, axis=1).astype(np.int32)
        return piC, np.min(costs, axis=1)

    def br_S(piC: np.ndarray, V: np.ndarray):
        idxs = next_idx[np.arange(nS)[:, None], piC[:, None], np.arange(na)[None, :], :]
        ev = (V[idxs] * noise_probs).sum(axis=-1)
        costs = (wS_x * xs + wS_g * gs)[:, None] + a_cost[None, :] + delta * ev
        piS = np.argmin(costs, axis=1).astype(np.int32)
        return piS, np.min(costs, axis=1)

    if continuation is not None and len(continuation["piC"]) == nS and len(continuation["piS"]) == nS:
        piC = np.array(continuation["piC"], dtype=np.int32).copy()
        piS = np.array(continuation["piS"], dtype=np.int32).copy()
    else:
        piC = np.zeros(nS, dtype=np.int32)
        piS = np.zeros(nS, dtype=np.int32)

    for _ in range(max_outer):
        V = np.zeros(nS)
        for __ in range(max_vi):
            piC_new, V_new = br_C(piS, V)
            if np.max(np.abs(V_new - V)) < tol:
                piC = piC_new
                break
            V = V_new
        else:
            piC = piC_new

        V = np.zeros(nS)
        for __ in range(max_vi):
            piS_new, V_new = br_S(piC, V)
            if np.max(np.abs(V_new - V)) < tol:
                piS = piS_new
                break
            V = V_new
        else:
            piS = piS_new

    return dict(x_grid=xg, g_grid=gg, c_grid=cg, piC=piC, piS=piS, uC=uC, rC=rC, a_actions=aA, params=p)

def v8_sim(sol: Dict, T: int = 240, seed: int = 42, x0: float = 0.10, g0: float = 0.40, c0: float = 0.75):
    p = sol["params"]
    xg, gg, cg = sol["x_grid"], sol["g_grid"], sol["c_grid"]
    dx = xg[1] - xg[0]
    dg = gg[1] - gg[0]
    dc = cg[1] - cg[0]
    nx, ng, nc = len(xg), len(gg), len(cg)

    rng = np.random.default_rng(seed)
    noise_vals = np.array([-float(p["sigma_x"]), 0.0, +float(p["sigma_x"])])
    noise_probs = np.array([0.25, 0.50, 0.25])

    x = np.zeros(T + 1)
    g = np.zeros(T + 1)
    c = np.zeros(T + 1)
    u = np.zeros(T + 1)
    r = np.zeros(T + 1)
    a = np.zeros(T + 1)

    x[0] = float(np.clip(x0, 0.0, float(p["XMAX"])))
    g[0] = float(np.clip(g0, 0.0, float(p["GMAX"])))
    c[0] = float(np.clip(c0, 0.0, float(p["CMAX"])))

    for t in range(T):
        ix0 = int(np.clip(int(np.rint((x[t] - xg[0]) / dx)), 0, nx - 1))
        ig0 = int(np.clip(int(np.rint((g[t] - gg[0]) / dg)), 0, ng - 1))
        ic0 = int(np.clip(int(np.rint((c[t] - cg[0]) / dc)), 0, nc - 1))
        s = (ix0 * ng + ig0) * nc + ic0

        icA = int(sol["piC"][s])
        ia = int(sol["piS"][s])

        u[t] = float(sol["uC"][icA])
        r[t] = float(sol["rC"][icA])
        a[t] = float(sol["a_actions"][ia])

        eps = float(rng.choice(noise_vals, p=noise_probs))
        inj = float(p["S0"]) * np.exp(-float(p["beta"]) * u[t]) * (1.0 + float(p["phi_g"]) * g[t])
        x[t + 1] = float(np.clip(float(p["rho"]) * x[t] + inj - float(p["k_a"]) * a[t] + eps, 0.0, float(p["XMAX"])))
        g[t + 1] = float(np.clip(float(p["mu_g"]) * g[t] + float(p["spill_g"]) * x[t] - float(p["k_r"]) * r[t] + float(p["g_drift"]), 0.0, float(p["GMAX"])))
        dep = float(p["dep0"] + p["dep_x"] * x[t])
        c[t + 1] = float(np.clip(c[t] + float(p["eta_a"]) * a[t] + float(p["eta_u"]) * u[t] - dep, 0.0, float(p["CMAX"])))

    return x, g, c, u, r, a

def v8_summarize_and_save(out: Path, tag: str, sol: Dict, sim, burn: int = 35) -> Dict:
    x, g, c, u, r, a = sim
    ed = ed_proxy_from_xc(x, c, lam=float(sol["params"]["ed_lambda_c"]))
    summ = dict(
        tag=tag,
        mean_ed=float(np.mean(ed[burn:])),
        mean_x=float(np.mean(x[burn:])),
        mean_g=float(np.mean(g[burn:])),
        mean_c=float(np.mean(c[burn:])),
        mean_u=float(np.mean(u[burn:-1])),
        mean_r=float(np.mean(r[burn:-1])),
        mean_a=float(np.mean(a[burn:-1])),
        acf1_x=acf1(x[burn:]),
        acf1_c=acf1(c[burn:]),
    )

    plt.figure(figsize=(6.8, 3.6))
    plt.plot(x)
    plt.axhline(0.10, linestyle="--")
    plt.title(f"V8 {tag}: pressure x")
    plt.xlabel("t")
    plt.ylabel("x")
    plt.tight_layout()
    plt.savefig(out / f"v8_{tag}_pressure.png", dpi=220)
    plt.close()

    plt.figure(figsize=(6.8, 3.6))
    plt.plot(c)
    plt.title(f"V8 {tag}: capacity c")
    plt.xlabel("t")
    plt.ylabel("c")
    plt.tight_layout()
    plt.savefig(out / f"v8_{tag}_capacity.png", dpi=220)
    plt.close()

    plt.figure(figsize=(6.8, 3.6))
    plt.plot(ed)
    plt.axhline(ED_2024_25, linestyle="--")
    plt.title(f"V8 {tag}: ED proxy")
    plt.xlabel("t")
    plt.ylabel("ED≤4h")
    plt.tight_layout()
    plt.savefig(out / f"v8_{tag}_edproxy.png", dpi=220)
    plt.close()

    pd.DataFrame({"t": np.arange(len(x)), "x": x, "g": g, "c": c, "u": u, "r": r, "a": a, "ed_proxy": ed}).to_csv(
        out / f"v8_{tag}_timeseries.csv", index=False
    )
    return summ

def v8_scenarios(p0: Dict) -> Dict[str, Dict]:
    sc = {}
    sc["baseline"] = p0.copy()

    p = p0.copy()
    p["treasury_cap"] = False
    sc["treasury_relax"] = p

    p = p0.copy()
    p["eta_a"] = float(p0["eta_a"]) * 1.5
    p["dep0"] = float(p0["dep0"]) * 0.85
    sc["capacity_build"] = p

    p = p0.copy()
    p["burden_u"] = 0.35
    p["burden_a"] = 0.35
    p["eta_a"] = float(p0["eta_a"]) * 0.75
    sc["audit_heavy"] = p

    p = p0.copy()
    p["S0"] = float(p0["S0"]) * 0.90
    p["spill_g"] = float(p0["spill_g"]) * 0.90
    p["phi_g"] = float(p0["phi_g"]) * 0.75
    p["k_r"] = float(p0["k_r"]) * 1.25
    p["k_a"] = float(p0["k_a"]) * 1.25
    p["burden_a"] = 0.10
    p["eta_a"] = float(p0["eta_a"]) * 1.35
    p["dep0"] = float(p0["dep0"]) * 0.90
    sc["governance_package"] = p

    return sc

def v8_write_bundle(outdir: str) -> pd.DataFrame:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    p0 = v8_params_fast()
    sol0 = v8_solve(p0, continuation=None)
    sim0 = v8_sim(sol0, T=180, seed=42, x0=0.10, g0=0.40, c0=0.75)
    base = v8_summarize_and_save(out, "int_baseline", sol0, sim0)
    rows = [base]

    cont = {"piC": sol0["piC"], "piS": sol0["piS"]}
    for name, p in v8_scenarios(p0).items():
        if name == "baseline":
            continue
        sol = v8_solve(p, continuation=cont)
        sim = v8_sim(sol, T=180, seed=42, x0=0.10, g0=0.40, c0=0.75)
        rows.append(v8_summarize_and_save(out, f"int_{name}", sol, sim))
        cont = {"piC": sol["piC"], "piS": sol["piS"]}

    df = pd.DataFrame(rows)
    df.to_csv(out / "v8_interventions_summary_fast.csv", index=False)

    # summary plots
    d = df.sort_values("mean_ed", ascending=False)
    plt.figure(figsize=(9.0, 3.8))
    plt.bar(np.arange(len(d)), d["mean_ed"].to_numpy())
    plt.xticks(np.arange(len(d)), d["tag"].to_numpy(), rotation=45, ha="right", fontsize=8)
    plt.axhline(ED_2024_25, linestyle="--")
    plt.title("V8 interventions (mean ED proxy)")
    plt.ylabel("mean_ed")
    plt.tight_layout()
    plt.savefig(out / "v8_interventions_mean_ed_fast.png", dpi=220)
    plt.close()

    d = df.sort_values("mean_c", ascending=False)
    plt.figure(figsize=(9.0, 3.8))
    plt.bar(np.arange(len(d)), d["mean_c"].to_numpy())
    plt.xticks(np.arange(len(d)), d["tag"].to_numpy(), rotation=45, ha="right", fontsize=8)
    plt.title("V8 interventions (mean capacity)")
    plt.ylabel("mean_c")
    plt.tight_layout()
    plt.savefig(out / "v8_interventions_mean_capacity_fast.png", dpi=220)
    plt.close()

    plt.figure(figsize=(6.6, 4.2))
    plt.scatter(df["mean_c"], df["mean_ed"])
    for _, row in df.iterrows():
        plt.text(row["mean_c"], row["mean_ed"], str(row["tag"]).replace("int_", ""), fontsize=7)
    plt.axhline(ED_2024_25, linestyle="--")
    plt.xlabel("mean capacity c")
    plt.ylabel("mean ED proxy")
    plt.title("V8: ED proxy vs capacity")
    plt.tight_layout()
    plt.savefig(out / "v8_scatter_ed_vs_capacity_fast.png", dpi=220)
    plt.close()

    return df
