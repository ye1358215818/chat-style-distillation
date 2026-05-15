from __future__ import annotations

import re
from typing import Any


META_PATTERNS = [
    r"\[.*?mode.*?\]",
    r"based on (the )?(chat|logs|records)",
    r"as an ai",
    r"我切到",
    r"根据聊天记录",
    r"作为一个",
    r"模式",
]

PLACEHOLDER_PATTERNS = [
    r"PERSON_[A-Z]",
    r"LOCATION_[A-Z]",
    r"\[(?:PHONE|EMAIL|ID_CARD|WXID|URL|WINDOWS_PATH)\]",
]

THERAPY_SPEAK = ["情绪价值", "创伤", "依恋", "边界感", "课题分离", "原生家庭", "认知"]
GENERIC_ROMANCE = ["永远爱你", "命中注定", "你是我的全世界"]


def count_patterns(text: str, patterns: list[str]) -> int:
    return sum(len(re.findall(pattern, text, flags=re.IGNORECASE)) for pattern in patterns)


def _dimension(score: int, hits: int, label: str) -> dict[str, Any]:
    return {"score": max(score, 0), "hits": hits, "label": label}


def evaluate(text: str, *, profile: dict[str, Any] | None = None, analysis: dict[str, Any] | None = None) -> dict[str, Any]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    lengths = [len(line) for line in lines]
    meta_hits = count_patterns(text, META_PATTERNS)
    placeholder_hits = count_patterns(text, PLACEHOLDER_PATTERNS)
    therapy_hits = sum(text.count(word) for word in THERAPY_SPEAK)
    romance_hits = sum(text.count(word) for word in GENERIC_ROMANCE)

    warnings: list[str] = []
    if meta_hits:
        warnings.append("Contains narrator/method/mode language that can break immersion.")
    if placeholder_hits:
        warnings.append("Contains sterile placeholders; consider natural memory wording for private companion use.")
    if therapy_hits:
        warnings.append("Contains therapy-speak; verify the user asked for analysis rather than immersive chat.")
    if romance_hits:
        warnings.append("Contains generic romance wording unsupported by source evidence.")
    if lines and max(lengths) > 240:
        warnings.append("Contains very long chat lines; verify this matches the source person's real style.")

    dimensions = {
        "immersion": _dimension(100 - min(meta_hits * 25, 75), meta_hits, "no visible mode or narrator language"),
        "privacy": _dimension(100 - min(placeholder_hits * 15, 60), placeholder_hits, "no sterile placeholders or hard identifiers"),
        "therapy_speak": _dimension(100 - min(therapy_hits * 10, 60), therapy_hits, "chat-native rather than clinical"),
        "generic_romance": _dimension(100 - min(romance_hits * 10, 50), romance_hits, "source-specific rather than generic romance"),
        "length_fit": {
            "score": 80 if not lines or max(lengths) <= 240 else 60,
            "avg_line_length": round(sum(lengths) / len(lengths), 2) if lengths else 0,
            "max_line_length": max(lengths) if lengths else 0,
        },
        "scene_fit": {"score": 70, "label": "requires human review unless prompt/response scene labels are supplied"},
        "emotional_usefulness": {"score": 70, "label": "requires high-emotion test transcript for strong signal"},
        "safe_in_voice": {"score": 80 if not meta_hits else 50, "label": "no visible disclaimers; risky-action handling needs human review"},
    }
    overall = round(sum(d["score"] for d in dimensions.values()) / len(dimensions), 2)
    return {
        "overall_score": overall,
        "score": overall,
        "line_count": len(lines),
        "avg_line_length": dimensions["length_fit"]["avg_line_length"],
        "max_line_length": dimensions["length_fit"]["max_line_length"],
        "meta_hits": meta_hits,
        "placeholder_hits": placeholder_hits,
        "therapy_speak_hits": therapy_hits,
        "dimensions": dimensions,
        "warnings": warnings,
        "suggestions": warnings[:],
    }
