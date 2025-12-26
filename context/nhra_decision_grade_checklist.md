# Game-Theoretic Simulation Checklist (Batch 3): Decision-Grade Upgrades

**Source:** User provided text (December 2025)
**Context:** Making the simulation identifiable, testable, and policy-useful. Focus on incentives, operations, and validation.

---

## 1) Improve the game design (so incentives are realistic)

| Improvement | What to implement | Why it matters |
| :--- | :--- | :--- |
| **Multi-level principals/agents** | Commonwealth ↔ State Health Depts ↔ LHNs/Networks ↔ Hospitals ↔ clinical units | Most “gaming” and operational trade-offs happen below the state level; this lets you model internal contracting, not just intergovernmental bargaining. |
| **Hybrid time scales** | Monthly cashflow decisions + annual reconciliation + 5-year renegotiation | Captures timing games (month/EOFY) and long-horizon bargaining/credible threats. |
| **Incomplete contracts + renegotiation** | Allow “rule changes”/side deals after shocks (bargaining stage) | NHRA-like systems are not fully commitment-based; renegotiation is a feature, not a bug. |
| **Explicit information structure** | Who knows what, when (true costs, demand, coding options, audit thresholds) | Without this you can’t model signalling, screening, or strategic disclosure. |
| **Multiple strategy channels** | Volume, case-mix, coding intensity, classification (ABF vs block), deferral, substitution | Otherwise your equilibrium will be unrealistically “all volume growth”. |

## 2) Make payoffs less naïve (and more like real decision-making)

| Improvement | What to add to utilities | Why it matters |
| :--- | :--- | :--- |
| **Multi-objective utility** | Budget + access targets + quality/safety + political/reputational costs | Prevents degenerate equilibria where players always maximise dollars at any service-quality cost. |
| **Nonlinear political loss functions** | Steep penalty when ED wait/ambulance ramping/ elective breaches cross thresholds | Real systems react to *threshold breaches*, not smooth marginal changes. |
| **Risk and ambiguity aversion** | Penalise variance/uncertainty in future funding and audits | Drives conservative behaviour and “buffer building” that you see in practice. |
| **Fairness / equity weights** | Equity-adjusted welfare or explicit penalties for inequitable outcomes | Lets you test whether reforms improve equity vs just shift burden. |

## 3) Add realism to operations (queues/capacity), not just funding

| Improvement | Implementation | What you gain |
| :--- | :--- | :--- |
| **Queueing / congestion model** | Simple M/M/s or discrete-event queues for ED + electives | Converts “activity” into **waiting times**, cancellations, and access KPIs. |
| **Capacity constraints with adjustment costs** | Workforce/beds/OT with ramp-up friction and hiring lag | Stops instant “just add activity” behaviour; produces plausible dynamics. |
| **Substitution across settings** | ED ↔ short stay ↔ inpatient; hospital ↔ community; public ↔ private | Lets you see cost-shifting and avoidance strategies. |
| **Quality as endogenous** | Link throughput pressure to readmission/complications | Reveals when incentives trade access for quality. |

## 4) Strengthen the “gaming” layer (so it’s measurable and falsifiable)

| Improvement | What to model | Output you should track |
| :--- | :--- | :--- |
| **Audit as a strategic player** | Audit probability and targeting adapts to anomalies | Endogenous deterrence; realistic “arms race.” |
| **Coding as a constrained optimisation** | Coding discretion bounded by clinical record quality and audit risk | Avoids unrealistic unlimited upcoding. |
| **Measurement error + revision processes** | Late corrections, dispute rates, lagged data | Produces reconciliation volatility like the real world. |
| **Integrity constraints** | Hard constraints: mass-balance, eligibility logic, episode rules | Prevents impossible equilibria and improves credibility. |

## 5) Improve calibration, validation, and experiment design

| Improvement | How to implement | Why it matters |
| :--- | :--- | :--- |
| **Calibrate to multiple targets** | Match (i) total spend, (ii) NWAU growth, (iii) mix distribution, (iv) waitlist KPIs | Prevents “fits one metric, fails the rest.” |
| **Out-of-sample validation** | Train on earlier years; test on later shocks | Demonstrates predictive plausibility. |
| **Structural sensitivity analysis** | Vary not just parameters, but *mechanisms* (cap rules, audit regime, info timing) | Policy decisions change rules, not just numbers. |
| **Scenario library** | Standardised counterfactuals: cap removed, different contribution rates, stronger audits, different NEP trajectories | Makes results interpretable for negotiation and reform. |

## 6) Make it implementable and reproducible (so you can iterate fast)

| Improvement | What to do | Benefit |
| :--- | :--- | :--- |
| **Modular architecture** | Separate “Rules engine” (payments) from “Agents” (strategies) from “World” (demand/capacity) | Lets you swap NHRA variants without rewriting everything. |
| **Configuration-driven experiments** | YAML/JSON scenarios; seeds fixed; deterministic accounting | Easy batch runs + traceability. |
| **Explainability hooks** | Log “why” an agent chose an action (marginal payoff decomposition) | Lets you defend results to stakeholders. |
| **Equilibrium sanity checks** | Invariants + stress tests (no negative entitlements, conservation of activity, bounded utilities) | Catches silent model failures. |
