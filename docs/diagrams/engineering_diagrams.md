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
    
    Component(engine, "Engine", "Python/NumPy", "Core transition functions and Monte Carlo logic.")
    Component(domain, "Domain Models", "Python/Pydantic", "State vectors, parameters, and business logic.")
    Component(subgames, "Strategic Layer", "Python/NetworkX", "Game theory logic and Nash solvers.")
    Component(sensitivity, "Sensitivity Suite", "Python/SALib", "Sobol and Morris GSA implementations.")
    Component(viz, "Visualization API", "Python/Matplotlib/Plotly", "Unified plotting infrastructure.")
    
    Rel(engine, domain, "Uses")
    Rel(engine, subgames, "Calls strategic decisions")
    Rel(sensitivity, engine, "Wraps for variance analysis")
    Rel(engine, viz, "Feeds data for plotting")
    Rel(viz, domain, "Validates schemas")
```
