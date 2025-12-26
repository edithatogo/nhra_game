# Game Theory Models Reference

This page provides a comprehensive reference for all stage games in the NHRA Game Theory toolkit. Each game captures a specific strategic tension in healthcare funding negotiations.

---

## Overview

The simulation uses **nine stage games** that represent key decision points in NHRA negotiations. Each game is a two-player normal-form game solved for Nash equilibria.

### Master Index

| Game | Row Actions | Column Actions | Strategic Tension |
|------|-------------|----------------|-------------------|
| [Definition](#definition-game) | R (Realism) / E (Efficient) | R / E | What counts as "efficient" |
| [Bargaining](#bargaining-game) | A (Agree) / D (Defer) | A / D | CAP convergence negotiation |
| [Cost Shifting](#cost-shifting-game) | I (Invest) / S (Shift) | I / S | Upstream vs downstream investment |
| [Discharge Coordination](#discharge-coordination-game) | C (Coordinate) / F (Fragment) | C / F | Hospital discharge planning |
| [Governance Integration](#governance-integration-game) | I (Integrate) / S (Separate) | I / S | UCC and governance structures |
| [Aged Care Interface](#aged-care-interface-game) | C (Coordinate) / F (Fragment) | C / F | ACAT handoff coordination |
| [NDIS Interface](#ndis-interface-game) | C (Coordinate) / F (Fragment) | C / F | NDIS transition planning |
| [Coding/Audit](#codingaudit-game) | H (Honest) / U (Upcode) | L (Light) / T (Tight) | Activity-based funding compliance |
| [Compliance](#compliance-game) | T (Tight) / L (Light) | T / L | Regulatory intensity choice |

---

## Game Parameters

All games receive a `GameParams` dataclass with the following state variables:

```python
@dataclass
class GameParams:
    pressure: float           # System pressure index (≥~0.8 typical)
    efficiency_gap: float     # Divergence from NEP indexation (0..~0.6)
    discharge_delay: float    # Excess length of stay index (1.0 = baseline)
    political_salience: float # Media/political attention (0..1)
    audit_pressure: float     # Audit intensity (0..1)
    cost_shifting_intensity: float  # Fee-for-service incentives (0..1)
    political_capital: float  # Government negotiating capital (0..1)
```

---

## Funding Negotiation Games

### Definition Game

**Strategic tension**: What counts as "efficient"?

- **Row player**: Commonwealth framing / policy narrative
- **Column player**: State implementation reality

| Actions | Description |
|---------|-------------|
| **R** (Realism) | Acknowledge cost reality; reduce efficiency gap drift |
| **E** (Efficient) | Strict efficient-price framing; gap drifts upward |

**Payoff drivers**:

- `realism_benefit = 0.5 + 0.8 × efficiency_gap + 0.4 × (pressure - 1.0)`
- `realism_cost = 0.25 + 0.35 × political_salience`
- `strict_benefit = 0.35 + 0.45 × political_salience`
- `strict_cost = 0.30 + 0.50 × pressure`

**Equilibrium characteristics**: Under high pressure and efficiency gap, (R,R) becomes the welfare-dominant equilibrium. Under low pressure with high political salience, (E,E) may be preferred.

---

### Bargaining Game

**Strategic tension**: Converge on CAP target or defer?

| Actions | Description |
|---------|-------------|
| **A** (Agree) | Converge toward target nominal share |
| **D** (Defer) | Defer/escalate; slow movement with conflict costs |

**Payoff drivers**:

- `converge_gain = 0.45 + 0.25 × (pressure - 1.0) + 0.20 × political_capital`
- `conflict_cost = 0.55 + 0.90 × pressure`
- `narrative_gain = 0.25 + 0.50 × political_salience`

**Equilibrium characteristics**: High pressure increases conflict costs, making (A,A) more attractive. Political capital enhances agreement payoffs.

---

### Cost Shifting Game

**Strategic tension**: Invest upstream or shift costs downstream?

| Actions | Description |
|---------|-------------|
| **I** (Invest) | Invest in upstream prevention/primary care |
| **S** (Shift) | Shift costs to downstream acute care |

**Payoff drivers**:

- `coop_gain = 0.55 + 0.45 × (1.0 - efficiency_gap)`
- `shift_gain = 0.35 + 0.75 × efficiency_gap + 1.0 × cost_shifting_intensity`
- `pr_cost = 0.65 × pressure`

**Equilibrium characteristics**: High `cost_shifting_intensity` (fee-for-service incentives) shifts equilibria toward (S,S). Pooled funding (low CSI) promotes coordination.

---

## Discharge and Interface Games

### Discharge Coordination Game

**Strategic tension**: Coordinate discharge planning or fragment care?

| Actions | Description |
|---------|-------------|
| **C** (Coordinate) | Joint discharge planning; shared responsibility |
| **F** (Fragment) | Fragmented care; siloed decision-making |

**Payoff drivers**:

- `benefit = 0.70 + 0.80 × excess_delay` (where `excess_delay = max(0, discharge_delay - 1.0)`)
- `cost = 0.30 + 0.10 × (1.0 - min(1.0, excess_delay))`
- `pr_penalty = 0.45 × pressure`

**Equilibrium characteristics**: High discharge delay increases coordination benefits. Under pressure, fragmentation becomes increasingly costly.

---

### Governance Integration Game

**Strategic tension**: Integrate governance (e.g., UCCs) or maintain separation?

| Actions | Description |
|---------|-------------|
| **I** (Integrate) | Unified governance structures |
| **S** (Separate) | Maintain separate governance |

**Payoff drivers**:

- `safety_gain = 0.55 + 0.35 × (pressure - 1.0)`
- `integration_cost = 0.20 + 0.35 × political_salience`
- `fragmentation_risk = 0.40 + 0.60 × pressure`

**Equilibrium characteristics**: High pressure increases both safety gains from integration and fragmentation risks, generally favouring integration.

---

### Aged Care Interface Game

**Strategic tension**: Coordinate ACAT handoffs or fragment?

| Actions | Description |
|---------|-------------|
| **C** (Coordinate) | Coordinated aged care transitions |
| **F** (Fragment) | Fragmented handoffs |

**Payoff drivers**:

- `coord_benefit = 0.6 + 0.4 × (discharge_delay - 1.0)`
- `frag_cost = 0.5 × pressure`

**Equilibrium characteristics**: A symmetric coordination game where both players prefer (C,C) when discharge delays are high.

---

### NDIS Interface Game

**Strategic tension**: Coordinate NDIS transitions or fragment?

| Actions | Description |
|---------|-------------|
| **C** (Coordinate) | Coordinated NDIS transitions |
| **F** (Fragment) | Fragmented handoffs |

**Payoff drivers**:

- `coord_benefit = 0.5 + 0.5 × (discharge_delay - 1.0)`
- `frag_cost = 0.6 × pressure`

**Equilibrium characteristics**: Similar structure to Aged Care, but with slightly higher fragmentation costs under pressure.

---

## Compliance and Audit Games

### Coding/Audit Game

**Strategic tension**: Provider coding honesty vs auditor vigilance

- **Row player**: Healthcare provider
- **Column player**: Auditor/regulator

| Row Actions | Description |
|-------------|-------------|
| **H** (Honest) | Accurate activity coding |
| **U** (Upcode) | Inflate activity codes for higher reimbursement |

| Column Actions | Description |
|----------------|-------------|
| **L** (Light) | Minimal audit scrutiny |
| **T** (Tight) | Intensive audit regime |

**Payoff drivers**:

- `upcode_gain = 0.3 + 0.7 × efficiency_gap`
- `penalty = 0.8 × audit_pressure`
- `audit_cost = 0.2`
- `recovery = 0.4 × efficiency_gap`

**Equilibrium characteristics**: Mixed equilibrium common. High audit pressure deters upcoding; high efficiency gap increases temptation.

---

### Compliance Game

**Strategic tension**: Tight vs light regulatory compliance

| Actions | Description |
|---------|-------------|
| **T** (Tight) | Stringent compliance; higher admin cost, less leakage |
| **L** (Light) | Relaxed compliance; lower cost, more leakage |

**Payoff drivers**:

- `leakage = 0.40 + 0.70 × efficiency_gap`
- `admin = 0.18 + 0.45 × audit_pressure`

**Equilibrium characteristics**: Trade-off between administrative burden and revenue protection. High audit pressure makes tight compliance more attractive.

---

## Nash Equilibrium Solver

All games return a `TwoPlayerGame` object that supports:

```python
from nhra_gt.subgames.nash import solve_all_equilibria

game = definition_game(GameParams(pressure=1.0, efficiency_gap=0.3, ...))
equilibria = solve_all_equilibria(game)

for eq in equilibria:
    print(f"Row: {eq.row_strategy}, Col: {eq.col_strategy}")
    print(f"Expected payoffs: {eq.row_payoff:.3f}, {eq.col_payoff:.3f}")
```

The solver finds all pure and mixed Nash equilibria using support enumeration.

---

## References

- Source code: [`src/nhra_gt/subgames/games.py`](https://github.com/edithatogo/nhra_game/blob/main/src/nhra_gt/subgames/games.py)
- Nash solver: [`src/nhra_gt/subgames/nash.py`](https://github.com/edithatogo/nhra_game/blob/main/src/nhra_gt/subgames/nash.py)
- Agent integration: [`src/nhra_gt/agents/base.py`](https://github.com/edithatogo/nhra_game/blob/main/src/nhra_gt/agents/base.py)
