from scripts.generate_policy_brief import generate_brief


def test_generate_policy_brief_smoke(tmp_path):
    """Verify that the policy brief PDF can be generated without error."""
    out_path = tmp_path / "test_brief.pdf"
    generate_brief("Test Scenario", out_path)

    assert out_path.exists()
    assert out_path.stat().st_size > 0
