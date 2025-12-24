rule all:
    input:
        "data/gsa_v21/sensitivity_summary.md",
        "data/calibration_v21/calibration_optuna_best.csv",
        "data/baseline_v21/tables/trajectory.csv",
        "outputs/v8/plots/tradeoff_scatter.png",
        "outputs/v9/diagrams/games_network_minimal_v9.png",
        "outputs/v9/interactive/games_network_d3.html",
        "context/CONTEXT_PACK.md",
        "context/grounding.ok",
        "reports/validation_report_v21.md"

rule preprocess_historical:
    input:
        "data/raw/historical_aihw_ed.csv"
    output:
        "data/calibration_v21/historical_normalized.csv"
    shell:
        "PYTHONPATH=src python scripts/data/preprocess_historical.py"

rule backtest_recursive:
    input:
        "data/calibration_v21/historical_normalized.csv"
    output:
        "data/calibration_v21/recursive_results.json"
    shell:
        "LOGFIRE_SEND_TO_LOGFIRE=false PYTHONPATH=src python scripts/validation/recursive_backtest.py"

rule plot_validation:
    input:
        "data/calibration_v21/recursive_results.json"
    output:
        "outputs/validation/theil_decomposition.png"
    shell:
        "LOGFIRE_SEND_TO_LOGFIRE=false PYTHONPATH=src python scripts/validation/plot_theil_decomposition.py"

rule validate_mechanism_script:
    input:
        "data/gsa_v21/morris_results.csv"
    output:
        touch("outputs/validation/mechanism.ok")
    shell:
        "LOGFIRE_SEND_TO_LOGFIRE=false PYTHONPATH=src python scripts/validation/validate_mechanism.py && touch outputs/validation/mechanism.ok"

rule generate_report:
    input:
        "data/calibration_v21/recursive_results.json",
        "outputs/validation/theil_decomposition.png",
        "data/gsa_v21/morris_results.csv"
    output:
        "reports/validation_report_v21.md"
    shell:
        "LOGFIRE_SEND_TO_LOGFIRE=false PYTHONPATH=src python scripts/validation/generate_validation_report.py"

rule validate:
    input:
        "reports/validation_report_v21.md",
        "outputs/validation/mechanism.ok"

rule gsa_morris:
    output:
        "data/gsa_v21/morris_results.csv",
        "data/gsa_v21/morris_tornado.png"
    shell:
        "PYTHONPATH=src python scripts/run_gsa.py --method morris --samples 10 --output data/gsa_v21/morris_results.csv"

rule gsa_sobol:
    input:
        "data/gsa_v21/morris_results.csv"
    output:
        "data/gsa_v21/sobol_results.csv",
        "data/gsa_v21/sensitivity_summary.md"
    shell:
        "PYTHONPATH=src python scripts/run_gsa.py --method sobol --samples 32 --output data/gsa_v21/sobol_results.csv"

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
        "data/baseline_v21/tables/trajectory.csv"
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
