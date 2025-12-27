# Policy Scenarios

This page provides comparison tables for key policy intervention scenarios modelled in the toolkit.

---

## Intervention Comparison

### Overview Table

| Intervention | Mechanism | Target Game | Expected Effect |
|--------------|-----------|-------------|-----------------|
| **Pooled Funding** | Reduce cost shifting incentives | Cost Shifting | ↓ Fragmentation |
| **UCC Integration** | Unified governance | Governance Integration | ↑ Coordination |
| **Transparency Initiative** | Increase political salience | Definition, Bargaining | ↑ Accountability |
| **Audit Intensification** | Increase audit pressure | Coding/Audit, Compliance | ↓ Upcoding |
| **Discharge Coordination** | Structured handoffs | Discharge, Aged Care, NDIS | ↓ Delays |

---

## Detailed Scenario Analysis

### 1. Pooled Funding

**Objective**: Reduce cost shifting by removing fee-for-service incentives.

| Parameter | Baseline | Intervention | Change |
|-----------|----------|--------------|--------|
| `cost_shifting_intensity` | 0.35 | 0.15 | -57% |
| Expected equilibrium | (S, S) | (I, I) | → Invest |

**Mechanism**: Lower CSI shifts the Cost Shifting game equilibrium from (Shift, Shift) to (Invest, Invest) by reducing the payoff advantage of cost shifting.

```python
# Code example
pooled = Params(cost_shifting_intensity=0.15)
results = run_simulation(years=10, params=pooled)
```

**Expected Outcomes**:
- ↓ Downstream pressure
- ↓ ED presentations from cost shifting
- ↑ Primary care investment

---

### 2. UCC Integration

**Objective**: Implement Urgent Care Clinics with unified governance.

| Parameter | Baseline | Intervention | Change |
|-----------|----------|--------------|--------|
| `fragmentation_index` | 1.0 | 0.7 | -30% |
| Expected equilibrium | (S, S) | (I, I) | → Integrate |

**Mechanism**: UCC integration reduces fragmentation risk in the Governance Integration game, making integration the dominant strategy.

```python
ucc = Params(fragmentation_index=0.7)
results = run_simulation(years=10, params=ucc)
```

**Expected Outcomes**:
- ↓ ED overcrowding
- ↑ Low-acuity diversion
- ↑ Coordination of care

---

### 3. Transparency Initiative

**Objective**: Increase public visibility of system performance.

| Parameter | Baseline | Intervention | Change |
|-----------|----------|--------------|--------|
| `political_salience` | 0.3 | 0.7 | +133% |
| Expected equilibrium | Variable | (R, R) | → Realism |

**Mechanism**: Higher political salience increases the cost of "efficiency theatre" in the Definition game, pushing toward realistic acknowledgment of cost pressures.

```python
transparency = Params(political_salience=0.7)
results = run_simulation(years=10, params=transparency)
```

**Expected Outcomes**:
- ↑ Pressure to acknowledge cost reality
- ↓ Efficiency gap drift
- ↑ Evidence-based policy

---

### 4. Audit Intensification

**Objective**: Reduce upcoding through stricter compliance monitoring.

| Parameter | Baseline | Intervention | Change |
|-----------|----------|--------------|--------|
| `audit_pressure` | 0.3 | 0.7 | +133% |
| Expected equilibrium | (U, L) | (H, T) | → Honest/Tight |

**Mechanism**: Higher audit pressure in the Coding/Audit game increases the penalty for upcoding, shifting equilibrium toward honest coding.

```python
audit = Params(audit_pressure=0.7)
results = run_simulation(years=10, params=audit)
```

**Expected Outcomes**:
- ↓ Upcoding prevalence
- ↑ ABF accuracy
- ↓ Revenue leakage (short-term)

!!! note "Trade-off"
    High audit pressure increases administrative burden. Optimal level depends on efficiency gap magnitude.

---

## Scenario Comparison Matrix

### Effect on System Pressure

| Scenario | Year 1 | Year 5 | Year 10 | Direction |
|----------|--------|--------|---------|-----------|
| Baseline | 1.00 | 1.08 | 1.15 | ↑ |
| Pooled Funding | 1.00 | 0.98 | 0.95 | ↓ |
| UCC Integration | 1.00 | 1.02 | 1.05 | → |
| Transparency | 1.00 | 1.05 | 1.10 | ↗ |
| Audit Intensification | 1.00 | 1.06 | 1.12 | ↗ |

### Equilibrium Shift Summary

| Scenario | Games Affected | Equilibrium Change |
|----------|----------------|-------------------|
| Pooled Funding | Cost Shifting | (S,S) → (I,I) |
| UCC Integration | Governance | (S,S) → (I,I) |
| Transparency | Definition, Bargaining | Various → (R,R), (A,A) |
| Audit Intensification | Coding/Audit, Compliance | (U,L) → (H,T) |

---

## Combined Interventions

### Pooled Funding + UCC Integration

Combining structural reforms can produce synergistic effects:

```python
combined = Params(
    cost_shifting_intensity=0.15,
    fragmentation_index=0.7
)
results = run_simulation(years=10, params=combined)
```

| Metric | Baseline | Pooled Only | UCC Only | Combined |
|--------|----------|-------------|----------|----------|
| Pressure (Y10) | 1.15 | 0.95 | 1.05 | 0.88 |
| Coordination | Low | Medium | Medium | High |
| Cost Shifting | High | Low | High | Low |

---

## Parameter Sensitivity

### Key Levers

Based on Sobol sensitivity analysis:

| Parameter | Sensitivity (ST) | Policy Leverage |
|-----------|-----------------|-----------------|
| `cost_shifting_intensity` | 0.65 | **Very High** |
| `efficiency_gap` | 0.20 | Medium |
| `pressure` (initial) | 0.10 | Low |
| `political_salience` | 0.05 | Low |

**Implication**: Policy efforts targeting cost shifting mechanisms (e.g., pooled funding) have the highest leverage for reducing system pressure.

---

## Running Your Own Scenarios

```python
from nhra_gt.engine import Params, run_simulation

# Define custom scenario
my_scenario = Params(
    cost_shifting_intensity=0.25,
    political_salience=0.5,
    audit_pressure=0.4
)

# Run simulation
results = run_simulation(
    years=10,
    n_samples=500,
    params=my_scenario
)

# Analyse results
print(f"Final pressure: {results['pressure'].mean():.2f}")
```

---

## See Also

- [Game Theory Models](guides/models.md) — Game specifications
- [Usage Guide](guides/usage.md) — Running simulations
- [Validation](validation.md) — Testing approach
