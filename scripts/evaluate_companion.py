#!/usr/bin/env python3
"""Evaluate a companion-mode transcript for immersion and drift risks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from chat_style_distillation.evaluate import (  # noqa: E402
    GENERIC_ROMANCE,
    META_PATTERNS,
    PLACEHOLDER_PATTERNS,
    THERAPY_SPEAK,
    count_patterns,
    evaluate,
)


def _load_json(path: Path | None) -> dict[str, Any] | None:
    if not path:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate companion-mode transcript immersion.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--profile", type=Path, help="Optional style-profile.json for source comparison.")
    parser.add_argument("--analysis", type=Path, help="Optional analysis-summary.json for source comparison.")
    parser.add_argument("--output", type=Path, help="Write JSON report to this path. Defaults to stdout.")
    args = parser.parse_args()

    report = evaluate(
        args.input.read_text(encoding="utf-8"),
        profile=_load_json(args.profile),
        analysis=_load_json(args.analysis),
    )
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print(f"Wrote: {args.output}")
    else:
        print(payload)


if __name__ == "__main__":
    main()
