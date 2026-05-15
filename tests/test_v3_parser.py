from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


analyze_chat = load_script("analyze_chat")


class V3ParserTests(unittest.TestCase):
    def write_chat(self, text: str, suffix: str = ".txt") -> Path:
        temp = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=suffix, delete=False)
        with temp:
            temp.write(text)
        self.addCleanup(Path(temp.name).unlink, missing_ok=True)
        return Path(temp.name)

    def read_messages(self, text: str, suffix: str = ".txt"):
        path = self.write_chat(text, suffix=suffix)
        return analyze_chat.read_messages(path, self_name="Me", other_name="OTHER")

    def test_reads_timestamped_chat_with_speakers(self) -> None:
        messages = self.read_messages(
            "[2026-05-14 09:00] Me: morning\n"
            "[2026-05-14 09:01] Her: hey\n"
        )

        self.assertEqual(2, len(messages))
        self.assertEqual("SELF", messages[0]["speaker"])
        self.assertEqual("morning", messages[0]["content"])
        self.assertEqual("Her", messages[1]["speaker"])
        self.assertEqual("hey", messages[1]["content"])

    def test_preserves_multiline_message_bodies(self) -> None:
        messages = self.read_messages(
            "[2026-05-14 09:00] Me: first line\n"
            "second line\n"
            "third line\n"
            "[2026-05-14 09:04] Her: next\n"
        )

        self.assertEqual("first line\nsecond line\nthird line", messages[0]["content"])
        self.assertEqual("next", messages[1]["content"])

    def test_splits_same_line_timestamp_messages(self) -> None:
        messages = self.read_messages(
            "[2026-05-14 09:00] Me: first "
            "[2026-05-14 09:01] Her: second "
            "[2026-05-14 09:02] Me: third"
        )

        self.assertEqual(["first", "second", "third"], [m["content"] for m in messages])
        self.assertEqual(["SELF", "Her", "SELF"], [m["speaker"] for m in messages])

    def test_reads_json_chat_exports(self) -> None:
        messages = self.read_messages(
            '[{"timestamp":"2026-05-14 09:00","speaker":"Me","content":"json one"},'
            '{"timestamp":"2026-05-14 09:03","speaker":"Her","content":"json two"}]',
            suffix=".json",
        )

        self.assertEqual(2, len(messages))
        self.assertEqual("SELF", messages[0]["speaker"])
        self.assertEqual("json one", messages[0]["content"])
        self.assertEqual("Her", messages[1]["speaker"])
        self.assertEqual("json two", messages[1]["content"])


if __name__ == "__main__":
    unittest.main()
