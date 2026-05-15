from __future__ import annotations

import json
from typing import Any


def render_style_card(profile: dict[str, Any]) -> str:
    voice = profile.get("voice", {})
    data = profile.get("data_health", {})
    phrases = ", ".join(voice.get("phrases", [])) or "Review needed"
    return (
        "# Memory Companion Style Card\n\n"
        "## Data Health\n\n"
        f"- Message count: {data.get('message_count', 0)}\n"
        f"- Date range: {data.get('first_timestamp')} to {data.get('last_timestamp')}\n"
        f"- Privacy layer: {profile.get('privacy_layer')}\n\n"
        "## The Voice At A Glance\n\n"
        f"{voice.get('summary', '')}\n\n"
        "## Small Words And Repeated Phrases\n\n"
        f"{phrases}\n"
    )


def render_companion_mode(profile: dict[str, Any]) -> str:
    companion = profile.get("companion_mode", {})
    contract = "\n".join(f"- {item}" for item in companion.get("reply_contract", []))
    return (
        "# Companion Mode\n\n"
        "When activated, answer directly in the distilled voice. No narrator label, method explanation, router label, or opening preface.\n\n"
        "## Reply Contract\n\n"
        f"{contract}\n\n"
        "## Private Emotional Router\n\n"
        "Privately classify scene, intensity, action risk, reality risk, and response shape. Never show this classification in chat.\n"
    )


def render_plain_artifact(title: str, body: str = "Review and complete from representative source evidence.") -> str:
    return f"# {title}\n\n{body}\n"


def render_evaluation_report(report: dict[str, Any]) -> str:
    return "# Evaluation Report\n\n```json\n" + json.dumps(report, ensure_ascii=False, indent=2) + "\n```\n"
