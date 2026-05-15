from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Message:
    timestamp: datetime | None
    speaker: str
    content: str
    raw: str
    source_line: int | None = None
    message_type: str = "text"


@dataclass(frozen=True)
class ParseOptions:
    self_name: str | None = None
    other_name: str = "OTHER"
    encoding: str = "utf-8"
    strict: bool = False


@dataclass(frozen=True)
class ParseResult:
    messages: list[Message]
    format: str
    warnings: list[str] = field(default_factory=list)
    speaker_aliases: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SceneMatch:
    primary: str
    scores: dict[str, float]
    signals: list[str]
    confidence: float


def message_to_dict(message: Message) -> dict[str, Any]:
    return {
        "timestamp": message.timestamp,
        "speaker": message.speaker,
        "content": message.content,
        "raw": message.raw,
        "source_line": message.source_line,
        "message_type": message.message_type,
    }
