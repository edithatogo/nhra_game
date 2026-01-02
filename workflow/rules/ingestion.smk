rule preprocess_historical:
    input:
        "data/raw/historical_aihw_ed.csv"
    output:
        "data/calibration/historical_normalized.csv"
    shell:
        "PYTHONPATH=src python scripts/data/preprocess_historical.py"

rule context_pack:
    output:
        "context/CONTEXT_PACK.md"
    shell:
        "PYTHONPATH=src python scripts/build_context_pack.py"

rule check_grounding:
    output:
        "context/grounding.ok"
    shell:
        "PYTHONPATH=src python scripts/check_parameters_grounded.py && echo OK > context/grounding.ok"
