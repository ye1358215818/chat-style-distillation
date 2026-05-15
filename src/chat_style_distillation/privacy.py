from __future__ import annotations

import json
import re
import hashlib
from pathlib import Path
from typing import Any


HARD_IDENTIFIER_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("WXID", re.compile(r"\bwxid_[a-zA-Z0-9_-]{6,}\b")),
    ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("PHONE", re.compile(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)")),
    ("ID_CARD", re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)")),
    ("URL", re.compile(r"https?://[^\s<>\"]+")),
    ("WINDOWS_PATH", re.compile(r"[A-Za-z]:\\(?:[^\\/:*?\"<>|\r\n]+\\)*[^\\/:*?\"<>|\r\n]*")),
]

PUBLISH_EXTRA_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("MONEY", re.compile(r"(?:￥|¥)\s?\d+(?:\.\d+)?|\b\d+(?:\.\d+)?\s?(?:元|yuan)\b", re.IGNORECASE)),
]

MODE_PATTERNS = {
    "companion": HARD_IDENTIFIER_PATTERNS,
    "publish": HARD_IDENTIFIER_PATTERNS + PUBLISH_EXTRA_PATTERNS,
}

AUDIT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("LONG_NUMBER", re.compile(r"(?<!\d)\d{6,}(?!\d)")),
    ("DATE_LIKE", re.compile(r"\b\d{4}[-/.年]\d{1,2}(?:[-/.月]\d{1,2}日?)?\b")),
    ("QQ_LIKE", re.compile(r"(?<!\d)[1-9]\d{4,11}(?!\d)")),
    ("LOCATION_HINT", re.compile(r"[\u4e00-\u9fff]{2,12}(?:小区|公寓|学校|大学|公司|医院|酒店|路|街|镇|村|区|市)")),
]


def parse_replace(items: list[str]) -> list[tuple[str, str]]:
    replacements: list[tuple[str, str]] = []
    for item in items:
        if "=" not in item:
            raise SystemExit(f"--replace expects OLD=NEW, got: {item}")
        old, new = item.split("=", 1)
        if old:
            replacements.append((old, new))
    return replacements


def parse_replace_file(path: Path) -> list[tuple[str, str]]:
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return [(str(old), str(new)) for old, new in payload.items() if str(old)]
        if isinstance(payload, list):
            parsed: list[tuple[str, str]] = []
            for item in payload:
                if isinstance(item, dict) and item.get("old"):
                    parsed.append((str(item["old"]), str(item.get("new", ""))))
            return parsed
        raise SystemExit(f"Unsupported replacement JSON format: {path}")

    replacements: list[tuple[str, str]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "\t" in line:
            old, new = line.split("\t", 1)
        elif "=" in line:
            old, new = line.split("=", 1)
        else:
            raise SystemExit(f"Replacement file expects OLD=NEW or OLD<TAB>NEW, got: {raw}")
        if old:
            replacements.append((old, new))
    return replacements


def load_anchor_items(items: list[str]) -> set[str]:
    anchors: set[str] = set()
    for item in items:
        path = Path(item)
        if path.exists() and path.is_file():
            for raw in path.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if line and not line.startswith("#"):
                    anchors.add(line)
        elif item:
            anchors.add(item)
    return anchors


def anonymize(
    text: str,
    replacements: list[tuple[str, str]],
    self_name: str | None = None,
    other_name: str | None = None,
    mode: str = "publish",
    keep_anchors: set[str] | None = None,
) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}
    keep_anchors = keep_anchors or set()
    work_replacements = list(replacements)

    if self_name:
        work_replacements.append((self_name, "SELF"))
    if other_name:
        work_replacements.append((other_name, "OTHER"))

    for old, new in sorted(work_replacements, key=lambda item: len(item[0]), reverse=True):
        if not old or old in keep_anchors:
            continue
        n = text.count(old)
        if n:
            counts[f"literal:{new}"] = counts.get(f"literal:{new}", 0) + n
            text = text.replace(old, new)

    for label, pattern in MODE_PATTERNS[mode]:
        text, n = pattern.subn(f"[{label}]", text)
        if n:
            counts[label] = n
    return text, counts


def _safe_candidate(value: str, full: bool) -> dict[str, Any]:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]
    if full:
        return {"value": value, "hash": digest, "length": len(value)}
    if len(value) <= 6:
        preview = "*" * len(value)
    else:
        preview = value[:3] + "..." + value[-2:]
    return {"preview": preview, "hash": digest, "length": len(value)}


def audit_candidates(text: str, limit: int = 80, *, full: bool = False) -> dict[str, list[dict[str, Any]]]:
    candidates: dict[str, list[dict[str, Any]]] = {}
    for label, pattern in AUDIT_PATTERNS:
        seen: list[str] = []
        for match in pattern.finditer(text):
            value = match.group(0)
            if value not in seen:
                seen.append(value)
            if len(seen) >= limit:
                break
        if seen:
            candidates[label] = [_safe_candidate(value, full) for value in seen]
    return candidates
