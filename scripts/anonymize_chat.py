#!/usr/bin/env python3
"""Anonymize chat exports before companion distillation or publication.

This script is intentionally dependency-free. It supports two privacy modes:

- companion: keep emotional anchors for private local companion work while
  redacting hard identifiers.
- publish: strongly redact for sharing, examples, or commits.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


HARD_IDENTIFIER_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("WXID", re.compile(r"\bwxid_[a-zA-Z0-9_-]{6,}\b")),
    ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("PHONE", re.compile(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)")),
    ("ID_CARD", re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)")),
    ("URL", re.compile(r"https?://[^\s<>\"]+")),
    ("WINDOWS_PATH", re.compile(r"[A-Za-z]:\\(?:[^\\/:*?\"<>|\r\n]+\\)*[^\\/:*?\"<>|\r\n]*")),
]

PUBLISH_EXTRA_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("MONEY", re.compile(r"(?:￥|¥)\s?\d+(?:\.\d+)?|\b\d+(?:\.\d+)?\s?元\b")),
]

MODE_PATTERNS = {
    "companion": HARD_IDENTIFIER_PATTERNS,
    "publish": HARD_IDENTIFIER_PATTERNS + PUBLISH_EXTRA_PATTERNS,
}

AUDIT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("LONG_NUMBER", re.compile(r"(?<!\d)\d{6,}(?!\d)")),
    ("DATE_LIKE", re.compile(r"\b\d{4}[-/.年]\d{1,2}(?:[-/.月]\d{1,2}日?)?\b")),
    ("QQ_LIKE", re.compile(r"(?<!\d)[1-9]\d{4,11}(?!\d)")),
    ("LOCATION_HINT", re.compile(r"[\u4e00-\u9fff]{2,12}(?:小区|公寓|学校|大学|公司|医院|酒店|路|街|镇|村|区|市)")),
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


def anonymize(
    text: str,
    replacements: list[tuple[str, str]],
    self_name: str | None,
    other_name: str | None,
    mode: str,
) -> tuple[str, dict[str, int]]:
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

    for label, pattern in MODE_PATTERNS[mode]:
        text, n = pattern.subn(f"[{label}]", text)
        if n:
            counts[label] = n

    return text, counts


def audit_candidates(text: str, limit: int = 80) -> dict[str, list[str]]:
    candidates: dict[str, list[str]] = {}
    for label, pattern in AUDIT_PATTERNS:
        seen: list[str] = []
        for match in pattern.finditer(text):
            value = match.group(0)
            if value not in seen:
                seen.append(value)
            if len(seen) >= limit:
                break
        if seen:
            candidates[label] = seen
    return candidates


def main() -> None:
    parser = argparse.ArgumentParser(description="Anonymize chat export text.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--mode",
        choices=sorted(MODE_PATTERNS),
        default="publish",
        help="companion keeps non-identifying emotional anchors; publish strongly redacts for sharing.",
    )
    parser.add_argument("--replace", action="append", default=[], help="Literal replacement OLD=NEW. May be repeated.")
    parser.add_argument("--self-name", help="User/self display name to replace with SELF.")
    parser.add_argument("--other-name", help="Other person's display name to replace with OTHER.")
    parser.add_argument("--audit-output", type=Path, help="Write possible remaining privacy candidates to JSON.")
    args = parser.parse_args()

    text = args.input.read_text(encoding="utf-8")
    sanitized, counts = anonymize(text, parse_replace(args.replace), args.self_name, args.other_name, args.mode)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(sanitized, encoding="utf-8", newline="\n")

    print(f"Wrote: {args.output}")
    print(f"Mode: {args.mode}")
    if counts:
        for key in sorted(counts):
            print(f"{key}: {counts[key]}")
    else:
        print("No redactions matched.")

    if args.audit_output:
        candidates = audit_candidates(sanitized)
        args.audit_output.parent.mkdir(parents=True, exist_ok=True)
        args.audit_output.write_text(
            json.dumps(candidates, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Audit: {args.audit_output}")


if __name__ == "__main__":
    main()
