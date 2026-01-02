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
        "PYTHONPATH=src python scripts/run_baseline.py"

rule backtest_recursive:
    input:
        "data/calibration/historical_normalized.csv"
    output:
        "data/calibration/recursive_results.json"
    shell:
        "LOGFIRE_SEND_TO_LOGFIRE=false PYTHONPATH=src python scripts/validation/recursive_backtest.py"
