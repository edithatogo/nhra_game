# Game-Theoretic Simulation Checklist: NHRA

**Source:** User provided text (December 2025)
**Context:** Strategic modelling of Pricing, Activity Growth, Caps, Coding, Reconciliation, and Renegotiation.

---

## Inputs to model (state variables, parameters, data)

| Input group | What to include (variables/parameters) | Why it matters (strategic content) | Typical granularity |
| :--- | :--- | :--- | :--- |
| **Players & objectives** | Commonwealth; each State/Territory; (optionally) Local Hospital Networks / Health Services; IHACPA (price setter); NH Funding Pool Administrator/NHFB (calculator/payer); auditors | Defines strategy spaces and payoff functions; separates **rule-setters** (pricing) from **strategic actors** (funders/providers) | Jurisdiction × year/quarter |
| **Funding policy parameters** | Commonwealth contribution rate(s) (e.g., share of “efficient growth”); cap parameters (annual/cumulative; soft vs national cap); any one-off top-ups/side payments | These are the “rules of the game” that create incentives for activity growth, cost control, and bargaining | Jurisdiction × year |
| **Pricing & weights** | NEP/NEC; price weights and adjustments; eligibility rules (ABF vs block-funded categories); outlier policies | Creates incentives for **service mix**, **coding intensity**, and **substitution across settings** | Service category × year |
| **Activity & case-mix** | Baseline NWAU volume; growth trend; case-mix distribution; DRG/service-line mix; emergency/elective split | Strategic lever: states/providers can grow activity, shift mix, or change recorded complexity to affect payments | Hospital/LHN × month/quarter (or state-level if simplified) |
| **Cost structure & capacity** | Cost per NWAU distribution; fixed/variable split; workforce constraints; bed/ICU capacity; productivity/efficiency trajectories | Determines whether “efficient growth” is feasible, and whether growth is real capacity or “paper activity” | LHN/hospital × period |
| **Demand drivers & shocks** | Population growth/ageing; inflation; epidemics; policy shocks; seasonal demand | Forces off-equilibrium behaviour and stress-tests bargaining/cap mechanisms | State × period |
| **Information & measurement error** | True cost vs reported cost; coding discretion; lagged data; forecasting error in entitlements | Core for game theory: incomplete information enables **signalling**, **screening**, and **gaming** | Variable-specific |
| **Compliance & audit regime** | Audit probability; detection sensitivity; penalties/repayments; reputational costs | Governs whether coding/mix gaming is optimal vs too risky | State/service × period |
| **Political constraints** | Electoral cycle proxy; salience of waiting lists; media penalty; intergovernmental relationship costs; bargaining power | Converts “budget maximisation” into realistic utilities: avoid deficits *and* avoid political pain | State × period |
| **Cross-system substitution** | Private hospital capacity; primary care access; aged care/NDIS interface; ambulance/ED pathways | Enables modelling **cost shifting** and “dumping” incentives between funders/programs | State × period |

---

## Mechanisms to model (institutional rules + strategic “games”)

| Mechanism (institutional feature) | Real-world analogue | How to represent in a game-theory simulation | Key behaviours it enables |
| :--- | :--- | :--- | :--- |
| **Activity-Based Funding payment rule** | Payments driven by **NEP × NWAU** for eligible services | Stage: players choose activity/mix/coding → NWAU realised → payments calculated | Activity inflation; service substitution; coding intensity |
| **Block funding rule for ineligible/other services** | Some services/functions funded by block (IHACPA eligibility rules; NHFP calculates payments) | Separate budget constraint + different marginal incentive (near-zero marginal revenue) | Shifting services between ABF/block categories |
| **“Efficient growth” concept** | Commonwealth funds a share of “efficient growth” under addendum rules | Define counterfactual efficient cost frontier; payoffs depend on distance to frontier | Incentive to claim growth is “efficient”; invest in efficiency vs volume |
| **Funding cap and redistribution** | 6.5% cap + reconciliation redistribution mechanics | Cap as piecewise payoff kink: marginal Commonwealth $ drops after cap; redistribution as contestable pool | Race-to-cap dynamics; strategic timing of activity |
| **Annual reconciliation** | Ex-post adjustment of entitlements and payments | Repeated game: period t actions affect period t+1 transfers; include lag | End-of-year “activity surges”; smoothing/manipulation |
| **Price setting & updates** | IHACPA annual NEP determinations | Exogenous/leader move (Stackelberg): IHACPA sets price; others respond | Anticipation effects; lobbying/signalling to influence future prices |
| **Transparency & oversight** | NHFB/NHFP reporting; Administrator independence | Public signals update beliefs (Bayesian learning); reputational utility term | Strategic reporting; “performative compliance” |
| **Renegotiation / extension** | Addendum extended (Schedule K) while negotiating a new agreement | Bargaining game with outside options, deadlines, and asymmetric impatience | Brinkmanship; hold-out; side-payments |
| **Special purpose/side payments** | One-off boosts / additional funding agreements | Transfer shocks contingent on agreement state; can be modelled as bargaining outcomes | “Compensation” for caps; political settlement payments |
| **Audit/enforcement** | Coding/eligibility audits (if modelled) | Principal-agent: stochastic detection + penalty; choose audit intensity | Deterrence vs gaming equilibrium |
| **Cost shifting between programs** | Spillovers to Commonwealth programs or other systems | Multi-budget environment: each actor minimises own cost subject to outcomes | ED boarding, premature discharge, “hospital avoidance” narratives |

---

## Outputs to model (what your simulation should produce)

| Output domain | Outputs (model observables) | What they diagnose |
| :--- | :--- | :--- |
| **Funding flows** | Commonwealth payments by state; state own-source hospital spend; net transfers; reconciliation adjustments; distribution of “redistribution amount” | Who pays, who benefits, and how cap/reconciliation changes incentives |
| **Activity & mix** | Total NWAU; NWAU by service category; growth rates; elective vs emergency volumes; average complexity | Whether actors respond by **real growth** or **mix/coding shifts** |
| **Efficiency & cost** | Cost per NWAU; distance to efficient frontier; fixed-cost absorption; productivity trend | Whether the model produces “efficient growth” vs cost blowouts |
| **Access & timeliness** | Waiting list size; time-to-treatment; ED LOS; bed occupancy; diversion rates | Whether funding rules drive access improvements or queue shifting |
| **Quality & safety** | Readmissions, complications, mortality proxies, sentinel events; patient-reported outcomes (if included) | Whether volume incentives create quality trade-offs |
| **Equity** | Outputs by region/SES/Indigenous status (if stratified); rural access metrics | Whether incentives widen or reduce disparities |
| **Strategic behaviour indicators** | Coding intensity index; upcoding probability; end-of-period activity spikes; service shifting to ABF-eligible categories | “Gaming” signatures and where they emerge |
| **Political/utility outcomes** | Actor utilities (budget + access + political cost); probability of renegotiation breakdown; stability of agreements | Whether equilibrium is cooperative, conflictual, or unstable |
| **System spillovers** | Primary care burden; private sector substitution; aged care/NDIS spillovers | Whether the NHRA incentives displace costs rather than reduce them |
