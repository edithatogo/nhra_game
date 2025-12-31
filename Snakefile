import sys

PY = sys.executable

rule all:
    input:
        "data/gsa/sensitivity_summary.md",
        "data/calibration/calibration_optuna_best.csv",
        "data/baseline/tables/trajectory.csv",
        "outputs/diagrams/games_network_minimal.png",
        "outputs/interactive/games_network_d3.html",
        "context/CONTEXT_PACK.md",
        "context/grounding.ok",
        "reports/validation_report.md"

rule preprocess_historical:
    input:
        "data/raw/historical_aihw_ed.csv"
    output:
        "data/calibration/historical_normalized.csv"
    shell:
        "PYTHONPATH=src python scripts/data/preprocess_historical.py"

rule backtest_recursive:
    input:
        "data/calibration/historical_normalized.csv"
    output:
        "data/calibration/recursive_results.json"
    shell:
        "LOGFIRE_SEND_TO_LOGFIRE=false PYTHONPATH=src python scripts/validation/recursive_backtest.py"

rule plot_validation:
    input:
        "data/calibration/recursive_results.json"
    output:
        "outputs/validation/theil_decomposition.png"
    shell:
        "LOGFIRE_SEND_TO_LOGFIRE=false PYTHONPATH=src python scripts/validation/plot_theil_decomposition.py"

rule validate_mechanism_script:
    input:
        "data/gsa/morris_results.csv"
    output:
        touch("outputs/validation/mechanism.ok")
    shell:
        "LOGFIRE_SEND_TO_LOGFIRE=false PYTHONPATH=src python scripts/validation/validate_mechanism.py && touch outputs/validation/mechanism.ok"

rule generate_report:
    input:
        "data/calibration/recursive_results.json",
        "outputs/validation/theil_decomposition.png",
        "data/gsa/morris_results.csv"
    output:
        "reports/validation_report.md"
    shell:
        "LOGFIRE_SEND_TO_LOGFIRE=false PYTHONPATH=src python scripts/validation/generate_validation_report.py"

rule validate:
    input:
        "reports/validation_report.md",
        "outputs/validation/mechanism.ok"

rule gsa_morris:
    output:
        "data/gsa/morris_results.csv",
        "data/gsa/morris_tornado.png"
    shell:
        "PYTHONPATH=src python scripts/run_gsa.py --method morris --samples 10 --output data/gsa/morris_results.csv"

rule gsa_sobol:
    input:
        "data/gsa/morris_results.csv"
    output:
        "data/gsa/sobol_results.csv",
        "data/gsa/sensitivity_summary.md"
    shell:
        "PYTHONPATH=src python scripts/run_gsa.py --method sobol --samples 32 --output data/gsa/sobol_results.csv"

rule calibrate:
    input:
        "data/raw/calibration_targets.csv"
    output:
        "data/calibration/calibration_optuna_best.csv",
        "data/calibration/calibration_trials_posterior.csv"
    shell:
        "PYTHONPATH=src python scripts/optimize_calibration.py"

rule run_baseline:
    output:
        "data/baseline/tables/trajectory.csv"
    shell:
        f"\"{PY}\" scripts/run_baseline.py"

rule render_diagrams:
    output:
        "outputs/diagrams/games_network_minimal.png"
    shell:
        "PYTHONPATH=src python scripts/diagrams/render_all.py"

rule make_d3:
    input:
        "outputs/diagrams/games_network_minimal.png"
    output:
        "outputs/interactive/games_network_d3.html"
    shell:
        "PYTHONPATH=src python scripts/interactive/make_d3_network.py"

rule context_pack:
    output:
        "context/CONTEXT_PACK.md"
    shell:
        f"\"{PY}\" scripts/build_context_pack.py"

rule check_grounding:
    output:
        "context/grounding.ok"
    shell:
        f"\"{PY}\" scripts/check_parameters_grounded.py && echo OK > context/grounding.ok"
