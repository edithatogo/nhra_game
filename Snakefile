rule all:
    input:
        "data/calibration_v21/calibration_optuna_best.csv",
        "data/baseline_v21/trajectory.csv",
        "outputs/v8/plots/tradeoff_scatter.png",
        "outputs/v9/diagrams/games_network_minimal_v9.png",
        "outputs/v9/interactive/games_network_d3.html",
        "context/CONTEXT_PACK.md",
        "context/grounding.ok"

rule calibrate:
    input:
        "data/raw/calibration_targets.csv"
    output:
        "data/calibration_v21/calibration_optuna_best.csv",
        "data/calibration_v21/calibration_trials_posterior.csv"
    shell:
        "PYTHONPATH=src python scripts/optimize_calibration_v21.py"

rule run_baseline:
    output:
        "data/baseline_v21/trajectory.csv"
    shell:
        "PYTHONPATH=src python scripts/run_baseline_v21.py"

rule run_v8:
    output:
        "outputs/v8/plots/tradeoff_scatter.png"
    shell:
        "PYTHONPATH=src python scripts/run_v8_all.py"

rule render_diagrams:
    input:
        "outputs/v8/plots/tradeoff_scatter.png"
    output:
        "outputs/v9/diagrams/games_network_minimal_v9.png"
    shell:
        "PYTHONPATH=src python scripts/diagrams/render_all.py"

rule make_d3:
    input:
        "outputs/v9/diagrams/games_network_minimal_v9.png"
    output:
        "outputs/v9/interactive/games_network_d3.html"
    shell:
        "PYTHONPATH=src python scripts/interactive/make_d3_network_v9.py"

rule context_pack:
    output:
        "context/CONTEXT_PACK.md"
    shell:
        "python scripts/build_context_pack.py"

rule check_grounding:
    output:
        "context/grounding.ok"
    shell:
        "python scripts/check_parameters_grounded.py && echo OK > context/grounding.ok"
