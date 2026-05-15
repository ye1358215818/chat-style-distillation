from __future__ import annotations

from collections import Counter
from datetime import datetime, date
from typing import Any

from .metrics import is_media_or_system
from .models import Message


def _month_key(timestamp: datetime) -> str:
    return timestamp.strftime("%Y-%m")


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def assess_health(
    messages: list[Message],
    *,
    min_messages: int = 50,
    expected_start: str | None = None,
    expected_end: str | None = None,
    relationship_mode: str = "other",
) -> dict[str, Any]:
    timestamped = [message for message in messages if message.timestamp]
    issues: list[dict[str, Any]] = []
    total = len(messages)

    if total < min_messages:
        issues.append({"code": "low_volume", "severity": "medium", "detail": f"Only {total} parsed message(s)."})

    previous: Message | None = None
    max_gap_days = 0.0
    for message in timestamped:
        if previous and previous.timestamp and message.timestamp:
            delta_days = (message.timestamp - previous.timestamp).total_seconds() / 86400
            if delta_days < 0:
                issues.append({"code": "out_of_order", "severity": "high", "detail": "Messages are not strictly chronological."})
            max_gap_days = max(max_gap_days, delta_days)
        previous = message
    if max_gap_days >= 30:
        issues.append({"code": "time_gap", "severity": "medium", "detail": f"Largest timestamp gap is {round(max_gap_days, 1)} day(s)."})

    seen: set[tuple[str | None, str, str]] = set()
    duplicate_count = 0
    for message in messages:
        key = (
            message.timestamp.strftime("%Y-%m-%d %H:%M:%S") if message.timestamp else None,
            message.speaker,
            message.content.strip(),
        )
        if key in seen:
            duplicate_count += 1
        seen.add(key)
    if duplicate_count:
        issues.append({"code": "duplicate_message", "severity": "medium", "detail": f"{duplicate_count} duplicate-looking message(s)."})

    speaker_counts = Counter(message.speaker for message in messages)
    if len(speaker_counts) >= 2:
        counts = list(speaker_counts.values())
        low = min(counts)
        high = max(counts)
        if low and high / low >= 3:
            issues.append({"code": "speaker_imbalance", "severity": "medium", "detail": f"Speaker split is imbalanced: {dict(speaker_counts)}."})
    elif total:
        issues.append({"code": "single_speaker", "severity": "medium", "detail": "Only one speaker was parsed."})

    media_count = sum(1 for message in messages if message.message_type != "text" or is_media_or_system(message.content))
    media_ratio = round(media_count / total, 3) if total else 0.0
    if total and media_ratio >= 0.3:
        issues.append({"code": "high_media_ratio", "severity": "medium", "detail": f"Media/system ratio is {media_ratio}."})

    start = _parse_date(expected_start)
    end = _parse_date(expected_end)
    if start and timestamped and timestamped[0].timestamp and timestamped[0].timestamp.date() > start:
        issues.append({"code": "expected_start_gap", "severity": "medium", "detail": f"First parsed message is after expected start {expected_start}."})
    if end and timestamped and timestamped[-1].timestamp and timestamped[-1].timestamp.date() < end:
        issues.append({"code": "expected_end_gap", "severity": "medium", "detail": f"Last parsed message is before expected end {expected_end}."})

    month_counts = Counter(_month_key(message.timestamp) for message in timestamped if message.timestamp)
    severe = any(issue["severity"] == "high" for issue in issues)
    if not messages or severe or any(issue["code"] in {"low_volume", "time_gap", "single_speaker"} for issue in issues):
        readiness = "review-needed"
    elif issues:
        readiness = "draft"
    else:
        readiness = "ready-for-private-companion"

    return {
        "readiness": readiness,
        "message_count": total,
        "timestamped_count": len(timestamped),
        "first_timestamp": timestamped[0].timestamp.strftime("%Y-%m-%d %H:%M") if timestamped else None,
        "last_timestamp": timestamped[-1].timestamp.strftime("%Y-%m-%d %H:%M") if timestamped else None,
        "speaker_counts": dict(speaker_counts),
        "media_or_system_ratio": media_ratio,
        "month_counts": dict(sorted(month_counts.items())),
        "largest_gap_days": round(max_gap_days, 2),
        "issues": issues,
        "config": {
            "min_messages": min_messages,
            "expected_start": expected_start,
            "expected_end": expected_end,
            "relationship_mode": relationship_mode,
        },
    }
