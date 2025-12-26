# Entity-Relationship Diagrams (Grounded Architecture)

These diagrams define the logical data models and integrity constraints of the NHRA Game Theory simulation.

## ER-A: Grounded Parameters & Evidence
Maps simulation parameters to their empirical grounding and policy sources.

```mermaid
erDiagram
    PARAMS ||--o{ EVIDENCE_SOURCE : "grounded_by"
    PARAMS {
        float nep_annual_growth
        float demand_base
        float bed_capacity_index
        float nominal_cth_share_target
        float cost_shifting_intensity
    }
    EVIDENCE_SOURCE {
        string key "Primary Key"
        string url "Source URI"
        string nhmrc_level "Evidence Grade"
        string description
    }
    POLICY_LEVER ||--|| PARAMS : "parameterizes"
    POLICY_LEVER {
        string name
        string goal "Policy Objective"
    }
```

## ER-B: State Vectors & Temporal Transitions
Defines the schema of simulation states and how they evolve over time.

```mermaid
erDiagram
    STATE ||--o{ STATE : "transitions_to (monthly)"
    STATE {
        int year
        int month
        float pressure "Operational Strain"
        float occupancy "Bed Utilization"
        float relative_risk "Harm Proxy"
        string system_mode "Normal/Crisis"
    }
    STATE ||--|| PARAMS : "respects"
```

## ER-C: Strategic Nodes & Equilibria
Models the game theory layer, including payoffs and Nash equilibria.

```mermaid
erDiagram
    GAME_NODE ||--o{ STRATEGY : "defines"
    GAME_NODE ||--o{ PAYOFF_MATRIX : "evaluated_by"
    GAME_NODE {
        string id "BARG/DEF/SHIFT/etc."
        string name
    }
    STRATEGY {
        string code "A/D, R/E, I/S"
        string description
    }
    PAYOFF_MATRIX {
        float utility_cth
        float utility_state
    }
    NASH_EQUILIBRIUM ||--|| GAME_NODE : "solved_for"
    NASH_EQUILIBRIUM {
        string type "Pure/Mixed"
        string selected_strategy
    }
```

## ER-D: Provenance & Artifacts
Tracks the lineage from simulation runs to output figures and reports.

```mermaid
erDiagram
    SIMULATION_RUN ||--o{ OUTPUT_DATA : "produces"
    SIMULATION_RUN {
        int seed "Reproducibility Key"
        int n_mc "Sample Count"
        datetime timestamp
    }
    OUTPUT_DATA ||--o{ FIGURE : "visualizes"
    OUTPUT_DATA {
        string path "CSV/JSON location"
        string schema_version
    }
    FIGURE ||--|| FIGURE_REGISTRY : "registered_in"
    FIGURE {
        string id "fig_trajectory_*"
        string format "PNG/SVG/PDF"
    }
    FIGURE_REGISTRY {
        string description
        string function_name
    }
```
