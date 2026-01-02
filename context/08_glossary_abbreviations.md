# Glossary and Abbreviations

## Acronyms & Domain Terms
- **ABF**: Activity-Based Funding. A funding method where hospitals are paid based on the number and mix of services provided.
- **ACEC**: Australian Emergency Care Classification.
- **AIHW**: Australian Institute of Health and Welfare.
- **IHACPA**: Independent Health and Aged Care Pricing Authority. Sets the NEP.
- **IHPA**: Independent Hospital Pricing Authority (historic name).
- **NEP**: National Efficient Price (annual $/NWAU, determined by IHACPA).
- **NWAU**: National Weighted Activity Unit. A measure of health service activity expressed as a common unit of cost.
- **NHFB**: National Health Funding Body. Administers the payments.
- **NHRA**: National Health Reform Agreement. The policy framework being modeled.
- **VFI**: Vertical Fiscal Imbalance. The mismatch between revenue raising powers and expenditure responsibilities.
- **ED≤4h**: Emergency Department performance metric (Percentage of presentations completed within 4 hours).
- **LHN**: Local Hospital Network. The state-managed entity operating hospitals.

## Game Theoretic Concepts
- **Nash Equilibrium**: A stable state of a system involving the interaction of different participants, in which no participant can gain by a unilateral change of strategy.
- **Cost Shifting**: Strategic action where an agent transfers costs to another agent without a corresponding transfer of benefits.
- **Upcoding**: Systematically assigning higher-paying codes to patient encounters than is warranted by the clinical documentation.
- **Fragility Node**: A point in the system (e.g., information lag) that is structurally vulnerable to exploitation or failure.
- **Information Lag**: The delay between an action (e.g., treating a patient) and the observation of its outcome (e.g., data reporting), creating strategic ambiguity.

## Parameter Mapping (Manuscript vs. Code)
This table maps the mathematical symbols used in the manuscripts to the variable names in the `nhra_gt` codebase.

| Manuscript Symbol | Code Variable | Description |
| :--- | :--- | :--- |
| $\alpha$ (Alpha) | `nwau_utility` | Weight placed on revenue generation in the agent's utility function. |
| $\beta$ (Beta) | `kpi_satisfaction` / `ramping_penalty` | Weight placed on reputation or KPI satisfaction (often related to tipping points). |
| $\theta$ (Theta) | `coding_intensity` | The level of upcoding effort exerted by the LHN. |
| $P_{audit}$ | `audit_pressure` | The probability or intensity of an audit by the regulator. |
| $C_{adjust}$ | `adjustment_costs` | Cost associated with changing capacity or service levels (frictional cost). |
