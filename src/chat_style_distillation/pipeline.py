from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .distillers import (
    render_emotional_memory,
    render_relationship_texture,
    render_scenario_guide,
    render_session_memory,
)
from .evaluate import evaluate
from .health import assess_health
from .metrics import summarize
from .models import ParseOptions
from .parsers import parse_chat
from .privacy import anonymize, audit_candidates, load_anchor_items, parse_replace_file
from .profile import build_style_profile
from .render import render_companion_mode, render_evaluation_report, render_plain_artifact, render_style_card


ARTIFACTS = [
    "sanitized-chat.txt",
    "privacy-candidates.json",
    "analysis-summary.json",
    "style-profile.json",
    "bundle-index.md",
    "style-card.md",
    "export-health.md",
    "emotional-memory-profile.md",
    "relationship-texture.md",
    "scenario-response-guide.md",
    "private-emotional-router.md",
    "memory-companion-mode.md",
    "session-memory.md",
    "evaluation-report.json",
    "evaluation-report.md",
    "manifest.json",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_pipeline(
    input_path: Path,
    output_dir: Path,
    *,
    self_name: str | None = None,
    other_name: str = "OTHER",
    mode: str = "companion",
    fmt: str = "auto",
    replace_files: list[Path] | None = None,
    keep_anchors: list[str] | None = None,
    full_privacy_audit: bool = False,
    top_n: int = 30,
    burst_gap_minutes: int = 3,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    replace_files = replace_files or []
    keep_anchors = keep_anchors or []

    raw_text = input_path.read_text(encoding="utf-8")
    replacements: list[tuple[str, str]] = []
    for replace_file in replace_files:
        replacements.extend(parse_replace_file(replace_file))
    anchors = load_anchor_items(keep_anchors)
    sanitized, redaction_counts = anonymize(raw_text, replacements, self_name=None, other_name=None, mode=mode, keep_anchors=anchors)
    sanitized_path = output_dir / "sanitized-chat.txt"
    sanitized_path.write_text(sanitized, encoding="utf-8", newline="\n")

    privacy_candidates = audit_candidates(sanitized, full=full_privacy_audit)
    (output_dir / "privacy-candidates.json").write_text(json.dumps(privacy_candidates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    parse_result = parse_chat(sanitized_path, ParseOptions(self_name=self_name, other_name=other_name), fmt=fmt)
    if not parse_result.messages:
        raise SystemExit("No messages parsed. Check --format, encoding, or input export shape.")
    analysis = summarize(parse_result.messages, top_n=top_n, burst_gap_minutes=burst_gap_minutes)
    health = assess_health(parse_result.messages)
    analysis["health"] = health
    analysis["input_format"] = parse_result.format
    analysis["parse_warnings"] = parse_result.warnings
    (output_dir / "analysis-summary.json").write_text(json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    profile = build_style_profile(
        analysis,
        privacy_layer="companion_artifact" if mode == "companion" else "published_sample",
        target_speaker=other_name,
    )
    (output_dir / "style-profile.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    (output_dir / "style-card.md").write_text(render_style_card(profile), encoding="utf-8")
    (output_dir / "export-health.md").write_text(
        render_plain_artifact(
            "Export Health",
            f"Message count: {analysis.get('total_messages', 0)}\n\n"
            f"Date range: {analysis.get('first_timestamp')} to {analysis.get('last_timestamp')}\n\n"
            f"Speaker split: {json.dumps({k: v.get('messages', 0) for k, v in analysis.get('speakers', {}).items()}, ensure_ascii=False)}",
        ),
        encoding="utf-8",
    )
    (output_dir / "emotional-memory-profile.md").write_text(render_emotional_memory(profile), encoding="utf-8")
    (output_dir / "relationship-texture.md").write_text(render_relationship_texture(profile), encoding="utf-8")
    (output_dir / "scenario-response-guide.md").write_text(render_scenario_guide(profile), encoding="utf-8")
    (output_dir / "private-emotional-router.md").write_text(
        render_plain_artifact(
            "Private Emotional Router",
            "Privately classify scene, intensity, action risk, reality risk, and response shape. Do not show router labels in companion chat.",
        ),
        encoding="utf-8",
    )
    (output_dir / "memory-companion-mode.md").write_text(render_companion_mode(profile), encoding="utf-8")
    (output_dir / "session-memory.md").write_text(render_session_memory(profile, health), encoding="utf-8")

    eval_report = evaluate((output_dir / "memory-companion-mode.md").read_text(encoding="utf-8"), profile=profile, analysis=analysis)
    (output_dir / "evaluation-report.json").write_text(json.dumps(eval_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "evaluation-report.md").write_text(render_evaluation_report(eval_report), encoding="utf-8")

    manifest = {
        "version": "0.4.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "name": input_path.name,
            "sha256": sha256_file(input_path),
            "first_timestamp": analysis.get("first_timestamp"),
            "last_timestamp": analysis.get("last_timestamp"),
            "total_messages": analysis.get("total_messages"),
            "input_format": parse_result.format,
        },
        "privacy": {
            "mode": mode,
            "redaction_counts": redaction_counts,
            "kept_anchors": sorted(anchors),
            "full_privacy_audit": full_privacy_audit,
        },
        "health": health,
        "artifacts": ARTIFACTS,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "bundle-index.md").write_text(
        "# Companion Bundle Index\n\n"
        "## Readiness\n\n"
        f"- State: {health.get('readiness')}\n"
        f"- Private companion use: {'reasonable after review' if health.get('readiness') != 'review-needed' else 'review needed before activation'}\n"
        "- Publishable: no\n\n"
        "## Input Summary\n\n"
        f"- Privacy mode: {mode}\n"
        f"- Date range: {analysis.get('first_timestamp')} to {analysis.get('last_timestamp')}\n"
        f"- Message count: {analysis.get('total_messages', 0)}\n\n"
        "## Known Gaps\n\n"
        + ("\n".join(f"- {issue.get('code')}: {issue.get('detail')}" for issue in health.get("issues", [])) or "- No deterministic health gaps detected.")
        + "\n\n"
        "## Next Action\n\n"
        + ("- Review the health gaps, then inspect the style and scenario artifacts.\n\n" if health.get("issues") else "- Read `memory-companion-mode.md`, then test a short private companion exchange.\n\n")
        + "## Artifact Map\n\n"
        + "\n".join(f"- `{artifact}`" for artifact in ARTIFACTS)
        + "\n",
        encoding="utf-8",
    )
    return manifest
