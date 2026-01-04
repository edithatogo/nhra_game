# The NHRA “Definition Game”: what counts as a hospital service (and why that changes who pays)

If you’ve ever watched two people argue about *definitions* and thought “this is pointless”… welcome to health funding.

Under Australia’s National Health Reform Agreement (NHRA), a lot of money moves based on *what gets counted* as an in-scope “public hospital service”, how it’s classified, and how activity is priced. When the system is under pressure, that debate stops being academic — it becomes strategic.

This article explains one simple idea: sometimes the fight over definitions behaves like a small game with predictable outcomes.

## The NHRA situation (in plain English)

Two groups have to agree on rules:

- The **Commonwealth** wants rules that are clear, measurable, and fiscally containable.
- **States** want rules that match the messy reality of running hospitals under demand pressure.

If a definition is too strict, costs don’t disappear — they show up somewhere else (often as “hospital pressure”, delayed care, or cost-shifting). If a definition is too loose, the funder worries it will pay for things that are hard to compare, audit, or justify.

So both sides are often arguing about the same sentence… but with different incentives.

## The “game” hiding inside it

Think of it like each side choosing one of two postures:

- **Realism**: acknowledge cost reality; definitions flex to reflect actual care needs.
- **Strictness**: keep definitions tight; hold the line on what qualifies and how it’s counted.

Each side prefers a world where *their* posture sets the framing — and each posture has trade-offs.

In the codebase, this is represented as a small 2×2 “stage game” (a payoff matrix), where the best response can flip depending on system pressure and other parameters:

- `src/nhra_gt/subgames/games.py` → `definition_game()`

## The simple model (no math required)

In a 2×2 game, each side asks: “Given what the other side is doing, which choice gives me the better outcome?”

If strictness reduces fiscal exposure (good for the Commonwealth) but raises operational risk (bad for States), the “best response” depends on how severe the pressure is and how big the efficiency gap is between pricing and real costs.

That’s the whole point: **the same written rule can create different strategic behaviour depending on pressure and incentives.**

## What the equilibrium predicts (intuition)

An equilibrium in this context is not “the best” outcome — it’s “the outcome that tends to stick” because neither side can improve their position by changing stance *unilaterally*.

In many realistic settings, a tight-definition posture can become “sticky” because:

- it is narratively simpler (“we’re paying for X, not Y”),
- it looks fiscally disciplined,
- and the operational costs are delayed or diffuse.

But if operational pressure rises enough, the system can push back: strictness starts to create visible failures (waiting times, bed block, political blowback), and “realism” becomes the better response even if it costs more.

That means the equilibrium can “tip” as conditions change.

## Why this matters (policy implications)

If this framing is roughly correct, then policy arguments about definitions aren’t just “wonk fights” — they’re incentive design problems:

- If you want definitions to stay realistic under pressure, you need **mechanisms that make operational reality legible and auditable**, not just rhetorical.
- If you want definitions to remain strict without harming patients, you need **credible pressure-relief pathways** (otherwise strictness just pushes problems downstream).
- If you want fewer fights over definitions, you need **shared measurement and shared consequences**, so both sides pay attention to the same signals.

## Evidence / further reading

- Independent Health and Aged Care Pricing Authority (IHACPA). *Pricing Framework for Australian Public Hospital Services 2024–25*. <https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2024-25>
- Australian Institute of Health and Welfare (AIHW). *Hospital resources 2022–23: Australian hospital statistics*. <https://www.aihw.gov.au/reports/hospitals/hospital-resources-2022-23>

## TL;DR

- Under the NHRA, definitions are strategic because they change what gets counted (and funded).
- A simple 2×2 game can explain why “strictness” can be sticky until pressure forces a shift.
- If you want better outcomes, change incentives and measurement — not just wording.
