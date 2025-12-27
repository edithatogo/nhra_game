# Protocol: Modelling the NHRA Strategic Landscape (ODD Protocol v1.0)
**Author:** Dylan A Mordaunt

## 1. Purpose
The purpose of this model is to investigate the emergent strategic behavior of healthcare providers (Local Health Networks, LHNs) and jurisdictions (States/Territories) within the incentive framework defined by the National Health Reform Agreement (NHRA). Specifically, the model aims to quantify the conditions under which "Strategic Gaming" becomes a dominant equilibrium over "High Reliability" clinical performance, and to evaluate the sensitivity of the system to policy interventions such as increased audit pressure or transparency surges.

## 2. Entities, State Variables, and Scales

### 2.1 Entities
1.  **The Commonwealth:** The primary principal, setting the National Efficient Price (NEP) and audit policies.
2.  **State/Territory Governments:** Intermediary agents responsible for LHN budget allocation and data certification.
3.  **Local Health Networks (LHNs):** Primary agents responsible for service delivery and clinical documentation.
4.  **The NHFP Payment Engine:** A rule-based referee applying statutory formulae.

### 2.2 State Variables
*   **System Pressure ($P$):** A composite index derived from occupancy, ambulance offload delay, and discharge lag.
*   **Coding Intensity ($	heta$):** The level of documentation detail provided for ABF claims.
*   **Reputation Score ($R$):** A cumulative index based on public safety/quality signals (e.g., PSI-90).
*   **Efficiency Gap ($G$):** The divergence between actual input costs and the NEP.

## 3. Process Overview and Scheduling
The model operates on a monthly time-step ($t$) within an annual financial cycle ($Y$). The sequence of events in each step is:
1.  **Demand Realization:** Stochastic arrivals generated for ED and elective streams.
2.  **Jurisdiction Move:** States set internal budget targets and capacity directives based on fiscal constraints and political capital.
3.  **Provider Move:** LHNs observe their internal state and choose strategic actions (Admissions, Discharge, Coding Intensity).
4.  **Payment Processing:** The NHFP engine calculates interim NWAU payments based on submitted activity and NEP.
5.  **Audit Step:** An optional stochastic move where the regulator selects claims for data quality verification.
6.  **Belief Update:** Players update their internal beliefs about opponent strategies and future audit risks based on released signals.

## 4. Design Concepts

### 4.1 Emergence
Strategic Gaming behaviors emerge as a rational response to the interaction between the 6.5% growth cap and the noisy safety-based penalty mechanisms.

### 4.2 Sensing
Agents sense the system state via noisy signals (e.g., lagged performance reports) rather than perfect information.

### 4.3 Interaction
The model explicitly represents the multi-layered principal-agent interaction between the three levels of government.

## 5. Implementation
The model is implemented in Python as a hybrid Agent-Based / System Dynamics simulation. All parameters are tracked in the `context/04_parameter_registry.csv` and grounded in empirical data from IHACPA and AIHW.
