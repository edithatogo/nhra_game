# The NHRA “Definition Game”: what counts as a hospital service (and why that changes who pays)

If you’ve ever watched two grown-ups argue about *definitions* and thought “this is pointless”… welcome to health funding.

**NHRA** = the national agreement that sets key funding rules and responsibilities between the Commonwealth and States for public hospitals.  
**IHACPA** = the body that publishes pricing frameworks used in Australian public hospital funding.  
**AIHW** = a major national source of health system reporting and statistics.

This article explains one simple idea: in the NHRA, fights over definitions often behave like a small game with predictable outcomes.

## The NHRA situation (in plain English)

Two groups have to agree on rules about what gets counted, priced, and funded:

- The **Commonwealth** tends to prefer definitions that are clear, measurable, comparable, and fiscally containable.
- **States** tend to prefer definitions that match the messy reality of running hospitals under demand pressure.

Here’s a concrete mini-example:

> Imagine a category of care that sits near a boundary. If it’s counted as “in-scope hospital activity”, funding follows. If it’s counted as “out-of-scope” (or classified differently), the work still happens — but the money signal changes, and so does behaviour.

And “pressure” is not abstract: it’s the everyday stuff people feel — ED waits, bed occupancy, discharge delays, staffing strain, and political heat.

## The “game” hiding inside it

Think of each side choosing one of two postures:

- **Realism**: definitions flex to reflect actual care needs and costs.
- **Strictness**: definitions stay tight; hold the line on what qualifies and how it’s counted.

Each posture has trade-offs:

- Strictness can improve comparability and budget predictability.
- Realism can reduce the risk of “unfunded reality” (where the work exists but the funding signal doesn’t match it).

In the codebase, this is represented as a small 2×2 “stage game” (a payoff matrix), where the best response can shift depending on system pressure and other parameters:

- `src/nhra_gt/subgames/games.py` → `definition_game()`

## The simple model (no math required)

In a 2×2 game, each side asks: “Given what the other side is doing, which choice gives me the better outcome?”

That’s it. No calculus required.

The key insight is that **the same written rule can lead to different strategic behaviour depending on pressure and incentives**.

## What the equilibrium predicts (intuition)

An equilibrium in this context is not “the best” outcome — it’s “the outcome that tends to stick” because neither side can improve their position by changing stance *unilaterally*.

Often (not always), a tight-definition posture can become “sticky” because it is:

- narratively simpler (“we’re paying for X, not Y”),
- easier to defend as fiscally disciplined,
- and its downsides can be delayed, diffuse, or hard to attribute.

But if operational pressure rises enough, strictness can produce visible failures (waiting times, bed block, political blowback). At that point, “realism” can become the better response even if it costs more. That’s the “tipping” idea.

## What this is NOT

- This is **not** an accusation that individual clinicians or coders are “gaming”.
- It’s a way of describing how systems behave when incentives and measurement don’t line up with reality.

## Why this matters (policy implications)

If this framing is roughly correct, policy debates about definitions are incentive design problems:

- If you want definitions to stay realistic under pressure, you need **shared measurement that makes operational reality legible and auditable** (so realism isn’t just a plea).
- If you want definitions to remain strict without harming patients, you need **credible pressure-relief pathways** (so strictness doesn’t just push problems downstream).
- If you want fewer definition fights, you need **shared data and shared consequences**, so both sides pay attention to the same signals.

One patient-impact sentence, because it matters: when definitions and incentives don’t match reality, pressure often shows up as *delays and bottlenecks* that patients experience as “the system isn’t moving”.

## Evidence / further reading

- IHACPA. *Pricing Framework for Australian Public Hospital Services 2024–25*. https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2024-25
- AIHW. *Hospital resources 2022–23: Australian hospital statistics*. https://www.aihw.gov.au/reports/hospitals/hospital-resources-2022-23

## TL;DR

- Under the NHRA, definitions matter because they change what gets counted (and funded).
- A simple 2×2 game can explain why “strictness” can be sticky until pressure forces a shift.
- If you want better outcomes, change incentives and measurement — not just wording.

