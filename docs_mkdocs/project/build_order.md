# Game-Theoretic Simulation Checklist (Batch 6): Priority Behaviours & Build Order

**Source:** User provided text (December 2025)
**Context:** Prioritisation of behaviors for implementation, focusing on policy relevance and "NHRA-shaped" incentives. Includes a phased build order.

---

## Priority behaviours

| Priority | Behaviour to reproduce | Why it’s top-tier | Minimal game lens | What to measure (signature outputs) |
| ---: | :--- | :--- | :--- | :--- |
| 1 | **Threshold & timing behaviour** (EOFY surges, smoothing, “race-to-cap”, claim timing) | It’s the cleanest fingerprint of caps + reconciliation + lags; drives big $ and real operational decisions | Kinked payoff + repeated game | Month-by-month NWAU spikes; cap consumption trajectory; reconciliation volatility; pre/post-threshold behaviour |
| 2 | **Coding intensity / complexity drift** (bounded upcoding, documentation effort, “creep”) | Explains systematic growth in measured complexity independent of true acuity; central to ABF incentives | Principal–agent (hidden effort) + audit risk | Coding intensity index; complexity inflation vs clinical proxies; audit yield/repayments |
| 3 | **ABF↔block (and boundary) shifting** (classification/venue shifting) | Eligibility boundaries create substitution incentives that look like “efficiency” but are often reclassification | Mechanism design / boundary game | Share of activity by stream; sudden shifts around rule changes; service-line boundary switches |
| 4 | **Capacity-constrained access dynamics** (queues, cancellations, ED crowding) | Converts dollars/NWAU into the outcomes everyone argues about; prevents unrealistic “free growth” | Congestion/queueing game | ED LOS distribution; elective breaches; occupancy; cancellation rates; ramping proxy |
| 5 | **Internal contracting / delegation** (State↔LHN↔hospital target games) | Most real decisions are internal: budget envelopes, targets, and blame-shifting; generates heterogeneity within states | Nested principal–agent | LHN-level variance; target chasing; internal transfer rules; localised surges/cuts |
| 6 | **Cost shifting & substitution across settings** (public↔private, hospital↔community, downstream spillovers) | Captures externalities and “moving the problem” rather than solving it | Common-pool + routing/substitution | Displacement indicators: ED avoidance, short-stay/inpatient substitution, private share shifts, readmission bounce-backs |
| 7 | **Audit / integrity “arms race”** (targeting adapts to gaming) | Turns gaming into a measurable equilibrium with policy levers (audit intensity, penalties) | Dynamic enforcement game | Detection rate vs intensity; deterrence curves; false-positive cost vs gaming reduction |
| 8 | **Renegotiation & side-payment dynamics** (extensions, settlement transfers, brinkmanship) | Important for long-run realism, but less necessary for first-pass operational accuracy | Bargaining / coalition game | Probability of renegotiation breakdown; size/frequency of side-payments; rule-regime switches |

---

## A pragmatic “build order”

### Core v1 (Must-Have)
**Focus:** Timing/Threshold (#1), Coding Drift (#2), Capacity/Queues (#4).
*   **State:** Time, Budget caps, Claim timing, NWAU, Coding intensity, Capacity utilization, Queue lengths.
*   **Actions:** Submit claim, Allocate capacity, Manage queues.

### v2 (High Value)
**Focus:** Boundary Shifting (#3), Internal Contracting (#5).
*   **State:** v1 State + Eligibility rules, Internal contract targets.
*   **Actions:** v1 Actions + Reclassify activity, Adjust internal targets.

### v3 (Policy Breadth)
**Focus:** Cost Shifting (#6), Audit Arms Race (#7).
*   **State:** v1/v2 State + Audit intensity, Penalty structure.
*   **Actions:** v1/v2 Actions + Adjust audit params, Gaming responses.

### v4 (Long-Horizon Realism)
**Focus:** Renegotiation & Side-Payments (#8).
*   **State:** v1/v2/v3 State + Renegotiation params, Side-payment rules.
*   **Actions:** v1/v2/v3 Actions + Initiate renegotiation, Offer/accept side-payments.
