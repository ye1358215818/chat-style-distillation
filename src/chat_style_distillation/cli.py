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
            top_n=args.top_n,
            burst_gap_minutes=args.burst_gap_minutes,
        )
        print(json.dumps({"manifest": str(args.output_dir / "manifest.json"), "artifacts": manifest["artifacts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
