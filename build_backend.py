from __future__ import annotations

import base64
import csv
import hashlib
import io
from pathlib import Path
import zipfile


NAME = "chat-style-distillation"
DIST = "chat_style_distillation"
VERSION = "0.5.0"
DIST_INFO = f"{DIST}-{VERSION}.dist-info"
TAG = "py3-none-any"


def get_requires_for_build_wheel(config_settings: dict | None = None) -> list[str]:
    return []


def get_requires_for_build_editable(config_settings: dict | None = None) -> list[str]:
    return []


def prepare_metadata_for_build_wheel(metadata_directory: str, config_settings: dict | None = None) -> str:
    return _write_metadata_dir(Path(metadata_directory))


def prepare_metadata_for_build_editable(metadata_directory: str, config_settings: dict | None = None) -> str:
    return _write_metadata_dir(Path(metadata_directory))


def build_wheel(
    wheel_directory: str,
    config_settings: dict | None = None,
    metadata_directory: str | None = None,
) -> str:
    return _build_wheel(Path(wheel_directory), editable=False)


def build_editable(
    wheel_directory: str,
    config_settings: dict | None = None,
    metadata_directory: str | None = None,
) -> str:
    return _build_wheel(Path(wheel_directory), editable=True)


def _write_metadata_dir(base: Path) -> str:
    dist_info = base / DIST_INFO
    dist_info.mkdir(parents=True, exist_ok=True)
    (dist_info / "METADATA").write_text(_metadata(), encoding="utf-8")
    (dist_info / "WHEEL").write_text(_wheel_metadata(), encoding="utf-8")
    (dist_info / "entry_points.txt").write_text(_entry_points(), encoding="utf-8")
    (dist_info / "top_level.txt").write_text(f"{DIST}\n", encoding="utf-8")
    (dist_info / "RECORD").write_text("", encoding="utf-8")
    return DIST_INFO


def _build_wheel(wheel_dir: Path, *, editable: bool) -> str:
    wheel_dir.mkdir(parents=True, exist_ok=True)
    wheel_name = f"{DIST}-{VERSION}-{TAG}.whl"
    wheel_path = wheel_dir / wheel_name
    root = Path(__file__).resolve().parent
    records: list[tuple[str, bytes]] = []

    def add(path: str, data: str | bytes) -> None:
        payload = data.encode("utf-8") if isinstance(data, str) else data
        records.append((path, payload))

    add(f"{DIST_INFO}/METADATA", _metadata())
    add(f"{DIST_INFO}/WHEEL", _wheel_metadata())
    add(f"{DIST_INFO}/entry_points.txt", _entry_points())
    add(f"{DIST_INFO}/top_level.txt", f"{DIST}\n")
    if editable:
        add(f"__editable__.{DIST}.pth", f"{root / 'src'}\n")
    else:
        for source in (root / "src" / DIST).rglob("*.py"):
            archive_name = source.relative_to(root / "src").as_posix()
            add(archive_name, source.read_bytes())

    record_text = _record_text(records, f"{DIST_INFO}/RECORD")
    add(f"{DIST_INFO}/RECORD", record_text)
    with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_DEFLATED) as wheel:
        for archive_name, payload in records:
            wheel.writestr(archive_name, payload)
    return wheel_name


def _metadata() -> str:
    return (
        "Metadata-Version: 2.1\n"
        f"Name: {NAME}\n"
        f"Version: {VERSION}\n"
        "Summary: Local chat style distillation into private emotional companion bundles\n"
        "Requires-Python: >=3.10\n"
    )


def _wheel_metadata() -> str:
    return (
        "Wheel-Version: 1.0\n"
        "Generator: chat-style-distillation-build-backend\n"
        "Root-Is-Purelib: true\n"
        f"Tag: {TAG}\n"
    )


def _entry_points() -> str:
    return "[console_scripts]\nchat-style-distill = chat_style_distillation.cli:main\n"


def _record_text(records: list[tuple[str, bytes]], record_path: str) -> str:
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    for archive_name, payload in records:
        digest = base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).rstrip(b"=").decode("ascii")
        writer.writerow([archive_name, f"sha256={digest}", str(len(payload))])
    writer.writerow([record_path, "", ""])
    return output.getvalue()
