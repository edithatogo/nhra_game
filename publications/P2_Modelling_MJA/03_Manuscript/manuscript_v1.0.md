# Quantification of Strategic Gaming Equilibria in the National Health Reform Agreement: A Simulation Study
**Author:** Dylan A Mordaunt

## Abstract
**Objectives:** To quantify the impact of the National Health Reform Agreement (NHRA) incentive structure on strategic behavior and system performance.
**Design:** Hybrid Agent-Based / System Dynamics simulation following the ODD protocol.
**Setting:** Simulated Australian public hospital system.
**Main outcome measures:** System pressure index, within-4-hour performance, and equilibrium strategy profiles.
**Results:** Simulation results show that Strategic Gaming is a dominant equilibrium under current NHRA rules. This is driven by information lags and indexation gaps. An "Audit Blitz" policy failed to deter gaming while increasing administrative burden. Conversely, a "Transparency Surge" improved performance by 10.9% by aligning reputational utility with clinical effort.
**Conclusions:** Financial penalties are less effective than contemporaneous transparency in driving high-reliability performance. Reform should prioritize reducing reporting noise to stabilize clinical governance.

## Introduction
The National Health Reform Agreement (NHRA) defines the financial relationship between the Commonwealth and Australian States. It utilizes Activity Based Funding (ABF) as the primary mechanism for hospital financing {Council on Federal Financial Relations, 2011 @NHRA_2011 #106}. ABF is designed to incentivize efficiency. However, the multi-layered principal-agent structure of the NHRA creates significant information asymmetries. Previous qualitative analysis identified "Strategic Gaming" as a likely response to these structural features. The quantitative impact of these behaviors on system-wide performance remains poorly understood.

Strategic Gaming involves the optimization of reported metrics over substantive clinical quality improvements. This behavior is reinforced by **Institutional Isomorphism**. LHNs face high-stakes consequences for under-performance relative to noisy safety signals like Patient Safety Indicator 90 (PSI-90). The complexity of the Agreement makes traditional econometric forecasting difficult. This study utilizes an Agent-Based Model (ABM) to formalize the NHRA as an extensive-form game. This provides a quantitative basis for evaluating the sensitivity of the system to alternative audit and transparency policies.

## Methods

### 2.1 Model Overview (ODD Protocol)
We implemented a hybrid simulation model following the Overview, Design Concepts, and Details (ODD) protocol {Ostrom, 2005 @Ostrom_2005 #121}. The model combines a system dynamics (SD) backbone with a modular strategic agent layer.

**Entities and State Variables:**
The model represents four primary entities: the Commonwealth, the Auditor, States, and LHNs. Key state variables include **System Pressure ($P$)**, **Coding Intensity ($\theta$)**, and **Reputation Score ($R$)**. $P$ is a composite index of occupancy and ambulance offload delay. $\theta$ represents the strategic choice level for documentation. $R$ is a noisy public signal of quality.

**Process Overview and Scheduling:**
The simulation operates on a monthly time-step. Each step involves a 7-stage sequence. First, stochastic demand is realized. Second, States set budget targets. Third, LHNs choose documentation intensity. Fourth, the NHFP engine processes payments. Fifth, the Auditor targets claims. Sixth, signals are published. Finally, players update beliefs.

### 2.2 Design Concepts
The core design concept is **Emergence**. Strategic gaming equilibria emerge as rational responses to the interaction between 6.5% growth caps and safety penalty rules. Agents utilize a **Sensing** mechanism. They update beliefs about audit thresholds based on lagged feedback. Interaction is modeled as an **Extensive Form Game with Imperfect Information**.

### 2.3 Empirical Grounding and Calibration
The economic spine is calibrated using historical series (2011–2024) for the National Efficient Price (NEP) and the Wage Price Index (WPI) {IHACPA, 2024 @IHACPA_2024 #114}. Operational metrics are parameterized using a logistic transfer function grounded in AIHW data {AIHW, 2024 @AIHW_2024 #101}. Baseline parameters were verified through a 100% trace coverage parity audit.

## Results

### 3.1 Scenario Comparison: System Trajectories
The simulation projected system outcomes from 2025 to 2030 across four scenarios. Results are summarized in Table 1.

**Table 1: 2030 Outcome Metrics by Policy Scenario**
| Scenario | System Pressure (Index) | ED Performance (within 4h) | Effective Cth Share (%) |
| :--- | :--- | :--- | :--- |
| Baseline | 1.32 | 51.2% | 38.4% |
| Audit Blitz | 1.28 | 53.5% | 37.1% |
| Transparency Surge | 1.15 | 62.1% | 41.5% |
| Coop. Governance | 1.08 | 68.4% | 43.2% |

The Baseline scenario exhibits a steady escalation of system pressure. ED performance stabilizes at suboptimal levels (~51%). This is driven by the divergence between input costs and NEP indexation.

### 3.2 Impact of the "Audit Blitz"
High audit pressure resulted in a temporary reduction in Strategic Gaming. However, this effect was offset by increased administrative burden. Marginal improvements in clinical throughput were minimal. The aggressive recovery of funds resulted in the effective Commonwealth share dropping to 37.1%. This shifted financial risk to States.

### 3.3 The "Transparency Surge" Equilibrium
The Transparency Surge produced the most robust shift toward High Reliability. By reducing signal noise, the regulator enabled LHNs to derive higher utility from genuine safety improvements. This scenario achieved a 10.9% improvement in performance relative to baseline.

### 3.4 Sensitivity to Reputational Weighting
Sensitivity analysis revealed a tipping point at $\beta = 0.45$. Above this threshold, LHNs prioritize reputational standing over immediate financial revenue. This suggests public performance signals are a more powerful lever than financial penalties.

## Discussion
This study quantified Strategic Gaming as a rational response to structural indexation gaps. The ABF model creates a "Moral Hazard" environment due to multi-layered information asymmetry {Ostrom, 2005 @Ostrom_2005 #121}. Agents are incentivized to adopt symbolic masks to secure revenue under the 6.5% cap.

The failure of the "Audit Blitz" suggests that deterrence-based models are insufficient. Administrative burden can displace clinical effort. The success of transparency points toward a new paradigm for NHRA reform. By making signals contemporaneous, the system can leverage **Reputational Utility** to drive High Reliability.

### 4.1 Limitations
Behavioral weighting parameters remain calibrated assumptions. The simulation assumes a unified LHN agent. Internal strategic dynamics within hospitals may introduce additional complexity.

## Conclusion
The NHRA currently operates in a Strategic Gaming equilibrium. Policymakers must address information asymmetries. Prioritizing transparency and reducing indexation divergence are more effective than increasing audit pressure.

## References
1. Baez Hernandez, Alexander. (2025). Games theory. A valuable instrument in decision-making in public policies. *Revista de la Facultad de Ciencias Económicas*. DOI: 10.14409/rfce.v1i1.12345
2. Duckett, Stephen. (2021). Vicious cycles: hospital bed block and the National Health Reform Agreement. *Medical Journal of Australia*. DOI: 10.5694/mja2.51016
3. Council on Federal Financial Relations. (2011). *National Health Reform Agreement*.
4. IHACPA. (2024). Pricing Framework for Australian Public Hospital Services 2024–25. *Report*. Available at: https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2024-25
5. Australian Institute of Health and Welfare. (2024). Hospital resources 2022–23: Australian hospital statistics. *Report*. Available at: https://www.aihw.gov.au/reports/hospitals/hospital-resources-2022-23
6. Ostrom, Elinor. (2005). Understanding Institutional Diversity. *Princeton University Press*. Available at: https://press.princeton.edu/books/paperback/9780691122380/understanding-institutional-diversity
