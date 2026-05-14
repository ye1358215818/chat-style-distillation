#!/usr/bin/env python3
"""Analyze chat export health and real-chat style signals.

The script is local-only and dependency-free. It gives an agent a first pass
over a chat export without printing the private conversation.
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

SCENE_KEYWORDS: dict[str, list[str]] = {
    "daily": ["早", "晚安", "吃饭", "睡", "起床", "上班", "下班", "到家", "干嘛"],
    "missing": ["想你", "想我", "抱抱", "见你", "梦到", "舍不得"],
    "comfort": ["别哭", "别硬撑", "我在", "抱抱", "没事", "慢慢说", "听着"],
    "conflict": ["算了", "随便", "你每次", "生气", "吵", "烦", "不想说"],
    "apology": ["对不起", "抱歉", "错了", "原谅", "不是故意"],
    "jealousy": ["吃醋", "谁啊", "别人", "前任", "男的", "女的"],
    "coldness": ["嗯", "哦", "行", "知道了", "不用", "没事"],
    "repair": ["好啦", "不气", "回来", "和好", "别闹", "乖"],
}


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


def percentile(values: list[int | float], pct: float) -> float:
    if not values:
        return 0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    idx = (len(ordered) - 1) * pct
    lo = int(idx)
    hi = min(lo + 1, len(ordered) - 1)
    frac = idx - lo
    return round(ordered[lo] * (1 - frac) + ordered[hi] * frac, 2)


def classify_scene(content: str) -> str:
    text = content.strip()
    scores = {
        scene: sum(1 for keyword in keywords if keyword in text)
        for scene, keywords in SCENE_KEYWORDS.items()
    }
    scene, score = max(scores.items(), key=lambda item: item[1])
    return scene if score else "unspecified"


def message_ending(content: str) -> str:
    text = content.strip()
    if not text:
        return ""
    if text.endswith(("...", "…")):
        return "ellipsis"
    last = text[-1]
    if last in "。！？!?~～":
        return last
    return "plain"


def burst_stats(messages: list[dict[str, Any]], max_gap_minutes: int) -> dict[str, Any]:
    bursts: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []

    for message in messages:
        if not current:
            current = [message]
            continue
        gap = (message["timestamp"] - current[-1]["timestamp"]).total_seconds() / 60
        if message["speaker"] == current[-1]["speaker"] and gap <= max_gap_minutes:
            current.append(message)
        else:
            if len(current) > 1:
                bursts.append({"speaker": current[0]["speaker"], "size": len(current)})
            current = [message]
    if len(current) > 1:
        bursts.append({"speaker": current[0]["speaker"], "size": len(current)})

    by_speaker: dict[str, list[int]] = defaultdict(list)
    for burst in bursts:
        by_speaker[burst["speaker"]].append(burst["size"])

    return {
        speaker: {
            "burst_count": len(sizes),
            "avg_burst_size": round(sum(sizes) / len(sizes), 2) if sizes else 0,
            "max_burst_size": max(sizes) if sizes else 0,
        }
        for speaker, sizes in by_speaker.items()
    }


def response_latency(messages: list[dict[str, Any]]) -> dict[str, Any]:
    latencies: dict[str, list[float]] = defaultdict(list)
    previous: dict[str, Any] | None = None
    for message in messages:
        if previous and previous["speaker"] != message["speaker"]:
            delta = (message["timestamp"] - previous["timestamp"]).total_seconds() / 60
            if 0 <= delta <= 60 * 24:
                latencies[message["speaker"]].append(round(delta, 2))
        previous = message

    return {
        speaker: {
            "count": len(values),
            "median_minutes": percentile(values, 0.5),
            "p90_minutes": percentile(values, 0.9),
        }
        for speaker, values in latencies.items()
    }


def summarize(messages: list[dict[str, Any]], top_n: int, burst_gap_minutes: int) -> dict[str, Any]:
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
        scenes = Counter(classify_scene(m["content"]) for m in text_items)
        endings = Counter(message_ending(m["content"]) for m in text_items if m["content"].strip())
        multi_line = sum(1 for m in text_items if "\n" in m["content"])

        speakers[speaker] = {
            "messages": len(items),
            "text_messages": len(text_items),
            "media_or_system_messages": len(items) - len(text_items),
            "avg_text_length": round(sum(lengths) / len(lengths), 2) if lengths else 0,
            "median_text_length": percentile(lengths, 0.5),
            "p10_text_length": percentile(lengths, 0.1),
            "p90_text_length": percentile(lengths, 0.9),
            "multi_line_messages": multi_line,
            "top_short_phrases": phrases.most_common(top_n),
            "marker_counts": marker_counts,
            "scene_counts": scenes.most_common(),
            "ending_counts": endings.most_common(),
            "top_hours": Counter(m["timestamp"].hour for m in items).most_common(8),
        }

    return {
        "total_messages": len(messages),
        "first_timestamp": messages[0]["timestamp"].strftime("%Y-%m-%d %H:%M") if messages else None,
        "last_timestamp": messages[-1]["timestamp"].strftime("%Y-%m-%d %H:%M") if messages else None,
        "speakers": speakers,
        "burst_stats": burst_stats(messages, burst_gap_minutes),
        "response_latency": response_latency(messages),
        "scene_keywords": SCENE_KEYWORDS,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze chat export health and style signals.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--self-name", help="Display name used for the user's own messages in the export.")
    parser.add_argument("--other-name", default="OTHER", help="Fallback label for messages without a speaker prefix.")
    parser.add_argument("--top-n", type=int, default=30)
    parser.add_argument("--burst-gap-minutes", type=int, default=3)
    parser.add_argument("--output", type=Path, help="Write JSON summary to this path. Defaults to stdout.")
    args = parser.parse_args()

    messages = read_messages(args.input, args.self_name, args.other_name)
    summary = summarize(messages, args.top_n, args.burst_gap_minutes)
    payload = json.dumps(summary, ensure_ascii=False, indent=2)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print(f"Wrote: {args.output}")
    else:
        print(payload)


if __name__ == "__main__":
    main()
