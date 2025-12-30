import os
import sys

import textstat


def analyze_file(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, encoding="utf-8") as f:
        text = f.read()

    # Basic stats
    flesch_reading_ease = textstat.flesch_reading_ease(text)
    flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
    smog_index = textstat.smog_index(text)
    coleman_liau_index = textstat.coleman_liau_index(text)
    automated_readability_index = textstat.automated_readability_index(text)
    dale_chall_readability_score = textstat.dale_chall_readability_score(text)
    difficult_words = textstat.difficult_words(text)
    linsear_write_formula = textstat.linsear_write_formula(text)
    gunning_fog = textstat.gunning_fog(text)
    text_standard = textstat.text_standard(text)

    # Detailed sentence check
    sentences = text.split(".")
    long_sentences = [s.strip() for s in sentences if len(s.split()) > 30]

    report = f"""# Readability Report: {os.path.basename(file_path)}

## Summary Scores
- **Flesch Reading Ease:** {flesch_reading_ease} (Higher is easier)
- **Flesch-Kincaid Grade Level:** {flesch_kincaid_grade} (Target: 12-14 for academic)
- **SMOG Index:** {smog_index}
- **Coleman–Liau Index:** {coleman_liau_index}
- **Automated Readability Index:** {automated_readability_index}
- **Dale–Chall Readability Score:** {dale_chall_readability_score}
- **Linsear Write Formula:** {linsear_write_formula}
- **Gunning Fog Index:** {gunning_fog}
- **Consensus Grade Level:** {text_standard}

## Detailed Metrics
- **Difficult Words Count:** {difficult_words}
- **Average Words Per Sentence:** {textstat.lexicon_count(text) / max(1, textstat.sentence_count(text)):.2f}

## Flags
### Long Sentences (>30 words)
"""
    for i, s in enumerate(long_sentences):
        report += f'{i + 1}. "{s}..."\n'

    return report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_readability.py <file_path>")
        sys.exit(1)

    report_output = analyze_file(sys.argv[1])
    print(report_output)
