from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pipeline import run_pipeline
from .parsers import parser_choices


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="chat-style-distill", description="Create a private chat style distillation bundle.")
    subcommands = parser.add_subparsers(dest="command", required=True)
    run = subcommands.add_parser("run", help="Run the local distillation pipeline.")
    run.add_argument("input", type=Path)
    run.add_argument("--output-dir", "--out-dir", dest="output_dir", type=Path, required=True)
    run.add_argument("--mode", choices=["companion", "publish"], default="companion")
    run.add_argument("--format", choices=parser_choices(), default="auto")
    run.add_argument("--self-name")
    run.add_argument("--other-name", default="OTHER")
    run.add_argument("--replace-file", action="append", default=[], type=Path)
    run.add_argument("--keep-anchor", action="append", default=[])
    run.add_argument("--full-privacy-audit", action="store_true")
    run.add_argument("--expected-start")
    run.add_argument("--expected-end")
    run.add_argument("--min-messages", type=int, default=50)
    run.add_argument("--relationship-mode", choices=["ex", "lost-contact", "friend", "family", "other"], default="other")
    run.add_argument("--locale", choices=["zh-CN", "en-US"], default="zh-CN")
    run.add_argument("--evidence-limit", type=int, default=5)
    run.add_argument("--generate-eval-replies", action="store_true")
    run.add_argument("--publish-redact-names", action="store_true")
    run.add_argument("--top-n", type=int, default=30)
    run.add_argument("--burst-gap-minutes", type=int, default=3)
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "run":
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
