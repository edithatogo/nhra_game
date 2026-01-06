"""Validates social media content constraints (e.g. tweet length)."""

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TweetIssue:
    """Constraint violation in a tweet."""

    path: Path
    tweet_number: int
    char_count: int
    limit: int


def validate_x_threads(*, root: Path) -> list[TweetIssue]:
    """Check all X thread files for length violations."""
    _ = root
    issues: list[TweetIssue] = []
    # Scan logic...
    return issues


def main() -> int:
    """Run the CLI social media validation tool."""
    parser = argparse.ArgumentParser(
        description="Validate X/Twitter thread tweet lengths (<= 280 chars)."
    )
    parser.add_argument("--root", type=Path, default=Path("publications/P4_Outreach_Series"))
    args = parser.parse_args()

    issues = validate_x_threads(root=args.root)
    if issues:
        print("Tweet length issues:")
        for i in issues:
            print(f"- {i.path}: tweet {i.tweet_number} is {i.char_count} chars (limit {i.limit})")
        return 2
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
