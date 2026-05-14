#!/usr/bin/env python3
"""Evaluate a companion-mode transcript for immersion risks.

This is a lightweight local check. It does not decide whether the voice is
"accurate"; it catches common failure modes before a companion prompt is reused.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


META_PATTERNS = [
    r"\[.*?mode.*?\]",
    r"based on (the )?(chat|logs|records)",
    r"as an ai",
    r"我切到",
    r"根据聊天记录",
    r"作为一个",
    r"模式",
]

PLACEHOLDER_PATTERNS = [
    r"PERSON_[A-Z]",
    r"LOCATION_[A-Z]",
    r"\[(?:PHONE|EMAIL|ID_CARD|WXID|URL|WINDOWS_PATH)\]",
]

THERAPY_SPEAK = [
    "情绪价值",
    "创伤",
    "依恋",
    "边界感",
    "课题分离",
    "原生家庭",
    "认知",
]


def count_patterns(text: str, patterns: list[str]) -> int:
    return sum(len(re.findall(pattern, text, flags=re.IGNORECASE)) for pattern in patterns)


def evaluate(text: str) -> dict[str, object]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    lengths = [len(line) for line in lines]
    meta_hits = count_patterns(text, META_PATTERNS)
    placeholder_hits = count_patterns(text, PLACEHOLDER_PATTERNS)
    therapy_hits = sum(text.count(word) for word in THERAPY_SPEAK)

    score = 100
    score -= min(meta_hits * 20, 40)
    score -= min(placeholder_hits * 15, 30)
    score -= min(therapy_hits * 5, 20)

    warnings: list[str] = []
    if meta_hits:
        warnings.append("Contains narrator/method/mode language that can break immersion.")
    if placeholder_hits:
        warnings.append("Contains sterile placeholders; consider natural memory wording for private companion use.")
    if therapy_hits:
        warnings.append("Contains therapy-speak; verify the user asked for analysis rather than immersive chat.")
    if lines and max(lengths) > 240:
        warnings.append("Contains very long chat lines; verify this matches the source person's real style.")

    return {
        "score": max(score, 0),
        "line_count": len(lines),
        "avg_line_length": round(sum(lengths) / len(lengths), 2) if lengths else 0,
        "max_line_length": max(lengths) if lengths else 0,
        "meta_hits": meta_hits,
        "placeholder_hits": placeholder_hits,
        "therapy_speak_hits": therapy_hits,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate companion-mode transcript immersion.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, help="Write JSON report to this path. Defaults to stdout.")
    args = parser.parse_args()

    report = evaluate(args.input.read_text(encoding="utf-8"))
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print(f"Wrote: {args.output}")
    else:
        print(payload)


if __name__ == "__main__":
    main()
