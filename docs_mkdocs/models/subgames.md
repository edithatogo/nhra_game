# Strategic Subgames (Nash Equilibria)

Strategic behavior in the NHRA is modeled as a set of non-cooperative games between the Commonwealth (Principal), States (Agents), and LHNs (Operators).

## 1. The Negotiation Game (Hold-Up)

Every 5 years, at agreement expiry, a high-stakes bargaining game occurs.

### Payoff Matrix (Illustrative)

| | State: Agree (A) | State: Hold-Up (H) |
| :--- | :---: | :---: |
| **Cth: Concede (C)** | (0.9, 1.2) | (0.7, 1.5) |
| **Cth: Enforce (E)** | (1.0, 1.0) | (0.2, 0.4) |

- **Nash Equilibrium:** Under high system pressure, the state's threat of failure becomes credible, forcing the Commonwealth to concede higher funding shares ($\alpha$).

## 2. Cost-Shifting Game

Models the incentive to shift patients between Commonwealth-funded primary care and State-funded hospital care.

$$
Payoff_{State} = B_{efficiency} - C_{pressure} + G_{shifting}
$$

If $G_{shifting} > C_{penalty}$, the State chooses to 'Shift' rather than 'Invest'.

## 3. Solver Implementation

We use two primary solvers:
1. **Discrete Nash:** Brute-force enumeration for small 2x2 games.
2. **Quantal Response Equilibrium (QRE):** A JAX-native Logit solver for boundedly rational agents.

## 4. Evidence Grounding
- **Strategies:** Derived from the **Blinded Qualitative Mapping** of the NHRA statutory text (see `publications/P1`).
- **Payoffs:** Stylised based on vertical fiscal imbalance metrics.
