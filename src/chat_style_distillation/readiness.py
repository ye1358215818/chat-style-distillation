from __future__ import annotations

from typing import Any


def _privacy_count(privacy_candidates: dict[str, Any]) -> int:
    return sum(len(items) for items in privacy_candidates.values() if isinstance(items, list))


def compute_readiness(
    *,
    health: dict[str, Any],
    privacy_candidates: dict[str, Any],
    evidence_map: dict[str, Any],
    evaluation_report: dict[str, Any],
) -> dict[str, Any]:
    blocks: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    for issue in health.get("issues", []):
        target = blocks if issue.get("severity") == "high" or issue.get("code") in {"low_volume", "time_gap", "single_speaker"} else warnings
        target.append({"code": f"health:{issue.get('code')}", "detail": issue.get("detail", "")})

    privacy_total = _privacy_count(privacy_candidates)
    if privacy_total:
        blocks.append({"code": "privacy_candidates", "detail": f"{privacy_total} privacy candidate(s) need review."})

    missing = evidence_map.get("coverage", {}).get("missing_core_scenes", [])
    if missing:
        warnings.append({"code": "scene_coverage", "detail": "Missing core scene evidence: " + ", ".join(missing)})

    eval_warnings = evaluation_report.get("warnings", [])
    leakage = evaluation_report.get("dimensions", {}).get("visible_router_leakage", {})
    if leakage and leakage.get("score", 100) < 100:
        blocks.append({"code": "visible_router_leakage", "detail": "Evaluation detected visible router or method language."})
    for warning in eval_warnings:
        if "narrator" in warning.lower() or "mode" in warning.lower() or "router" in warning.lower():
            blocks.append({"code": "evaluation_warning", "detail": warning})
        else:
            warnings.append({"code": "evaluation_warning", "detail": warning})

    if blocks:
        state = "review-needed"
    elif warnings:
        state = "draft"
    else:
        state = "ready-for-private-companion"

    return {
        "version": "0.5.0",
        "state": state,
        "blocks": blocks,
        "warnings": warnings,
        "next_action": "Resolve blocking review items." if blocks else "Review the bundle with a short private companion test.",
    }
