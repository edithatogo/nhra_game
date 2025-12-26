# Game-Theoretic Simulation Checklist (Batch 4): "All-In" Spec

**Source:** User provided text (December 2025)
**Context:** Comprehensive specification for an "All-In" simulation, including inputs, decision variables, mechanisms, operations, outputs, and validation.

---

## 1) Inputs (exogenous state, parameters, data)

| Input group | What to include (examples) | Notes |
| :--- | :--- | :--- |
| **Players / institutions** | Commonwealth; each State/Territory; (optional) LHNs/hospitals; IHACPA (price/weights); National Health Funding Pool (NHFP) Administrator/NHFB (payments/reconciliation); auditors/regulators | IHACPA sets NEP that underpins ABF. NHFP Administrator is independent statutory office supporting payment/reconciliation functions. |
| **Agreement period & schedules** | NHRA baseline terms; Addendum (e.g., 2020–25); extension terms (e.g., Schedule K 2025–26); renegotiation deadlines | Schedule K extends arrangements for 1 Jul 2025–30 Jun 2026 and includes time-limited adjustments. |
| **Funding streams (3-stream)** | ABF stream; block funding stream; public health (if modelled as distinct stream) | ABF uses NEP × NWAU; block is for determined services/functions. |
| **Pricing & classification inputs** | NEP/NEC; NWAU calculators/weights/adjustments; classification rules; outlier rules | NEP & NWAU tooling are published by IHACPA. |
| **Policy parameters** | Contribution shares; cap parameters; reconciliation rules; dispute process parameters | Addendum includes a national growth cap (e.g., 6.5%/yr) and defines reconciliation. |
| **One-off adjustments / side-payments** | Fixed top-ups; special uplifts (e.g., NT uplift); earmarks | Schedule K (per NHFB corporate plan) describes one-time fixed funding and other one-offs for 2025–26. |
| **Demand drivers & shocks** | Population; morbidity; seasonality; pandemic-like shocks; inflation | Drives off-equilibrium stress tests; interacts with caps/queues. |
| **Capacity & adjustment frictions** | Beds, theatres, ICU, workforce; hiring/training lags; overtime costs; capital limits | Prevents unrealistic “instant growth”; generates queuing/congestion. |
| **Cost structure** | Fixed/variable costs; cost per NWAU distribution; efficiency frontier parameters | Needed to define “efficient growth” vs waste. |
| **Cross-system substitution** | Public ↔ private; hospital ↔ community/primary care; aged care/NDIS spillovers | Enables cost shifting and pathway substitution as strategic options. |
| **Information structure** | Who knows true demand/cost; reporting lags; measurement error; forecasting error | Required for signalling/screening; makes reconciliation non-trivial. |
| **Integrity/compliance regime** | Audit probability/targeting; detection sensitivity; penalties/repayments; dispute rates | Turns “gaming” into a constrained optimisation. |
| **Political/reputational constraints** | Election-cycle proxy; salience thresholds (ED, ramping, electives); media penalty; intergov relationship costs | Implements non-linear “pain” when KPI thresholds are breached. |
| **Mid-term review / scrutiny pressure** | Probability of adverse findings; adoption likelihood; reputational loss | Mid-Term Review is an identifiable external signal affecting beliefs/strategies. |

---

## 2) Agent decision variables (endogenous “strategy inputs” each period)

| Actor | Strategy channels to model | Typical constraints |
| :--- | :--- | :--- |
| **State/Territory (funder/operator)** | Activity targets; internal LHN budgets; elective scheduling; investment in capacity/efficiency; coding governance intensity; disclosure strategy; bargaining stance | Budget constraint; workforce constraints; KPI thresholds; political loss function |
| **LHNs / hospitals (agents)** | Case-mix choices; admission/LOS policies; theatre allocation; coding intensity (within bounds); shifting between ABF vs block-eligible activity; deferral/smoothing | Capacity/queues; audit risk; clinical constraints; internal contract rules |
| **Commonwealth** | Enforcement stance; willingness to side-pay/top-up; bargaining posture for new schedules; (if modelled) audit funding or integrity emphasis | Political utility; fiscal constraints; intergovernmental bargaining costs |
| **IHACPA (leader/stackelberg)** | NEP/weights updates (exogenous or strategic); eligibility determinations (esp. block) | Often treated as ruleset/leader rather than payoff-maximiser |
| **NHFP Administrator/NHFB (referee)** | Payment cadence rules; reconciliation processing; integrity checks; dispute resolution throughput | Administrator/NHFB run payment/reconciliation system functions. |
| **Auditor/integrity actor (optional explicit player)** | Audit targeting intensity; thresholds; penalties | Resource constraint; false positive/negative trade-off |

---

## 3) Mechanisms (rules engine + strategic “games”)

| Mechanism | How to model it | Why it’s high leverage |
| :--- | :--- | :--- |
| **ABF payment rule** | Payments = NEP × realised NWAU (with adjustments) | Core incentive for volume/mix/coding. |
| **Block funding eligibility + payment** | IHACPA determines block-eligible services/functions; Administrator calculates block contributions | Creates a boundary where strategic “classification shifting” happens. |
| **Tri-stream choice (ABF vs block vs public health)** | Let actors allocate marginal effort/volume across streams with different marginal returns | Captures “venue shifting,” not just volume growth. |
| **Efficient growth accounting** | Efficient cost frontier; Commonwealth share applies to “efficient growth” definition | Prevents treating all growth as fundable; aligns incentives to efficiency. |
| **National growth cap + kinked payoffs** | Piecewise marginal funding: full rate until cap; reduced/zero after cap; include redistribution rules | Produces “race-to-cap” and timing games. Cap specified in Addendum (e.g., 6.5%/yr). |
| **Monthly payments + annual reconciliation loop** | Short-cycle cashflow + long-cycle true-up; lags and revisions | Generates end-of-period surges, smoothing, defensive reporting. |
| **Dispute resolution & data matching** | Probability of disputes; resolution delays; revisions | Small “business rules” changes can move large $ in reconciliation. |
| **Side-payments / one-off adjustments (Schedule K)** | Exogenous shock or bargaining settlement stage (transfer + conditions) | Strongly changes incentives for the year (e.g., top-up; NT uplift; equity commitments). |
| **Renegotiation / extension bargaining** | Alternating-offers bargaining with deadlines and outside options; asymmetric impatience | Captures brinkmanship and settlement dynamics during schedule transitions. |
| **Audit / integrity “arms race”** | Endogenous audit targeting responding to anomalies; expected penalty shapes coding strategies | Makes gaming measurable and policy-tunable (audit intensity vs behaviour). |
| **Transparency as public signals** | Publish KPI/funding signals → Bayesian belief updates → reputational utility impacts | Enables signalling/screening equilibria, not just complete-information play. |

---

## 4) Operational dynamics layer (so “activity” turns into access/quality)

| Operational module | What to include | What it prevents / enables |
| :--- | :--- | :--- |
| **Queues & congestion** | ED queue, elective queue; cancellations; M/M/s or discrete-event | Prevents “free” activity growth; yields waiting-time outcomes. |
| **Capacity with adjustment costs** | Hiring lags, overtime, bed expansion friction | Stops instant scale-up; produces realistic cycles. |
| **Substitution rules** | ED ↔ short stay ↔ inpatient; public ↔ private; hospital ↔ community | Captures cost shifting and avoidance strategies. |
| **Quality as endogenous** | Pressure → readmissions/complications; minimum quality constraints | Reveals access–quality trade-offs under funding pressure. |
| **Threshold-triggered political loss** | Step penalties when KPI thresholds are breached | Produces realistic “sudden priority shifts” rather than smooth optimisation. |

---

## 5) Outputs (what the simulation should report)

| Output domain | Primary outputs | “Gaming / integrity” signatures |
| :--- | :--- | :--- |
| **Funding flows** | Payments by stream (ABF/block/public health); by state/LHN; net transfers; reconciliation adjustments | Volatility of true-ups; dispute frequency; revisions |
| **Activity & case-mix** | NWAU volume; growth; DRG/service mix; elective/emergency split | Coding intensity index; complexity inflation; boundary switching (ABF↔block) |
| **Efficiency & cost** | Cost per NWAU; distance to frontier; fixed-cost absorption; productivity | “Paper efficiency” vs real efficiency (audit-adjusted) |
| **Access & timeliness** | Waiting lists; time-to-treatment; ED LOS; bed occupancy; ambulance offload delay (if modelled) | End-of-period surges; deferral/smoothing patterns |
| **Quality & safety** | Readmissions, complications, mortality proxies; patient outcomes (if included) | Quality degradation under throughput pressure |
| **Equity** | Stratified access/outcomes (region/SES/priority groups); equity-weighted welfare | Equity trade-offs under caps and scarcity |
| **Strategic stability** | Utilities by actor; cooperation vs conflict rate; renegotiation breakdown probability | Identifies unstable rulesets and perverse incentives |

---

## 6) Validation, stress-tests, and reproducibility (add all the “make it usable” improvements)

| Category | What to implement | Deliverable you should produce |
| :--- | :--- | :--- |
| **Calibration (multi-target)** | Fit simultaneously to spend, NWAU growth, mix, and access KPIs | Calibration report + fitted parameter set |
| **Out-of-sample validation** | Train on earlier years; test on later shocks | Predictive performance dashboard |
| **Structural sensitivity** | Vary *mechanisms* (cap form, audit regime, info timing), not just parameters | Tornado plots + scenario comparisons |
| **Scenario library (policy counterfactuals)** | Cap removed; different contribution shares; stronger audits; altered NEP paths; different schedule terms | A repeatable YAML/JSON catalogue of scenarios |
| **Modular architecture** | Separate rules engine / agents / world / measurement layer | Swap NHRA variants without rewrites |
| **Determinism & traceability** | Fixed random seeds; config-logged runs; invariant checks | Reproducible “run packets” (config + logs + outputs) |
| **Explainability hooks** | Log marginal payoff decomposition for each action | “Why did the agent do that?” audit trail |
| **Sanity/integrity tests** | Conservation checks; non-negative entitlements; bounded utilities; episode/eligibility invariants | Automated test suite gating model runs |
