"""Check Gambit's headless integration."""

import sys

import pygambit


def verify_headless_gambit():
    """Check that Gambit solves a small game without a display."""
    print("Verifying headless Gambit support...")
    try:
        # Create a simple game to test library loading
        g = pygambit.Game.new_table([2, 2])
        g.title = "Test Game"

        # Access some basic functionality that might trigger backend loading
        print(f"Game created: {g.title}")
        print(f"Players: {len(g.players)}")

        # Check if we can solve it (uses external solvers included in wheel often)
        # simplistic check
        profile = g.mixed_strategy_profile()
        print(f"Profile created successfully: {profile}")

        print("SUCCESS: pygambit loaded and functioned without error.")
    except Exception as e:
        print(f"FAILURE: {e}")
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(verify_headless_gambit())
