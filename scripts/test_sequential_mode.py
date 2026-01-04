from nhra_gt.domain.state import ParamsJax
from nhra_gt.engine import run_simulation


def test_sequential_impact():
    print("Running Baseline (Nash)...")
    p_nash = ParamsJax(use_sequential_bargaining=False)
    res_nash = run_simulation(years=10, params=p_nash, seed=42)

    print("Running Sequential (Stackelberg)...")
    p_seq = ParamsJax(use_sequential_bargaining=True)
    res_seq = run_simulation(years=10, params=p_seq, seed=42)

    # Compare Effective Commonwealth Share at end
    share_nash = res_nash["effective_cth_share"][-1]
    share_seq = res_seq["effective_cth_share"][-1]

    print(f"Nash End Share: {share_nash:.4f}")
    print(f"Seq  End Share: {share_seq:.4f}")

    diff = abs(share_nash - share_seq)
    print(f"Difference: {diff:.4f}")

    if diff < 1e-6:
        print(
            "WARNING: No difference observed. Solver might be defaulting to same outcome or not active."
        )
    else:
        print("SUCCESS: Sequential mode produced distinct outcome.")


if __name__ == "__main__":
    test_sequential_impact()
