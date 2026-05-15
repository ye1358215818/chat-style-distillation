from __future__ import annotations

import json
import re
import csv
from html.parser import HTMLParser
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import Message, ParseOptions, ParseResult


TIMESTAMP_RE = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})(?::\d{2})?\]\s*")
WECHAT_BLOCK_RE = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(.+?)\s*$")


def parse_timestamp_value(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        # WeChat-like exports sometimes use seconds or milliseconds.
        raw = float(value)
        if raw > 10_000_000_000:
            raw = raw / 1000
        try:
            return datetime.fromtimestamp(raw)
        except (OSError, OverflowError, ValueError):
            return None
    text = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M", "%Y/%m/%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


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
        timestamp = parse_timestamp_value(ts_value)
        speaker_value = str(record.get("speaker") or record.get("sender") or record.get("from") or options.other_name)
        speaker = normalize_speaker(speaker_value, options)
        content = str(record.get("content") or record.get("text") or record.get("message") or "")
        messages.append(
            Message(timestamp=timestamp, speaker=speaker, content=content, raw=json.dumps(record, ensure_ascii=False), source_line=idx)
        )
    if not messages:
        warnings.append("No JSON chat records parsed.")
    return ParseResult(messages=messages, format="json", warnings=warnings)


def parse_csv(path: Path, options: ParseOptions) -> ParseResult:
    messages: list[Message] = []
    warnings: list[str] = []
    with path.open("r", encoding=options.encoding, newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, record in enumerate(reader, start=2):
            ts_value = record.get("timestamp") or record.get("time") or record.get("createTime") or record.get("datetime")
            speaker_value = record.get("speaker") or record.get("sender") or record.get("from") or options.other_name
            content = record.get("content") or record.get("text") or record.get("message") or ""
            message_type = record.get("type") or record.get("message_type") or "text"
            speaker = normalize_speaker(str(speaker_value), options)
            messages.append(
                Message(
                    timestamp=parse_timestamp_value(ts_value),
                    speaker=speaker,
                    content=str(content),
                    raw=json.dumps(record, ensure_ascii=False),
                    source_line=idx,
                    message_type=str(message_type or "text"),
                )
            )
    if not messages:
        warnings.append("No CSV chat records parsed.")
    return ParseResult(messages=messages, format="csv", warnings=warnings)


class _ChatHTMLParser(HTMLParser):
    def __init__(self, options: ParseOptions) -> None:
        super().__init__(convert_charrefs=True)
        self.options = options
        self.messages: list[Message] = []
        self.current: dict[str, Any] | None = None
        self.depth = 0
        self.capture_content = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value or "" for key, value in attrs}
        classes = set(attr.get("class", "").split())
        if tag == "div" and "message" in classes and attr.get("data-time"):
            self.current = {
                "timestamp": parse_timestamp_value(attr.get("data-time")),
                "speaker": normalize_speaker(attr.get("data-speaker", self.options.other_name), self.options),
                "content": [],
            }
            self.depth = 1
            self.capture_content = False
            return
        if self.current is not None:
            self.depth += 1
            if "content" in classes or tag in {"p", "span"}:
                self.capture_content = True

    def handle_data(self, data: str) -> None:
        if self.current is not None and self.capture_content:
            self.current["content"].append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.current is None:
            return
        self.depth -= 1
        if tag in {"span", "p"}:
            self.capture_content = False
        if self.depth <= 0:
            content = "".join(self.current["content"]).strip()
            self.messages.append(
                Message(
                    timestamp=self.current["timestamp"],
                    speaker=self.current["speaker"],
                    content=content,
                    raw=content,
                    source_line=None,
                )
            )
            self.current = None
            self.depth = 0
            self.capture_content = False


def parse_html(path: Path, options: ParseOptions) -> ParseResult:
    parser = _ChatHTMLParser(options)
    parser.feed(path.read_text(encoding=options.encoding))
    warnings: list[str] = []
    if not parser.messages:
        warnings.append("No HTML chat records parsed.")
    return ParseResult(messages=parser.messages, format="html", warnings=warnings)


def parse_wechat_text(path: Path, options: ParseOptions) -> ParseResult:
    messages: list[Message] = []
    current: dict[str, Any] | None = None
    for idx, raw in enumerate(path.read_text(encoding=options.encoding).splitlines(), start=1):
        match = WECHAT_BLOCK_RE.match(raw)
        if match:
            if current:
                messages.append(
                    Message(
                        timestamp=current["timestamp"],
                        speaker=current["speaker"],
                        content="\n".join(current["content"]).strip(),
                        raw="\n".join(current["raw"]).strip(),
                        source_line=current["source_line"],
                    )
                )
            current = {
                "timestamp": parse_timestamp_value(match.group(1)),
                "speaker": normalize_speaker(match.group(2).strip(), options),
                "content": [],
                "raw": [raw],
                "source_line": idx,
            }
            continue
        if current:
            current["content"].append(raw)
            current["raw"].append(raw)
    if current:
        messages.append(
            Message(
                timestamp=current["timestamp"],
                speaker=current["speaker"],
                content="\n".join(current["content"]).strip(),
                raw="\n".join(current["raw"]).strip(),
                source_line=current["source_line"],
            )
        )
    warnings: list[str] = []
    if path.stat().st_size and not messages:
        warnings.append("No WeChat text blocks parsed.")
    return ParseResult(messages=messages, format="wechat-text", warnings=warnings)


PARSERS = {
    "timestamp-text": parse_timestamp_text,
    "wechat-text": parse_wechat_text,
    "wechat-txt": parse_wechat_text,
    "json": parse_json,
    "csv": parse_csv,
    "html": parse_html,
}


def parser_choices() -> list[str]:
    return ["auto", *sorted(PARSERS)]


def infer_format(path: Path) -> str:
    sample = path.read_text(encoding="utf-8", errors="ignore")[:4096].lstrip()
    if sample.startswith("[") or sample.startswith("{"):
        try:
            json.loads(sample if len(sample) < 4096 else path.read_text(encoding="utf-8"))
            return "json"
        except json.JSONDecodeError:
            pass
    first_line = sample.splitlines()[0] if sample.splitlines() else ""
    lowered = first_line.lower()
    if "," in first_line and any(name in lowered.split(",") for name in ("timestamp", "time", "datetime")):
        return "csv"
    if "<html" in sample.lower() or 'class="message"' in sample.lower() or "class='message'" in sample.lower():
        return "html"
    if WECHAT_BLOCK_RE.match(first_line):
        return "wechat-text"
    if TIMESTAMP_RE.search(sample):
        return "timestamp-text"
    suffix = path.suffix.lower()
    if suffix == ".json":
        return "json"
    if suffix == ".csv":
        return "csv"
    if suffix in {".html", ".htm"}:
        return "html"
    return "timestamp-text"


def parse_chat(path: Path, options: ParseOptions | None = None, fmt: str = "auto") -> ParseResult:
    options = options or ParseOptions()
    selected = infer_format(path) if fmt == "auto" else fmt
    if selected not in PARSERS:
        raise SystemExit(f"Unsupported chat format: {fmt}")
    return PARSERS[selected](path, options)
