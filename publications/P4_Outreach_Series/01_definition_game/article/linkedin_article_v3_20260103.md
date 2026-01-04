# The NHRA “Definition Game”: what counts (and why that changes who pays)

Sometimes the biggest fights in health funding are about one boring question:

**“Does this count?”**

Under Australia’s **National Health Reform Agreement (NHRA)**, what “counts” can change funding signals. That can change behaviour. And when behaviour changes, patients feel it.

Quick glossary (plain English):
- **NHRA**: the national deal that shapes how public hospitals are funded.
- **IHACPA**: publishes pricing frameworks used in public hospital funding.
- **AIHW**: publishes national hospital data and reports.

## The real-world situation

Two groups have to agree on rules.

- The **Commonwealth** wants rules that are easy to measure and defend.
- **States** want rules that match hospital reality.

Reality is messy. Hospitals do the work even when the rulebook is unclear.

So if a rule is too strict, the work can become “unfunded reality”.
If a rule is too loose, the funder worries it will pay for things it can’t compare or audit.

## A tiny example

Imagine a type of care that sits near a boundary.

- If it is counted as “in-scope hospital activity”, funding follows.
- If it is counted as “out-of-scope” (or coded differently), the work still happens — but the money signal changes.

When the money signal changes, people adapt. That is not evil. It is normal.

## The “game” hiding inside it

Think of each side choosing a posture:

- **Strictness**: keep definitions tight.
- **Realism**: let definitions reflect actual care needs and costs.

“Pressure” matters too. Pressure is not abstract.
It is things like ED waits, bed block, staffing strain, and political heat.

In the codebase, this is a small 2×2 game:
- `src/nhra_gt/subgames/games.py` → `definition_game()`

## What “equilibrium” means (no math)

An equilibrium is not “the best outcome”.

It is the outcome that tends to stick because neither side can improve by changing alone.

Often (not always), “strictness” can become sticky because it is:
- simpler to explain,
- easier to audit,
- easier to sell as “fiscal control”.

But if pressure rises, strictness can backfire.
The downsides become visible. Then the “best response” can flip toward realism.

## What this is NOT

- This is **not** accusing individual clinicians or coders of bad intent.
- It is about **system incentives** and **what we choose to measure**.

## Policy implications (practical)

If you want fewer definition wars, you can change the game:

- Make reality measurable: shared data and shared definitions.
- Make consequences shared: if pressure rises, both sides see it in the same dashboard.
- Design audit so it supports learning, not just punishment.

One patient-impact sentence, because it matters:
when rules and reality don’t match, the system often “pays” in delays and bottlenecks.

## Evidence / further reading

- IHACPA. *Pricing Framework for Australian Public Hospital Services 2024–25*. https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2024-25
- AIHW. *Hospital resources 2022–23: Australian hospital statistics*. https://www.aihw.gov.au/reports/hospitals/hospital-resources-2022-23

## TL;DR

- In the NHRA, “what counts” changes funding signals.
- Funding signals change behaviour.
- A simple game can explain why some positions become sticky until pressure forces change.

