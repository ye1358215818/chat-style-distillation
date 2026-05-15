from __future__ import annotations

import hashlib
from collections import defaultdict
from typing import Any

from .models import Message
from .scene import classify_message


CORE_SCENES = ["daily", "comfort", "missing"]


def evidence_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def paraphrase_message(message: Message) -> str:
    length = len(message.content.strip())
    if length <= 4:
        shape = "very short"
    elif length <= 16:
        shape = "short"
    elif length <= 60:
        shape = "medium"
    else:
        shape = "long"
    return f"{message.speaker} used a {shape} reply with {length} character(s)."


def summarize_signals(signals: list[str]) -> dict[str, Any]:
    categories = sorted({signal.split(":", 1)[0] for signal in signals if signal})
    return {"categories": categories, "count": len(signals)}


def build_evidence_map(messages: list[Message], *, target_speaker: str = "OTHER", limit: int = 5) -> dict[str, Any]:
    scenes: dict[str, dict[str, Any]] = {}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for index, message in enumerate(messages):
        if message.speaker not in {target_speaker, "OTHER"}:
            continue
        match = classify_message(message, messages[max(0, index - 3) : index])
        scene = match.primary
        if len(grouped[scene]) >= limit:
            continue
        context = messages[max(0, index - 2) : min(len(messages), index + 2)]
        context_fingerprint = "\n".join(f"{item.speaker}:{item.content}" for item in context)
        grouped[scene].append(
            {
                "hash": evidence_hash(context_fingerprint),
                "message_hash": evidence_hash(message.content),
                "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M") if message.timestamp else None,
                "speaker": message.speaker,
                "paraphrase": paraphrase_message(message),
                "signals": summarize_signals(match.signals),
                "confidence": match.confidence,
            }
        )

    for scene, items in grouped.items():
        timestamps = [item["timestamp"] for item in items if item.get("timestamp")]
        scenes[scene] = {
            "count": len(items),
            "first_timestamp": min(timestamps) if timestamps else None,
            "last_timestamp": max(timestamps) if timestamps else None,
            "items": items,
        }
    covered = sorted(scene for scene in scenes if scene in CORE_SCENES)
    missing = [scene for scene in CORE_SCENES if scene not in scenes]
    return {
        "version": "0.5.0",
        "target_speaker": target_speaker,
        "coverage": {
            "core_scenes": CORE_SCENES,
            "covered_scenes": covered,
            "missing_core_scenes": missing,
        },
        "scenes": scenes,
    }
