from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any

from .models import Message
from .scene import SCENE_KEYWORDS, classify_message


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


def burst_stats(messages: list[Message], max_gap_minutes: int) -> dict[str, Any]:
    bursts: list[dict[str, Any]] = []
    current: list[Message] = []
    for message in messages:
        if not message.timestamp:
            continue
        if not current:
            current = [message]
            continue
        prev = current[-1]
        if not prev.timestamp:
            current = [message]
            continue
        gap = (message.timestamp - prev.timestamp).total_seconds() / 60
        if message.speaker == prev.speaker and gap <= max_gap_minutes:
            current.append(message)
        else:
            if len(current) > 1:
                bursts.append({"speaker": current[0].speaker, "size": len(current)})
            current = [message]
    if len(current) > 1:
        bursts.append({"speaker": current[0].speaker, "size": len(current)})

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


def response_latency(messages: list[Message]) -> dict[str, Any]:
    latencies: dict[str, list[float]] = defaultdict(list)
    previous: Message | None = None
    for message in messages:
        if previous and previous.timestamp and message.timestamp and previous.speaker != message.speaker:
            delta = (message.timestamp - previous.timestamp).total_seconds() / 60
            if 0 <= delta <= 60 * 24:
                latencies[message.speaker].append(round(delta, 2))
        previous = message
    return {
        speaker: {
            "count": len(values),
            "median_minutes": percentile(values, 0.5),
            "p90_minutes": percentile(values, 0.9),
        }
        for speaker, values in latencies.items()
    }


def summarize(messages: list[Message], top_n: int = 30, burst_gap_minutes: int = 3) -> dict[str, Any]:
    by_speaker: dict[str, list[Message]] = defaultdict(list)
    for message in messages:
        by_speaker[message.speaker].append(message)
    message_positions = {id(message): index for index, message in enumerate(messages)}

    speakers: dict[str, Any] = {}
    for speaker, items in by_speaker.items():
        text_items = [m for m in items if not is_media_or_system(m.content)]
        lengths = [len(m.content.replace("\n", "")) for m in text_items]
        phrases = Counter(m.content.strip() for m in text_items if 1 <= len(m.content.strip()) <= 24)
        marker_counts = {marker: sum(m.content.count(marker) for m in text_items) for marker in DEFAULT_MARKERS}
        marker_counts = {k: v for k, v in marker_counts.items() if v}
        scenes = Counter(classify_message(m, messages[: message_positions[id(m)]]).primary for m in text_items)
        endings = Counter(message_ending(m.content) for m in text_items if m.content.strip())
        multi_line = sum(1 for m in text_items if "\n" in m.content)
        timestamped = [m for m in items if m.timestamp]
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
            "top_hours": Counter(m.timestamp.hour for m in timestamped if m.timestamp).most_common(8),
        }

    timestamped_all = [m for m in messages if m.timestamp]
    return {
        "total_messages": len(messages),
        "first_timestamp": timestamped_all[0].timestamp.strftime("%Y-%m-%d %H:%M") if timestamped_all else None,
        "last_timestamp": timestamped_all[-1].timestamp.strftime("%Y-%m-%d %H:%M") if timestamped_all else None,
        "speakers": speakers,
        "burst_stats": burst_stats(messages, burst_gap_minutes),
        "response_latency": response_latency(messages),
        "scene_keywords": SCENE_KEYWORDS,
    }
