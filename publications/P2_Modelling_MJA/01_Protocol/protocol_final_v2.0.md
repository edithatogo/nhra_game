# Protocol: Modelling the NHRA Strategic Landscape (Final ODD Protocol v2.0)

**Author:** Dylan A Mordaunt

## 1. Purpose

The purpose of this model is to investigate the emergent strategic behavior of healthcare providers (Local Health Networks, LHNs) and jurisdictions (States/Territories) within the incentive framework defined by the National Health Reform Agreement (NHRA). Specifically, the model aims to quantify the conditions under which **Strategic Gaming** (the optimization of metric reporting over substantive system performance) becomes a dominant equilibrium.

## 2. Entities, State Variables, and Scales

### 2.1 Entities

1. **The Commonwealth (Principal):** Sets the National Efficient Price (NEP) and high-level funding caps.
2. **The Auditor (Strategic Player):** A specialized Commonwealth agency that selects claims for audit based on anomaly signals and a finite budget.
3. **State/Territory Governments (Agents):** Manage internal budget allocations and certify LHN activity.
4. **Local Health Networks (Sub-agents):** Primary providers who choose clinical documentation, service stream substitution, and operational effort.

### 2.2 State Variables

* **System Pressure ($P$):** A composite index derived from occupancy and offload delay.
* **Coding Intensity ($ heta$):** Strategic choice level for documentation detail.
* **Reputation Score ($R$):** Public ranking based on published signals.
* **Efficiency Gap ($G$):** Divergence between marginal revenue (NEP) and marginal cost.

## 3. Process Overview and Scheduling

The model operates on a monthly time-step. The sequence is:

1. **Nature:** Stochastic demand shocks realized.
2. **State Move:** Allocation of budgets ($B_j$) and setting of elective targets.
3. **LHN Move:** Choosing coding intensity ($ heta$), discharge effort ($e_{disc}$), and service substitution ($s_{abf}$).
4. **Auditor Move:** Selecting audit targeting ($A_t$) based on $ heta$ variance.
5. **Payoff Realization:** Financial transfers processed; reputation scores updated.

## 4. Design Concepts

* **Interaction:** Multi-layered principal-agent-subagent hierarchy.
* **Emergence:** Gaming equilibria emerge when reputational payoffs are high relative to audit probability.
* **Sensing:** Agents update beliefs about audit thresholds based on lagged feedback.

## 5. Submodels (Details)

### 5.1 Pressure-to-Risk Mapping

System pressure ($P$) is mapped to clinical risk using a logistic transfer function calibrated to historical within-4-hour ED performance.

### 5.2 The Gaming Payoff Matrix

The payoff for gaming ($U_{game}$) is weighted by $\alpha$ (Revenue) and $\beta$ (Reputation) minus the risk-adjusted expected penalty ($\delta$).

## 6. Implementation

The model is implemented in Python. Parameters are tracked in `context/04_parameter_registry.csv`.
