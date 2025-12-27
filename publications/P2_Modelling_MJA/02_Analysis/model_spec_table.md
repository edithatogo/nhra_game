# Comprehensive Model Specification (P2 Supplementary Data)
**Author:** Dylan A Mordaunt

## 1. Parameter Table

| Parameter | Symbol | Value (Base) | Units | Source |
| :--- | :--- | :--- | :--- | :--- |
| National Efficient Price | $NEP$ | 1.0 (Index) | $/NWAU | IHACPA 2024-25 |
| Commonwealth Share | $\alpha$ | 0.45 | Fraction | NHRA Clause 34 |
| Growth Cap | $G_{max}$ | 0.065 | Fraction | NHRA Clause 38 |
| Reputation Weight | $\beta$ | 0.30 | Weight | Calibrated (Mordaunt 2025) |
| Audit Probability | $P_{audit}$ | 0.05 | Probability | Assumed Baseline |
| Clinical Effort Cost | $C$ | 0.25 | Utility | Assumed Baseline |

## 2. Core Equations

### 2.1 Utility ($U$)
$$U_i = \alpha \cdot F(a_i, \theta) + \beta \cdot R(s_i) - C(e_i) - P_{audit} \cdot \delta$$
Where $\delta$ is the penalty for detected gaming.

### 2.2 System Pressure ($P$)
$$P = 0.8 + 0.8 \cdot (0.55 \cdot \text{occ\_term} + 0.45 \cdot \text{off\_term}) \cdot \text{discharge\_delay}$$

## 3. Diagram Mapping

| Diagram File | Publication | Context |
| :--- | :--- | :--- |
| `NHRA_Problem_Map.svg` | P1 | Structural logic of the Agreement. |
| `NHRA_Advocacy_Map.svg` | P1 | Proposed policy interventions. |
| `Gaming_Cycle.mmd` (New) | P2 | The feedback loop between isomorphism and symbolic compliance. |
| `Equilibrium_Tipping.png` | P2 | Results of the sensitivity analysis. |
