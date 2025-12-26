# Game-Theoretic Simulation Checklist (Batch 5): Stage-Game Timeline & State Vector

**Source:** User provided text (December 2025)
**Context:** Formal stage-game specification, compact state vector, transition functions, and payoff templates for an agent-based or Markov game implementation.

---

## 1) Time structure

| Layer | Index | Purpose | What changes here |
| :--- | ---: | :--- | :--- |
| **Operational** | month `t` | queues, capacity use, coding/claims, cashflow | demand shocks, admissions/LOS, coding, interim payments, public signals |
| **Financial** | year `Y` | reconciliation + cap/redistribution + true-ups | annual true-up, cap kink/redistribution, annual audit outcomes |
| **Constitutional** | agreement cycle `G` (e.g., 5y) | renegotiation / schedule extension | contribution shares, cap design, side-payments, rule tweaks |

---

## 2) Monthly stage game (within-year repeated game)

### Stage timeline (one month `t`)

| Stage | Move order | Information at this point | Decision variables (examples) | State updates (examples) |
| ---: | :--- | :--- | :--- | :--- |
| 0 | World | Everyone sees last month’s published metrics + own internal data | – | advance calendars; apply lags; roll forward cumulative counters |
| 1 | Nature | Demand shock realised: `ε_t` (may be partially observed) | – | arrival streams for ED + elective demand; inflation/price drift (if monthly) |
| 2 | State/Territory (principal) | Knows own cash position, queues, capacity, election clock; uncertain about others’ internal constraints | `B_jt` internal allocations to LHNs; elective target rules; surge directives; capacity investment orders (with lags); disclosure stance | internal budgets/targets set; investment pipeline updated |
| 3 | LHNs / Hospitals (agents) | Observe own queues, staffing, demand signals; imperfectly observe future audits and next-year rules | admissions thresholds; scheduling; LOS management; substitution settings; coding governance effort `g_pt`; “classification shifting” choices (ABF vs block vs other stream) | episodes generated; throughput; queue changes; quality pressure metrics |
| 4 | Claims submission | Claims reflect coding intensity `θ_pt` within feasibility bounds | choose coding intensity (bounded); documentation effort; claim timing | NWAU computed from episodes + coding; measurement error introduced |
| 5 | NHFP payment engine (referee) | Applies deterministic rules to submitted activity | – | interim payments; cash positions; cumulative cap-used counters |
| 6 | Audit / integrity (optional explicit player) | Sees anomaly signals; chooses targeting | audit targeting `A_t`; thresholds | detections/repayments/penalties; update perceived audit risk |
| 7 | Public signal release | Everyone observes published signals (some lagged/aggregated) | – | belief updates (Bayesian or heuristic); reputation/political salience updates |
| 8 | Transition | – | – | carry-forward state to next month |

---

## 3) Annual stage (reconciliation + cap/redistribution + reset)

At end of each year `Y` (or at a reconciliation boundary), run this “year-end game within the repeated game”:

| Step | What happens | Inputs | Outputs/state updates |
| ---: | :--- | :--- | :--- |
| A1 | **Annual reconciliation** | submitted vs revised activity; lags; dispute outcomes | true-up payments, revised entitlements, corrections to cumulative counters |
| A2 | **Cap + redistribution** | cap design parameters; total growth and shares | marginal funding kink realised; redistribution amounts assigned |
| A3 | **Audit outcomes finalised** | audit pipeline, disputes, repayments | net penalties/repayments; update compliance reputations |
| A4 | **Budget closure** | state fiscal constraints; Commonwealth fiscal stance | end-year deficits/surpluses; political utility impacts |
| A5 | **Next-year expectations formed** | published year-end results; policy chatter | belief priors for next year (NEP path, enforcement stance, negotiation probabilities) |

---

## 4) Agreement-cycle stage (renegotiation / extension bargaining)

Run every `G` years (or whenever a “schedule extension / crisis” trigger occurs):

| Stage | Game form | Players | What’s chosen | What updates |
| ---: | :--- | :--- | :--- | :--- |
| G1 | Alternating-offers bargaining (deadline) | Commonwealth ↔ States/Territories | contribution shares; cap design; side-payments; rule changes; integrity regime | new parameter set for next cycle |
| G2 | Outside options realised | same | walk-away / interim extension | fallback rule-set (extension), political costs |
| G3 | Ratification & signalling | same | public commitments | belief resets + reputational terms |

---

## 5) Compact state vector (code-ready)

### Global / rule-set state `R_t`

| Symbol | Type | Meaning |
| :--- | :--- | :--- |
| `NEP_t` | float | national efficient price (or price index) |
| `W_t` | dict | weight system / grouper parameters for NWAU calculation |
| `elig_t` | dict | eligibility rules (ABF vs block vs other stream) |
| `alpha_t[j]` | float | Commonwealth share / contribution parameters by jurisdiction |
| `cap_t` | dict | cap design params (rate, base, redistribution rule, kink shape) |
| `recon_t` | dict | reconciliation lag structure, revision probabilities, dispute rules |
| `audit_policy_t` | dict | baseline audit intensity, targeting logic, penalty schedule |
| `bargain_state_t` | dict | where you are in the agreement cycle (time-to-deadline, offers on table) |

### For each jurisdiction `j`: fiscal + political + beliefs `J_t[j]`

| Symbol | Type | Meaning |
| :--- | :--- | :--- |
| `cash_jt` | float | cash position / liquidity |
| `own_spend_jt` | float | state-funded spend this year-to-date |
| `cum_nwau_jt` | float | cumulative NWAU (or eligible NWAU) this year-to-date |
| `cap_used_jt` | float | cap consumption metric needed for kink/redistribution |
| `queue_metrics_jt` | dict | headline KPIs (elective breaches, ED LOS, ramping proxy, etc.) |
| `pol_jt` | dict | political state: election clock, salience weights, reputation |
| `beliefs_jt` | dict | beliefs about demand growth, others’ constraints, audit risk, next-year rules |

### For each provider/LHN `p` within `j`: operations + coding + capacity `P_t[p]`

| Symbol | Type | Meaning |
| :--- | :--- | :--- |
| `cap_pt` | dict | capacity state (beds/ICU/theatres/workforce) |
| `inv_pipe_pt` | dict | capacity investments in pipeline with lags |
| `q_ed_pt` | float | ED queue state (or arrival + backlog) |
| `q_el_pt[u]` | float | elective queue by urgency class `u` |
| `mix_pt` | vector | case-mix distribution over DRGs/service lines |
| `cost_pt` | dict | cost structure (fixed/variable, efficiency parameter) |
| `theta_pt` | float | coding intensity (bounded) |
| `g_pt` | float | governance/documentation effort (affects feasible coding + audit risk) |
| `quality_pt` | dict | endogenous quality state (pressure → adverse events proxy) |
| `contract_pt` | dict | internal contract terms/targets from jurisdiction |
| `beliefs_pt` | dict | local beliefs about demand, audits, budgets |

### Lags / measurement layer `M_t`

| Symbol | Type | Meaning |
| :--- | :--- | :--- |
| `claims_lag_t` | queue | pipeline of submitted claims pending reconciliation |
| `signal_lag_t` | queue | what gets published when (lags/aggregation) |
| `revision_model_t` | dict | probability of later revisions by class/provider |

---

## 6) Transition functions (what updates the state)

| Function | Inputs | Outputs |
| :--- | :--- | :--- |
| `demand_step(S_t, seed)` | `S_t` | arrivals `λ_t`, realised shocks `ε_t` |
| `policy_step(S_t)` | `S_t` | updates to any monthly policy knobs (if any) |
| `jurisdiction_move(S_t)` | `S_t` | `B_jt`, targets, directives, investment orders |
| `provider_move(S_t)` | `S_t` | admissions/scheduling/LOS decisions; `theta_pt`, `g_pt`, stream-shifting |
| `ops_queue_update(S_t)` | decisions + capacity + arrivals | updated queues, throughput, congestion metrics |
| `nwau_calc(S_t)` | episodes + coding + rules | `nwau_pt`, eligible splits by stream |
| `payment_engine(S_t)` | eligible NWAU + cap state + rules | interim payments, cash updates, cap_used updates |
| `audit_step(S_t, seed)` | activity + anomalies + audit_policy | detections, penalties/repayments, updated perceived risk |
| `publish_signals(S_t)` | signal lag rules | observed signals for belief updates |
| `belief_update(S_t)` | observed signals + priors | updated beliefs (Bayesian or heuristic) |
| `year_end_reconciliation(S_Y)` | claims pipeline + revisions/disputes | true-up payments, corrected NWAU, redistribution, reset counters |

---

## 7) Invariants (sanity checks you should enforce)

| Invariant | Check |
| :--- | :--- |
| Non-negative entitlements | payments ≥ 0 unless explicit recovery/repayment |
| Mass-balance of activity | NWAU derived only from generated episodes; no “free” NWAU |
| Capacity feasibility | throughput ≤ feasible capacity given staffing and beds |
| Bounded coding | `theta_pt` within [min,max] and constrained by documentation/governance |
| Queue consistency | queues update with arrivals − served + deferrals; never negative |
| Cap accounting consistency | cap_used updates match eligible growth definition exactly |
| Reconciliation traceability | every year-end adjustment maps to a claim in the lag pipeline |
