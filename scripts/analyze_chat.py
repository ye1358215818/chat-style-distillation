#!/usr/bin/env python3
"""Analyze chat export health and style signals.

This script is local-only and dependency-free. It gives an agent a fast first
pass over an exported chat without printing the full private conversation.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


TIMESTAMP_RE = re.compile(r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\]\s*(.*)$")

MEDIA_PREFIXES = (
    "[图片]",
    "[视频]",
    "[语音]",
    "[链接]",
    "[通话]",
    "[位置]",
    "[文件]",
    "[系统]",
)

DEFAULT_MARKERS = [
    "哈哈",
    "笑死",
    "害",
    "唉",
    "哼",
    "呜",
    "好哦",
    "嗯嗯",
    "哦哦",
    "无语",
    "离谱",
    "想你",
    "晚安",
    "早",
    "宝",
    "亲亲",
    "？",
    "！",
    "...",
    "…",
]


def read_messages(path: Path, self_name: str | None, other_name: str) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        match = TIMESTAMP_RE.match(raw)
        if match:
            if current:
                messages.append(current)
            ts = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M")
            rest = match.group(2)
            speaker = other_name
            content = rest.strip()
            if self_name and rest.startswith(f"{self_name}:"):
                speaker = "SELF"
                content = rest.split(":", 1)[1].strip()
            elif ":" in rest:
                maybe_speaker, maybe_content = rest.split(":", 1)
                if 0 < len(maybe_speaker) <= 32:
                    speaker = maybe_speaker.strip()
                    content = maybe_content.strip()
            current = {"timestamp": ts, "speaker": speaker, "content": content}
        elif current and raw:
            current["content"] += "\n" + raw

    if current:
        messages.append(current)
    return messages


def is_media_or_system(content: str) -> bool:
    text = content.strip()
    if text.startswith("<?xml") or "<msg>" in text:
        return True
    if any(text.startswith(prefix) for prefix in MEDIA_PREFIXES):
        return True
    return bool(re.fullmatch(r"\[[^\]]+\](?:\s*local_id=\d+)?", text))


def summarize(messages: list[dict[str, Any]], top_n: int) -> dict[str, Any]:
    by_speaker: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for message in messages:
        by_speaker[message["speaker"]].append(message)

    speakers: dict[str, Any] = {}
    for speaker, items in by_speaker.items():
        text_items = [m for m in items if not is_media_or_system(m["content"])]
        lengths = [len(m["content"].replace("\n", "")) for m in text_items]
        phrases = Counter(
            m["content"].strip()
            for m in text_items
            if 1 <= len(m["content"].strip()) <= 24
        )
        marker_counts = {
            marker: sum(m["content"].count(marker) for m in text_items)
            for marker in DEFAULT_MARKERS
        }
        marker_counts = {k: v for k, v in marker_counts.items() if v}

        speakers[speaker] = {
            "messages": len(items),
            "text_messages": len(text_items),
            "media_or_system_messages": len(items) - len(text_items),
            "avg_text_length": round(sum(lengths) / len(lengths), 2) if lengths else 0,
            "median_text_length": statistics.median(lengths) if lengths else 0,
            "top_short_phrases": phrases.most_common(top_n),
            "marker_counts": marker_counts,
            "top_hours": Counter(m["timestamp"].hour for m in items).most_common(8),
        }

    return {
        "total_messages": len(messages),
        "first_timestamp": messages[0]["timestamp"].strftime("%Y-%m-%d %H:%M") if messages else None,
        "last_timestamp": messages[-1]["timestamp"].strftime("%Y-%m-%d %H:%M") if messages else None,
        "speakers": speakers,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze chat export health and style signals.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--self-name", help="Display name used for the user's own messages in the export.")
    parser.add_argument("--other-name", default="OTHER", help="Fallback label for messages without a speaker prefix.")
    parser.add_argument("--top-n", type=int, default=30)
    parser.add_argument("--output", type=Path, help="Write JSON summary to this path. Defaults to stdout.")
    args = parser.parse_args()

    messages = read_messages(args.input, args.self_name, args.other_name)
    summary = summarize(messages, args.top_n)
    payload = json.dumps(summary, ensure_ascii=False, indent=2)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print(f"Wrote: {args.output}")
    else:
        print(payload)


if __name__ == "__main__":
    main()
