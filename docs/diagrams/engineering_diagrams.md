# Engineering Diagrams (C4 Model)

These diagrams follow the C4 model to represent the system architecture at different levels of abstraction.

## Level 1: System Context
Shows the NHRA Model in the context of its users and external data sources.

```mermaid
C4Context
    title System Context Diagram for NHRA Game Theory Model
    
    Person(user, "Policy Researcher / Analyst", "Uses the model to run scenarios and generate reports.")
    System(model, "NHRA Game Theory Model", "Predictive forecasting engine for hospital system pressure and risk.")
    
    System_Ext(aihw, "AIHW / ABS Data", "Provides historical health system metrics (NEP, ED performance).")
    System_Ext(mja, "Academic Community (MJA)", "Peer review and reproducibility target.")
    
    Rel(user, model, "Configures parameters and runs simulations")
    Rel(aihw, model, "Feeds historical data for calibration")
    Rel(model, mja, "Provides reproducible methodology and figures")
    Rel(model, user, "Delivers interactive dashboard and PDF reports")
```

## Level 2: Container Diagram
Explores the high-level technology choices and data boundaries.

```mermaid
C4Container
    title Container Diagram for NHRA Game Theory Model
    
    Person(user, "User", "Policy Researcher")
    
    Container_Boundary(c1, "Simulation & Analysis Environment") {
        Container(app, "Python Runtime", "Python 3.10+", "Core execution engine.")
        Container(ui, "Streamlit Dashboard", "Web UI", "Interactive scenario analysis.")
        ContainerDb(data, "File System (Parquet/CSV/JSON)", "Data Lake", "Stores parameters, historical data, and simulation outputs.")
        Container(pipeline, "Snakemake Pipeline", "Workflow Engine", "Orchestrates GSA, Calibration, and Validation.")
    }
    
    Rel(user, ui, "Uses browser to interact")
    Rel(ui, app, "Triggers model runs")
    Rel(pipeline, app, "Executes batch processing")
    Rel(app, data, "Reads/Writes")
```

## Level 3: Component Diagram (Source Structure)
Details the internal module relationships within the Python package.

```mermaid
C4Component
    title Component Diagram for NHRA Game Theory Model (src/nhra_game_theory)
    
    Component(engine, "Engine (v26)", "Python/NumPy", "Core transition functions.")
    Component(legacy_engine, "Legacy Engine (v8)", "Python/Pydantic", "Baseline mechanism logic.")
    Component(domain, "Domain Models", "Python/Pydantic", "State vectors and Params.")
    Component(subgames, "Strategic Layer", "Python/NetworkX", "Nash solvers.")
    Component(rules, "Policy Rules", "Python", "Cap and Audit logic.")
    Component(viz, "Visualization API", "Python", "Unified plotting.")
    Component(sensitivity, "GSA Suite", "Python/SALib", "Sobol and Morris.")
    Component(audit, "Audit Suite", "Python", "Fingerprinting and integrity.")
    Component(plotting_legacy, "Legacy Plotting", "Python", "Deprecated wrappers.")
    Component(interfaces, "Protocols", "Python", "Interface definitions.")
    
    Rel(engine, subgames, "Calls")
    Rel(engine, domain, "Uses")
    Rel(engine, rules, "Respects")
    Rel(engine, viz, "Feeds")
    Rel(sensitivity, engine, "Wraps")
    Rel(audit, engine, "Scans")
    Rel(engine, legacy_engine, "Compares against")


```
