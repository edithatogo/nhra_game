# Architecture Diagrams

This page contains architecture and flow diagrams for the NHRA Game Theory toolkit.

---

## System Architecture

```mermaid
flowchart TB
    subgraph inputs["📥 Inputs"]
        params["Parameter Registry<br/>(context/04_parameter_registry.csv)"]
        config["Simulation Config<br/>(Params dataclass)"]
    end

    subgraph core["🎮 Core Engine"]
        games["Stage Games<br/>(9 two-player games)"]
        nash["Nash Solver<br/>(pure + mixed equilibria)"]
        agents["Agents<br/>(Heuristic, Optimizing)"]
        engine["Simulation Engine<br/>(annual dynamics)"]
    end

    subgraph outputs["📊 Outputs"]
        results["Simulation Results<br/>(pressure, efficiency, flow)"]
        sensitivity["Sensitivity Analysis<br/>(Sobol indices)"]
        reports["Reports & Figures"]
    end

    params --> config
    config --> engine
    engine --> games
    games --> nash
    nash --> agents
    agents --> engine
    engine --> results
    results --> sensitivity
    results --> reports
```

---

## Game Flow

```mermaid
sequenceDiagram
    participant E as Engine
    participant G as GameParams
    participant S as Stage Games
    participant N as Nash Solver
    participant A as Agent

    E->>G: Create GameParams from state
    E->>S: Call game function (e.g., definition_game)
    S->>S: Compute payoff matrices
    S-->>E: Return TwoPlayerGame
    E->>N: solve_all_equilibria(game)
    N-->>E: List of equilibria
    E->>A: Select equilibrium (welfare/risk-dominant)
    A-->>E: Chosen actions
    E->>E: Update state variables
```

---

## Data Pipeline (Snakemake DAG)

```mermaid
flowchart LR
    subgraph prep["Preparation"]
        check["check_parameters_grounded"]
        context["build_context_pack"]
    end

    subgraph sim["Simulation"]
        baseline["run_baseline"]
        sensitivity["run_sobol_analysis"]
        scenarios["run_scenarios"]
    end

    subgraph viz["Visualization"]
        figures["generate_figures"]
        reports["generate_reports"]
    end

    check --> baseline
    context --> baseline
    baseline --> sensitivity
    baseline --> scenarios
    sensitivity --> figures
    scenarios --> figures
    figures --> reports
```

---

## Stage Game Categories

```mermaid
mindmap
  root((Stage Games))
    Funding Negotiation
      Definition Game
      Bargaining Game
      Cost Shifting Game
    Discharge & Interface
      Discharge Coordination
      Governance Integration
      Aged Care Interface
      NDIS Interface
    Compliance & Audit
      Coding/Audit Game
      Compliance Game
```

---

## Parameter Dependencies

```mermaid
flowchart TD
    subgraph state["State Variables"]
        pressure["pressure"]
        eg["efficiency_gap"]
        dd["discharge_delay"]
        ps["political_salience"]
        ap["audit_pressure"]
        csi["cost_shifting_intensity"]
        pc["political_capital"]
    end

    subgraph games["Affected Games"]
        def["Definition"]
        bar["Bargaining"]
        cost["Cost Shifting"]
        disc["Discharge Coord"]
        gov["Governance"]
        aged["Aged Care"]
        ndis["NDIS"]
        audit["Coding/Audit"]
        comp["Compliance"]
    end

    pressure --> def
    pressure --> bar
    pressure --> cost
    pressure --> disc
    pressure --> gov
    pressure --> aged
    pressure --> ndis

    eg --> def
    eg --> cost
    eg --> audit
    eg --> comp

    dd --> disc
    dd --> aged
    dd --> ndis

    ps --> def
    ps --> bar
    ps --> gov

    ap --> audit
    ap --> comp

    csi --> cost

    pc --> bar
```

---

## See Also

- [Design Documentation](design.md) for architecture details
- [Models Reference](guides/models.md) for game specifications
