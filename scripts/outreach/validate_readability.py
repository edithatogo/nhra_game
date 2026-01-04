from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReadabilityResult:
    path: Path
    words: int
    sentences: int
    syllables: int
    flesch_kincaid_grade: float


_word_re = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")


def _count_syllables(word: str) -> int:
    w = word.lower()
    w = re.sub(r"[^a-z]", "", w)
    if not w:
        return 0
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for ch in w:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if w.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def _split_sentences(text: str) -> list[str]:
    # Simple sentence split suitable for heuristics.
    parts = re.split(r"[.!?]+", text)
    return [p.strip() for p in parts if p.strip()]


def score_text(text: str) -> tuple[int, int, int, float]:
    words = _word_re.findall(text)
    sentences = _split_sentences(text)
    syllables = sum(_count_syllables(w) for w in words)
    n_words = len(words)
    n_sent = max(1, len(sentences))
    # Flesch–Kincaid grade level
    grade = 0.39 * (n_words / n_sent) + 11.8 * (syllables / max(1, n_words)) - 15.59
    return n_words, len(sentences), syllables, float(grade)


def validate_articles(
    *, root: Path, max_grade: float = 9.5
) -> tuple[list[ReadabilityResult], list[ReadabilityResult]]:
    ok: list[ReadabilityResult] = []
    too_hard: list[ReadabilityResult] = []

    for path in root.rglob("linkedin_article_v*_????????.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        n_words, n_sent, n_syll, grade = score_text(text)
        res = ReadabilityResult(
            path=path, words=n_words, sentences=n_sent, syllables=n_syll, flesch_kincaid_grade=grade
        )
        if grade <= max_grade:
            ok.append(res)
        else:
            too_hard.append(res)

    return ok, too_hard


def _pick_latest_versions(paths: list[Path]) -> list[Path]:
    """
    Pick only the latest version per directory, based on filename `..._v<NUM>_YYYYMMDD.md`.
    """
    by_dir: dict[Path, list[tuple[int, str, Path]]] = {}
    pat = re.compile(r"^linkedin_article_v(\d+)_(\d{8})\.md$")
    for p in paths:
        m = pat.match(p.name)
        if not m:
            continue
        v = int(m.group(1))
        d = m.group(2)
        by_dir.setdefault(p.parent, []).append((v, d, p))

    latest: list[Path] = []
    for _dir, items in by_dir.items():
        items.sort(key=lambda x: (x[0], x[1]))
        latest.append(items[-1][2])
    return sorted(latest)


def validate_latest_articles(
    *, root: Path, max_grade: float = 9.5
) -> tuple[list[ReadabilityResult], list[ReadabilityResult]]:
    paths = list(root.rglob("linkedin_article_v*_????????.md"))
    latest_paths = _pick_latest_versions(paths)

    ok: list[ReadabilityResult] = []
    too_hard: list[ReadabilityResult] = []
    for path in latest_paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        n_words, n_sent, n_syll, grade = score_text(text)
        res = ReadabilityResult(
            path=path, words=n_words, sentences=n_sent, syllables=n_syll, flesch_kincaid_grade=grade
        )
        if grade <= max_grade:
            ok.append(res)
        else:
            too_hard.append(res)
    return ok, too_hard


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate readability heuristics for LinkedIn articles."
    )
    parser.add_argument("--root", type=Path, default=Path("publications/P4_Outreach_Series"))
    parser.add_argument("--max-grade", type=float, default=9.5)
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all versions (default: only latest version per bundle).",
    )
    args = parser.parse_args()

    if args.all:
        ok, too_hard = validate_articles(root=args.root, max_grade=args.max_grade)
    else:
        ok, too_hard = validate_latest_articles(root=args.root, max_grade=args.max_grade)
    if too_hard:
        print("Readability issues (Flesch–Kincaid grade too high):")
        for r in too_hard:
            print(
                f"- {r.path}: grade={r.flesch_kincaid_grade:.1f} words={r.words} sentences={r.sentences}"
            )
        return 2
    print(f"ok articles_scored={len(ok)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
