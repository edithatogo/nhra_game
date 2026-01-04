# Consensus Priorities — Bundle 02 (Bargaining Game) — v1_20260104 → v2

Decision method (simulated):
- Prioritise 14yo comprehension first, then policy usefulness, then “nice to have” polish.
- Avoid adding claims that require new evidence beyond the linked sources.

## Agreed priorities (implement in v2)

### P0 (must do)
1) Add a short “tiny example” paragraph that makes “agree now vs hold out” concrete (generic, not legalistic).
2) Add a plain-language analogy for “discounting” (e.g., pizza gets cold / phone battery / you miss the movie).
3) Add a short “What this is NOT” disclaimer (avoid implying bad intent; acknowledge repeated negotiations).

### P1 (should do)
4) Strengthen LinkedIn post hook (question format + punchy line).
5) Add one sentence acknowledging that equilibria can differ (sometimes multiple), without adding math.

### P2 (could do)
6) Add 1–2 bullets linking uncertainty to frontline planning (workforce, service planning), with a patient-impact line.

## Explicitly not doing (for now)
- Adding quantitative claims about “how much value shrinks” (needs data + careful framing).
- Naming specific negotiation events or attributing motives (not appropriate for a public explainer without evidence).

## Validation after changes
- `python scripts/outreach/validate_social.py --root publications/P4_Outreach_Series/02_bargaining_game`
- `python scripts/outreach/validate_readability.py --root publications/P4_Outreach_Series/02_bargaining_game --max-grade 9.5`
- `python scripts/outreach/validate_links.py --bundle bargaining_game`

