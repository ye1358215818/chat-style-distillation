#!/usr/bin/env python3
"""Anonymize chat exports before companion distillation or publication."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from chat_style_distillation.privacy import (  # noqa: E402
    HARD_IDENTIFIER_PATTERNS,
    MODE_PATTERNS,
    PUBLISH_EXTRA_PATTERNS,
    audit_candidates,
    anonymize,
    load_anchor_items,
    parse_replace,
    parse_replace_file,
)


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
    parser.add_argument("--replace-file", action="append", default=[], type=Path, help="Replacement file: JSON, OLD=NEW, or OLD<TAB>NEW.")
    parser.add_argument("--keep-anchor", action="append", default=[], help="Literal anchor or file of anchors to preserve when safe.")
    parser.add_argument("--self-name", help="User/self display name to replace with SELF.")
    parser.add_argument("--other-name", help="Other person's display name to replace with OTHER.")
    parser.add_argument("--audit-output", "--review-candidates", dest="audit_output", type=Path, help="Write possible privacy candidates to JSON.")
    args = parser.parse_args()

    replacements = parse_replace(args.replace)
    for replace_file in args.replace_file:
        replacements.extend(parse_replace_file(replace_file))
    keep_anchors = load_anchor_items(args.keep_anchor)

    text = args.input.read_text(encoding="utf-8")
    sanitized, counts = anonymize(
        text,
        replacements,
        self_name=args.self_name,
        other_name=args.other_name,
        mode=args.mode,
        keep_anchors=keep_anchors,
    )

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
        candidates = audit_candidates(sanitized, full=True)
        args.audit_output.parent.mkdir(parents=True, exist_ok=True)
        args.audit_output.write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Audit: {args.audit_output}")


if __name__ == "__main__":
    main()
