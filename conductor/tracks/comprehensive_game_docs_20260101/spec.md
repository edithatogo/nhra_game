# Specification: Comprehensive Game Theoretic Documentation

## 1. Overview
The goal is to update the dashboard and documentation to explicitly document and explain "every single game" modeled in the simulation. This includes both the core NHRA sub-games and the broader structural interactions (LHN Competition, Electoral Logic) that drive system dynamics.

## 2. In Scope Games
The following interactions will be documented as distinct games:
1.  **Definition Game** (Commonwealth vs State: Realism vs Strictness)
2.  **Bargaining Game** (Federal Cycle: Agree vs Defer)
3.  **Cost Shifting Game** (Operational: Invest vs Shift)
4.  **Discharge Game** (Interface: Coordinate vs Fragment)
5.  **Governance Game** (Structural: Integrate vs Separate)
6.  **Compliance Game** (Audit: Tight vs Light)
7.  **Internal LHN Competition** (Intra-State: Pressure vs Revenue Capture)
8.  **Electoral Game** (Political: Salience vs Funding)

## 3. Functional Requirements

### 3.1 Data Structure
-   Each game MUST be defined with a rigorous schema containing:
    -   **Players**: The agents involved (e.g., LHN vs MOH, State vs Federal).
    -   **Strategies**: The choice set available to each player.
    -   **Payoffs**: The incentives for each outcome (e.g., $ Funding, - Sensitivity).
    -   **Nash Equilibrium**: The analytical or simulation-derived equilibrium.
    -   **Strategic Insight**: A plain English explanation of the dilemma.
    -   **Evidence Link**: A citation or reference to the empirical source (e.g., Senate Inquiry Report X) justifying the game's inclusion.
    -   **Key Parameter**: Identification of one primary sensitive parameter (e.g., "Political Salience") and its effect on the equilibrium.

### 3.2 Hybrid UI Structure
-   **Centralized "Game Theoretic Encyclopedia" Tab**: A new top-level tab acting as the definitive reference. It will feature:
    -   A selector to choose any of the 8 games.
    -   Structured display of the schema fields defined above.
    -   **Payoff Matrix Visualization**: A dynamic or static 2x2 matrix plot illustrating the game.
-   **Contextual "Mechanism Explainers"**: Collapsible expanders (e.g., `st.expander("🧩 how the Electoral Game works")`) placed directly in pertinent tabs:
    -   *Scenario Analysis Tab* (Electoral, Bargaining).
    -   *Intra-State LHN Variance Tab* (LHN Competition).
    -   *Technical Analytics/Strategic Map* (Core mechanism games).

## 4. Acceptance Criteria
-   [ ] All 8 games are implemented in the data registry with complete fields (including Evidence Links and Key Parameters).
-   [ ] The "Encyclopedia" tab renders all 8 games correctly with a visual payoff matrix.
-   [ ] Contextual explainers are present and functional in at least 3 distinct dashboard tabs.
-   [ ] The Strategic Map (D3) is reviewed to ensure it aligns with these definitions (node naming consistency).
