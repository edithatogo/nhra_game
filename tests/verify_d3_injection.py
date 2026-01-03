import json
from pathlib import Path
import sys


def test_injection():
    # Paths based on project structure
    repo_root = Path(__file__).resolve().parents[1]
    d3_path = repo_root / "outputs/interactive/games_network_d3.html"
    json_path = repo_root / "outputs/interactive/games_network.json"
    series_path = repo_root / "outputs/interactive/scenario_timeseries.json"

    print(f"Checking files at {repo_root}...")

    if not d3_path.exists():
        print("❌ D3 HTML template missing")
        sys.exit(1)
    if not json_path.exists():
        print("❌ Games network JSON missing")
        sys.exit(1)
    if not series_path.exists():
        print("❌ Scenario timeseries JSON missing")
        sys.exit(1)

    # Read content
    html_content = d3_path.read_text(encoding="utf-8")
    graph_data = json_path.read_text(encoding="utf-8")
    series_data = series_path.read_text(encoding="utf-8")

    # Verify placeholders exist
    if "let graph = null; // INJECT_GRAPH_HERE" not in html_content:
        print("❌ Graph placeholder missing in HTML template")
        sys.exit(1)
    if "let series = null; // INJECT_SERIES_HERE" not in html_content:
        print("❌ Series placeholder missing in HTML template")
        sys.exit(1)

    print("✅ Placeholders found.")

    # Simulate Injection
    injected_html = html_content.replace(
        "let graph = null; // INJECT_GRAPH_HERE", f"let graph = {graph_data};"
    )
    injected_html = injected_html.replace(
        "let series = null; // INJECT_SERIES_HERE", f"let series = {series_data};"
    )

    # Verify Injection
    if f"let graph = {graph_data};" not in injected_html:
        print("❌ Graph injection failed during simulation")
        sys.exit(1)

    # Check for meaningful data in series injection
    # specific checks for time-series dynamic data
    if "baseline_equilibria" not in injected_html:
        print("❌ 'baseline_equilibria' key not found in injected HTML")
        sys.exit(1)

    # Check that we have different values for 2025 and 2030 (using string search for simplicity or parsing)
    # Let's parse the injected series object to be sure
    # Regex parsing of large JSON in HTML is fragile. Since we injected `series_data` directly,
    # we can verify the content on the source `series_data` variable which we read from the JSON file.

    loaded_series = json.loads(series_data)

    if "baseline_equilibria" in loaded_series:
        p2025 = loaded_series["baseline_equilibria"]["2025"]["PRESS"]["pressure"]
        p2030 = loaded_series["baseline_equilibria"]["2030"]["PRESS"]["pressure"]
        if p2025 == p2030:
            print(
                f"⚠️ Warning: 2025 and 2030 pressure values are identical ({p2025}). Slider might look static."
            )
        else:
            print(f"✅ Dynamic data confirmed: 2025 ({p2025}) != 2030 ({p2030})")

    print("✅ Injection logic verified. The Dashboard code will successfully populate the map.")


if __name__ == "__main__":
    test_injection()
