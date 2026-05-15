from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import Message, ParseOptions, ParseResult


TIMESTAMP_RE = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})(?::\d{2})?\]\s*")


def normalize_speaker(speaker: str, options: ParseOptions) -> str:
    return "SELF" if options.self_name and speaker == options.self_name else speaker


def split_timestamp_records(text: str) -> list[tuple[str, str, int]]:
    records: list[tuple[str, str, int]] = []
    matches = list(TIMESTAMP_RE.finditer(text))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end() : end]
        line = text.count("\n", 0, match.start()) + 1
        records.append((match.group(1), body, line))
    return records


def parse_timestamp_text(path: Path, options: ParseOptions) -> ParseResult:
    text = path.read_text(encoding=options.encoding)
    messages: list[Message] = []
    current: dict[str, Any] | None = None

    for ts_text, body, line_no in split_timestamp_records(text):
        if current:
            messages.append(
                Message(
                    timestamp=current["timestamp"],
                    speaker=current["speaker"],
                    content=current["content"].strip(),
                    raw=current["raw"].strip(),
                    source_line=current["source_line"],
                )
            )

        timestamp = datetime.strptime(ts_text, "%Y-%m-%d %H:%M")
        raw_body = body.strip()
        first_line = raw_body.splitlines()[0] if raw_body else ""
        speaker = options.other_name
        content = raw_body
        if options.self_name and first_line.startswith(f"{options.self_name}:"):
            speaker = "SELF"
            content = raw_body.split(":", 1)[1].strip()
        elif ":" in first_line:
            maybe_speaker, maybe_content = raw_body.split(":", 1)
            if 0 < len(maybe_speaker.strip()) <= 32:
                speaker = normalize_speaker(maybe_speaker.strip(), options)
                content = maybe_content.strip()

        current = {
            "timestamp": timestamp,
            "speaker": speaker,
            "content": content,
            "raw": raw_body,
            "source_line": line_no,
        }

    if current:
        messages.append(
            Message(
                timestamp=current["timestamp"],
                speaker=current["speaker"],
                content=current["content"].strip(),
                raw=current["raw"].strip(),
                source_line=current["source_line"],
            )
        )

    warnings: list[str] = []
    if text and not messages:
        warnings.append("No timestamped records parsed.")
    return ParseResult(messages=messages, format="timestamp-text", warnings=warnings)


def _json_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("messages", "data", "records", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def parse_json(path: Path, options: ParseOptions) -> ParseResult:
    payload = json.loads(path.read_text(encoding=options.encoding))
    messages: list[Message] = []
    warnings: list[str] = []
    for idx, record in enumerate(_json_records(payload), start=1):
        ts_value = record.get("timestamp") or record.get("time") or record.get("createTime")
        timestamp: datetime | None = None
        if isinstance(ts_value, str):
            for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
                try:
                    timestamp = datetime.strptime(ts_value, fmt)
                    break
                except ValueError:
                    continue
        speaker_value = str(record.get("speaker") or record.get("sender") or record.get("from") or options.other_name)
        speaker = normalize_speaker(speaker_value, options)
        content = str(record.get("content") or record.get("text") or record.get("message") or "")
        messages.append(
            Message(timestamp=timestamp, speaker=speaker, content=content, raw=json.dumps(record, ensure_ascii=False), source_line=idx)
        )
    if not messages:
        warnings.append("No JSON chat records parsed.")
    return ParseResult(messages=messages, format="json", warnings=warnings)


def parse_chat(path: Path, options: ParseOptions | None = None, fmt: str = "auto") -> ParseResult:
    options = options or ParseOptions()
    if fmt == "json" or (fmt == "auto" and path.suffix.lower() == ".json"):
        return parse_json(path, options)
    return parse_timestamp_text(path, options)
