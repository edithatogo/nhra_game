import json
import subprocess
from pathlib import Path


def test_build_figure_report_smoke(tmp_path):
    """Verify that the report builder script runs and produces output."""

    # Mock registry
    registry = [
        {
            "id": "test_fig",
            "source_file": "src/test.py",
            "function_name": "plot_test",
            "output_path": "outputs/test.png",
            "description": "Test description",
            "status": "active",
        }
    ]

    reg_path = tmp_path / "registry.json"
    with open(reg_path, "w") as f:
        json.dump(registry, f)

    # We need to run the script. Since it uses hardcoded paths (relative to cwd),
    # we might need to modify the script or run it in a way that respects tmp_path.
    # But the script uses 'docs/reports/...'.
    # So strictly testing the script *as is* requires the files to exist in the real path.
    # Alternatively, we can import the main function if we refactor it to accept paths.

    # Let's verify the actual script runs on the actual data as an integration smoke test.
    cmd = ["python", "scripts/build_figure_report.py"]
    result = subprocess.run(cmd, capture_output=True, text=True)  # nosec
    assert result.returncode == 0
    assert "Report generated" in result.stdout
    assert Path("docs/reports/figure_inventory.md").exists()
