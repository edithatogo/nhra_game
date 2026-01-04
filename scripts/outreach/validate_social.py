from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TweetIssue:
    path: Path
    tweet_number: int
    char_count: int
    limit: int = 280


def _parse_tweets(text: str) -> list[str]:
    """
    Parse tweets from a thread Markdown file.

    Expected minimal format:
    - Each tweet starts with a line like: "Tweet 1:" or "Tweet 1 -"
    - Tweet content continues until the next "Tweet N" header.
    """
    lines = text.splitlines()
    tweet_starts: list[tuple[int, int]] = []
    header = re.compile(r"^\s*Tweet\s+(\d+)\s*[:\-]\s*(.*)$", re.IGNORECASE)
    for i, line in enumerate(lines):
        m = header.match(line)
        if m:
            tweet_starts.append((i, int(m.group(1))))
    if not tweet_starts:
        return []

    tweets: list[str] = []
    for idx, (start_line, _num) in enumerate(tweet_starts):
        end_line = tweet_starts[idx + 1][0] if idx + 1 < len(tweet_starts) else len(lines)
        block = "\n".join(lines[start_line:end_line]).strip()
        # Remove the "Tweet N:" header for counting
        block = header.sub(r"\2", block, count=1).strip()
        tweets.append(block)
    return tweets


def validate_x_threads(*, root: Path) -> list[TweetIssue]:
    issues: list[TweetIssue] = []
    for path in root.rglob("x_thread_v*_????????.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        tweets = _parse_tweets(text)
        for i, tweet in enumerate(tweets, start=1):
            count = len(tweet)
            if count > 280:
                issues.append(TweetIssue(path=path, tweet_number=i, char_count=count))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate X/Twitter thread tweet lengths (<= 280 chars).")
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

