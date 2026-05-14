#!/usr/bin/env python3
"""Anonymize chat exports before analysis or publication.

This script is intentionally conservative and dependency-free. It redacts common
identifiers while preserving enough structure for style analysis.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("WXID", re.compile(r"\bwxid_[a-zA-Z0-9_-]{6,}\b")),
    ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("PHONE", re.compile(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)")),
    ("ID_CARD", re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)")),
    ("URL", re.compile(r"https?://[^\s<>\"]+")),
    ("WINDOWS_PATH", re.compile(r"[A-Za-z]:\\(?:[^\\/:*?\"<>|\r\n]+\\)*[^\\/:*?\"<>|\r\n]*")),
    ("MONEY", re.compile(r"(?:￥|¥)\s?\d+(?:\.\d+)?|\b\d+(?:\.\d+)?\s?元\b")),
]


def parse_replace(items: list[str]) -> list[tuple[str, str]]:
    replacements: list[tuple[str, str]] = []
    for item in items:
        if "=" not in item:
            raise SystemExit(f"--replace expects OLD=NEW, got: {item}")
        old, new = item.split("=", 1)
        if old:
            replacements.append((old, new))
    return replacements


def anonymize(text: str, replacements: list[tuple[str, str]], self_name: str | None, other_name: str | None) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}

    if self_name:
        replacements.append((self_name, "SELF"))
    if other_name:
        replacements.append((other_name, "OTHER"))

    for old, new in replacements:
        n = text.count(old)
        if n:
            counts[f"literal:{new}"] = counts.get(f"literal:{new}", 0) + n
            text = text.replace(old, new)

    for label, pattern in PATTERNS:
        text, n = pattern.subn(f"[{label}]", text)
        if n:
            counts[label] = n

    return text, counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Anonymize chat export text.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--replace", action="append", default=[], help="Literal replacement OLD=NEW. May be repeated.")
    parser.add_argument("--self-name", help="User/self display name to replace with SELF.")
    parser.add_argument("--other-name", help="Other person's display name to replace with OTHER.")
    args = parser.parse_args()

    text = args.input.read_text(encoding="utf-8")
    sanitized, counts = anonymize(text, parse_replace(args.replace), args.self_name, args.other_name)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(sanitized, encoding="utf-8", newline="\n")

    print(f"Wrote: {args.output}")
    if counts:
        for key in sorted(counts):
            print(f"{key}: {counts[key]}")
    else:
        print("No redactions matched.")


if __name__ == "__main__":
    main()
