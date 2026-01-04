# The “Cost Shifting Game”: why split funding can make us move costs instead of fixing problems

Why does it sometimes feel like the health system is just moving a problem from one bucket to another?

In Australia, the answer is often found in the **National Health Reform Agreement (NHRA)** and the split between Commonwealth and State funding.

When one side pays for “upstream” care (like GPs) and another pays for “downstream” care (like hospitals), we get a **Cost Shifting Game**.

## The real-world situation

Imagine a patient who needs help that could be provided in two places:

1. **Primary Care (GPs/Clinics)**: Funded mostly by the Federal government.
2. **Hospital EDs/Wards**: Funded by the State (with a share from the Federal government).

If primary care is hard to access, people go to the ED.

- The Federal government “saves” on GP rebates.
- The State “pays” for an expensive hospital visit.

Conversely, if a hospital discharges a patient quickly without enough support, they might end up back at their GP or in a Federal aged care program.

- The State “saves” on a hospital bed-day.
- The Federal government “pays” for the follow-up or complications.

## The “game” hiding inside it

In the codebase, we model this as a choice between two postures:

- **Invest (Holistic)**: spending money now to prevent a problem later, even if the saving goes to the “other” side.
- **Shift (Cut/Shunt)**: saving money in your own budget by letting the other side handle the consequence.

Check the logic:

- `src/nhra_gt/subgames/games.py` → `cost_shifting_game()`

## What “equilibrium” means here

In a perfect world, both sides would **Invest** because it creates the best health outcome for the lowest total cost.

But in the “game” of split budgets, **Shift** is often the Nash equilibrium.
Why? Because if you Invest and the other side Shifts, you pay twice: once for the investment and once for the extra burden they sent your way.

If both sides Shift, we get “System Failure / Low Cost” (at least in the short term). But the long-term cost in patient suffering and system inefficiency is huge.

## Externalities: a fancy word for “not my problem”

Economists call this an **externality**. It’s when my choice creates a cost for you that I don’t have to pay for.

In the NHRA, the “Efficiency Gap” and “CTH Share” are meant to balance this, but if the signals are too weak, the incentive to shift cost remains stronger than the incentive to collaborate.

## Policy implications

To break the Cost Shifting Game, you have to change the payoffs:

- **Pooled funding**: if both sides pay into the same bucket, shifting costs between them doesn't save anyone money.
- **Shared outcomes**: measure success by the patient's journey, not just the hospital's activity.
- **Transparency**: use data (from IHACPA and AIHW) to show where costs are actually moving.

## Evidence / further reading

- Senate Inquiry into Hospital Funding (2016). *Final Report*.
- Productivity Commission (2023). *Report on Government Services (Health)*.

## TL;DR

- Split funding creates a “Cost Shifting Game.”
- It is often rational for one side to shift costs to the other, even if it hurts the whole system.
- To fix it, we need incentives that reward holistic care over budget-shunting.
