#!/usr/bin/env python3
"""Build a structured style profile from analysis JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from chat_style_distillation.profile import build_style_profile  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Build style-profile.json from analysis-summary.json.")
    parser.add_argument("analysis", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--privacy-layer",
        default="companion_artifact",
        choices=["local_source", "companion_artifact", "published_sample"],
    )
    parser.add_argument("--target-speaker", default="OTHER")
    args = parser.parse_args()

    analysis = json.loads(args.analysis.read_text(encoding="utf-8"))
    profile = build_style_profile(analysis, privacy_layer=args.privacy_layer, target_speaker=args.target_speaker)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()
