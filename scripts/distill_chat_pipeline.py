#!/usr/bin/env python3
"""Run the v5 local chat-style distillation pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from chat_style_distillation.parsers import parser_choices  # noqa: E402
from chat_style_distillation.pipeline import run_pipeline  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a local chat style distillation output bundle.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", "--out-dir", dest="output_dir", type=Path, required=True)
    parser.add_argument("--mode", choices=["companion", "publish"], default="companion")
    parser.add_argument("--format", choices=parser_choices(), default="auto")
    parser.add_argument("--self-name")
    parser.add_argument("--other-name", default="OTHER")
    parser.add_argument("--replace-file", action="append", default=[], type=Path)
    parser.add_argument("--keep-anchor", action="append", default=[])
    parser.add_argument("--full-privacy-audit", action="store_true")
    parser.add_argument("--expected-start")
    parser.add_argument("--expected-end")
    parser.add_argument("--min-messages", type=int, default=50)
    parser.add_argument("--relationship-mode", choices=["ex", "lost-contact", "friend", "family", "other"], default="other")
    parser.add_argument("--locale", choices=["zh-CN", "en-US"], default="zh-CN")
    parser.add_argument("--evidence-limit", type=int, default=5)
    parser.add_argument("--generate-eval-replies", action="store_true")
    parser.add_argument("--publish-redact-names", action="store_true")
    parser.add_argument("--top-n", type=int, default=30)
    parser.add_argument("--burst-gap-minutes", type=int, default=3)
    args = parser.parse_args()

    manifest = run_pipeline(
        args.input,
        args.output_dir,
        self_name=args.self_name,
        other_name=args.other_name,
        mode=args.mode,
        fmt=args.format,
        replace_files=args.replace_file,
        keep_anchors=args.keep_anchor,
        full_privacy_audit=args.full_privacy_audit,
        expected_start=args.expected_start,
        expected_end=args.expected_end,
        min_messages=args.min_messages,
        relationship_mode=args.relationship_mode,
        locale=args.locale,
        evidence_limit=args.evidence_limit,
        generate_eval_replies=args.generate_eval_replies,
        publish_redact_names=args.publish_redact_names,
        top_n=args.top_n,
        burst_gap_minutes=args.burst_gap_minutes,
    )
    print(json.dumps({"manifest": str(args.output_dir / "manifest.json"), "artifacts": manifest["artifacts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
