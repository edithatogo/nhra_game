# Workflow & Logic Diagrams (ODD Protocol)

These diagrams describe the project's processes and the conceptual logic of the simulation.

## Flow-A: Development Lifecycle (Conductor + TDD)
Standardized process for feature implementation and quality assurance.

```mermaid
graph TD
    A[Start Track] --> B[Draft Spec.md]
    B --> C[Draft Plan.md]
    C --> D{Plan Approved?}
    D -- No --> B
    D -- Yes --> E[Red Phase: Write Failing Test]
    E --> F[Green Phase: Implement Logic]
    F --> G[Refactor & Lint]
    G --> H{Tests Pass & Coverage >80%?}
    H -- No --> F
    H -- Yes --> I[Checkpoint Commit & Note]
    I --> J[Sync Docs & Archive]
```

## Flow-Data: Evidence-to-Output Pipeline
The data science workflow from raw data to validated policy reports.

```mermaid
graph LR
    subgraph Ingestion
    A[AIHW Raw] --> B[Preprocess]
    end
    
    subgraph Calibration
    B --> C[Optuna Optimization]
    C --> D[Best-fit Params]
    end
    
    subgraph Verification
    D --> E[Recursive Backtest]
    E --> F[Theil Decomposition]
    D --> G[Global Sensitivity]
    end
    
    subgraph Reporting
    F --> H[Validation Report]
    G --> I[Sensitivity Map]
    end
```

## Flow-GameTheory: Strategic Chain of Influence
How strategic choices propagate through the simulation mechanism.

```mermaid
graph TD
    BARG[Bargaining] -- "funding levels" --> DEF[Definition]
    DEF -- "payment scope" --> SHIFT[Cost-shifting]
    SHIFT -- "community access" --> DISC[Discharge]
    DISC -- "throughput" --> COMP[Compliance]
    COMP -- "audit risk" --> SIGNAL[Signalling]
    SIGNAL -- "transparency" --> BARG
```

## Flow-Conceptual: Mechanism Map
High-level overview for non-technical stakeholders.

```mermaid
graph TD
    subgraph Policy Levers
    A[Nominal Share]
    B[NEP Growth]
    C[Cap Growth]
    end
    
    subgraph Simulation Mechanism
    D[Game Theory Layer]
    E[System Dynamics]
    end
    
    subgraph Operational Proxies
    F[Pressure Index]
    G[Wait Times]
    H[Relative Risk]
    end
    
    A & B & C --> D
    D --> E
    E --> F & G & H
```
