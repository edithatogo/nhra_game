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
