from __future__ import annotations

import json
from typing import Any


def render_style_card(profile: dict[str, Any]) -> str:
    voice = profile.get("voice", {})
    data = profile.get("data_health", {})
    phrases = ", ".join(voice.get("phrases", [])) or "Review needed"
    traits = "\n".join(f"- {item}" for item in profile.get("observed_traits", []))
    reply_shapes = "\n".join(f"- {name}: {text}" for name, text in profile.get("reply_shapes", {}).items())
    return (
        "# Memory Companion Style Card\n\n"
        "## Data Health\n\n"
        f"- Message count: {data.get('message_count', 0)}\n"
        f"- Date range: {data.get('first_timestamp')} to {data.get('last_timestamp')}\n"
        f"- Privacy layer: {profile.get('privacy_layer')}\n\n"
        "## The Voice At A Glance\n\n"
        f"{voice.get('summary', '')}\n\n"
        "## Observed Traits\n\n"
        f"{traits}\n\n"
        "## Small Words And Repeated Phrases\n\n"
        f"{phrases}\n\n"
        "## Reply Shapes\n\n"
        f"{reply_shapes}\n"
    )


def render_companion_mode(profile: dict[str, Any]) -> str:
    companion = profile.get("companion_mode", {})
    contract = "\n".join(f"- {item}" for item in companion.get("reply_contract", []))
    reply_shapes = "\n".join(f"- {name}: {text}" for name, text in profile.get("reply_shapes", {}).items())
    high_emotion = "\n".join(f"- {name}: {text}" for name, text in profile.get("high_emotion_handling", {}).items())
    return (
        "# Companion Mode\n\n"
        "When activated, answer directly in the distilled voice. No narrator label, method explanation, router label, or opening preface.\n\n"
        "## Reply Contract\n\n"
        f"{contract}\n\n"
        "## Length And Shape\n\n"
        f"{reply_shapes}\n\n"
        "## Private Emotional Router\n\n"
        "Privately classify scene, intensity, action risk, reality risk, and response shape. Never show this classification in chat.\n\n"
        "## High Emotion Handling\n\n"
        f"{high_emotion}\n"
    )


def render_plain_artifact(title: str, body: str = "Evidence is summarized from deterministic source signals.") -> str:
    return f"# {title}\n\n{body}\n"


def render_evaluation_report(report: dict[str, Any]) -> str:
    dimensions = report.get("dimensions", {})
    lines = ["# Evaluation Report", "", f"Overall score: {report.get('overall_score', 0)}", "", "## Dimension Scores", ""]
    for name, value in dimensions.items():
        lines.append(f"- {name}: {value.get('score', 0)}")
    if report.get("warnings"):
        lines.extend(["", "## Repair Suggestions", ""])
        lines.extend(f"- {warning}" for warning in report["warnings"])
    lines.extend(["", "## Raw Report", "", "```json", json.dumps(report, ensure_ascii=False, indent=2), "```", ""])
    return "\n".join(lines)
