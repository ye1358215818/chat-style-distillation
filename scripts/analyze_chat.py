#!/usr/bin/env python3
"""Analyze chat export health and real-chat style signals."""

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

from chat_style_distillation.metrics import (  # noqa: E402
    DEFAULT_MARKERS,
    MEDIA_PREFIXES,
    burst_stats as _burst_stats,
    is_media_or_system,
    message_ending,
    percentile,
    response_latency as _response_latency,
    summarize as _summarize_messages,
)
from chat_style_distillation.models import Message, ParseOptions  # noqa: E402
from chat_style_distillation.parsers import TIMESTAMP_RE, parse_chat  # noqa: E402
from chat_style_distillation.scene import SCENE_KEYWORDS, classify_message  # noqa: E402


def _message_dict(message: Message) -> dict[str, Any]:
    return {
        "timestamp": message.timestamp,
        "speaker": message.speaker,
        "content": message.content,
        "raw": message.raw,
        "source_line": message.source_line,
        "message_type": message.message_type,
    }


def _message_from_dict(message: dict[str, Any]) -> Message:
    return Message(
        timestamp=message.get("timestamp"),
        speaker=message.get("speaker", "OTHER"),
        content=message.get("content", ""),
        raw=message.get("raw", message.get("content", "")),
        source_line=message.get("source_line"),
        message_type=message.get("message_type", "text"),
    )


def read_messages(path: Path, self_name: str | None, other_name: str) -> list[dict[str, Any]]:
    result = parse_chat(path, ParseOptions(self_name=self_name, other_name=other_name))
    return [_message_dict(message) for message in result.messages]


def classify_scene(content: str) -> str:
    return classify_message(Message(timestamp=None, speaker="OTHER", content=content, raw=content)).primary


def burst_stats(messages: list[dict[str, Any]], max_gap_minutes: int) -> dict[str, Any]:
    return _burst_stats([_message_from_dict(message) for message in messages], max_gap_minutes)


def response_latency(messages: list[dict[str, Any]]) -> dict[str, Any]:
    return _response_latency([_message_from_dict(message) for message in messages])


def summarize(messages: list[dict[str, Any]], top_n: int, burst_gap_minutes: int) -> dict[str, Any]:
    return _summarize_messages([_message_from_dict(message) for message in messages], top_n, burst_gap_minutes)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze chat export health and style signals.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--self-name", help="Display name used for the user's own messages in the export.")
    parser.add_argument("--other-name", default="OTHER", help="Fallback label for messages without a speaker prefix.")
    parser.add_argument("--top-n", type=int, default=30)
    parser.add_argument("--burst-gap-minutes", type=int, default=3)
    parser.add_argument("--format", default="auto", choices=["auto", "timestamp-text", "wechat-txt", "json"])
    parser.add_argument("--output", type=Path, help="Write JSON summary to this path. Defaults to stdout.")
    args = parser.parse_args()

    result = parse_chat(args.input, ParseOptions(self_name=args.self_name, other_name=args.other_name), fmt=args.format)
    summary = _summarize_messages(result.messages, args.top_n, args.burst_gap_minutes)
    if result.warnings:
        summary["parse_warnings"] = result.warnings
    summary["input_format"] = result.format
    payload = json.dumps(summary, ensure_ascii=False, indent=2)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print(f"Wrote: {args.output}")
    else:
        print(payload)


if __name__ == "__main__":
    main()
