# Round 2 Implementation Plan → v17
**Date:** 2025-12-21  
**Objective:** Convert v16 into a decision-ready package without increasing conceptual complexity.

## Work packages
1. **Intervention scenario library**
   - Add pooled funding, UCC governance integration, aged care throughput, NEP indexation uplift, and audit burden scenarios.
   - Export absolute endpoints and deltas vs baseline.

2. **Equilibria transparency**
   - Export all equilibria by year at mean state.
   - Produce equilibrium multiplicity plots per game.

3. **Publication-style reporting**
   - Rewrite the report with section introductions, captions, abbreviations, and narrative limitations.
   - Generate HTML for circulation.

## Acceptance criteria
- All new outputs saved under outputs/v17.
- Report contains titled tables, captions, abbreviations, and narrative synthesis.
- Tests and coverage pass with per-file coverage ≥95%.
