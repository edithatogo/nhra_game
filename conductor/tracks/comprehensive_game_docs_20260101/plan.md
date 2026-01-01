# Plan: Comprehensive Game Documentation

## Phase 1: Data Structure & Content (The "Backend")
- [x] Task: Create `GameDefinition` data class and registry.
    -   Define a schema for game rules, players, strategies, payoffs, evidence links, and key parameters.
    -   files: `src/game_theory/registry.py`
    -   *Test:* unit tests for registry retrieval.
- [x] Task: Populate content for Core Games (Definition, Bargaining, Cost Shifting, Discharge, Governance, Compliance).
    -   Implement the data dictionaries for these 6 games.
    -   *Test:* Verify data integrity (no missing fields).
- [x] Task: Populate content for Structural Games (Internal LHN, Electoral).
    -   Implement the data dictionaries for these 2 games.
    -   *Test:* Verify data integrity.
- [x] Task: Conductor - Agent Verification 'Data Structure & Content' [checkpoint: fedc255]

## Phase 2: Centralized Encyclopedia Tab (The "Frontend" - Part 1)
- [x] Task: Implement `render_game_encyclopedia()` UI component.
    -   Create the layout: Selector sidebar/dropdown, main content area.
    -   Render text sections (Definition, Insight, Nash Equilibrium, Evidence, Sensitivity).
    -   files: `scripts/dashboard.py` (or new module `scripts/dashboard_components/encyclopedia.py`)
- [x] Task: Implement Payoff Matrix Visualizer.
    -   Create a helper to draw the 2x2 matrix dynamically from the `GameDefinition`.
    -   *Test:* Verify matrix generation for known inputs.
- [x] Task: Integrate into Dashboard.
    -   Add "Game Rules" as a top-level tab in `dashboard.py`.
    -   *Test:* Verify tab loads without error.
- [x] Task: Conductor - Agent Verification 'Centralized Encyclopedia Tab' [checkpoint: CHECKPOINT_SHA_PHASE2_FINAL]

## Phase 3: Contextual Integration (The "Frontend" - Part 2)
- [x] Task: Implement `render_game_context_expander(game_id)` helper.
    -   Create a reusable generic expander component that pulls from the registry.
- [x] Task: Inject Context into "Scenario Analysis".
    -   Add expanders for Electoral and Bargaining games.
- [x] Task: Inject Context into "Intra-State LHN Variance".
    -   Add expander for Internal LHN Competition.
- [x] Task: Inject Context into "Strategic Map" / "Technical Analytics".
    -   Add expander for core network games.
- [x] Task: Conductor - Agent Verification 'Contextual Integration' [checkpoint: 40b6546e]

## Phase 4: Final Polish
- [x] Task: Verify Evidence Links.
    -   Ensure every game has at least one citation.
- [x] Task: Full consistency check.
    -   Ensure colors/names match the simulation.
- [x] Task: Conductor - Agent Verification 'Final Polish' [checkpoint: VERIFICATION_PASSED]
