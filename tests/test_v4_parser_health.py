from __future__ import annotations

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from chat_style_distillation.health import assess_health  # noqa: E402
from chat_style_distillation.models import Message, ParseOptions  # noqa: E402
from chat_style_distillation.parsers import PARSERS, parse_chat  # noqa: E402


class V4ParserRegistryTests(unittest.TestCase):
    def write_file(self, text: str, suffix: str) -> Path:
        temp = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=suffix, delete=False, newline="")
        with temp:
            temp.write(text)
        self.addCleanup(Path(temp.name).unlink, missing_ok=True)
        return Path(temp.name)

    def test_parser_registry_includes_v4_formats(self) -> None:
        for fmt in ("timestamp-text", "wechat-text", "wechat-txt", "json", "csv", "html"):
            self.assertIn(fmt, PARSERS)

    def test_reads_csv_chat_exports(self) -> None:
        path = self.write_file(
            "timestamp,speaker,content\n"
            "2026-05-14 09:00,Me,早\n"
            "2026-05-14 09:01,Her,\"我在\n听你说\"\n",
            ".csv",
        )

        result = parse_chat(path, ParseOptions(self_name="Me", other_name="Her"), fmt="csv")

        self.assertEqual("csv", result.format)
        self.assertEqual(["SELF", "Her"], [message.speaker for message in result.messages])
        self.assertEqual("我在\n听你说", result.messages[1].content)

    def test_reads_html_chat_exports(self) -> None:
        path = self.write_file(
            '<div class="message" data-time="2026-05-14 09:00" data-speaker="Me">'
            '<span class="content">早</span></div>'
            '<div class="message" data-time="2026-05-14 09:02" data-speaker="Her">'
            '<span class="content">别硬撑</span></div>',
            ".html",
        )

        result = parse_chat(path, ParseOptions(self_name="Me", other_name="Her"), fmt="html")

        self.assertEqual("html", result.format)
        self.assertEqual(["早", "别硬撑"], [message.content for message in result.messages])
        self.assertEqual(["SELF", "Her"], [message.speaker for message in result.messages])

    def test_reads_wechat_text_blocks(self) -> None:
        path = self.write_file(
            "2026-05-14 09:00:00 Me\n"
            "早\n"
            "2026-05-14 09:01:00 Her\n"
            "我听着呢\n",
            ".txt",
        )

        result = parse_chat(path, ParseOptions(self_name="Me", other_name="Her"), fmt="wechat-text")

        self.assertEqual("wechat-text", result.format)
        self.assertEqual(["早", "我听着呢"], [message.content for message in result.messages])
        self.assertEqual(["SELF", "Her"], [message.speaker for message in result.messages])


class V4HealthTests(unittest.TestCase):
    def msg(self, ts: str, speaker: str, content: str, message_type: str = "text") -> Message:
        return Message(
            timestamp=datetime.strptime(ts, "%Y-%m-%d %H:%M"),
            speaker=speaker,
            content=content,
            raw=content,
            message_type=message_type,
        )

    def test_health_flags_gaps_duplicates_order_and_media(self) -> None:
        messages = [
            self.msg("2026-01-01 09:00", "SELF", "早"),
            self.msg("2026-03-10 09:00", "OTHER", "早"),
            self.msg("2026-03-09 09:00", "OTHER", "早"),
            self.msg("2026-03-11 09:00", "OTHER", "[图片]", "media"),
            self.msg("2026-03-11 09:00", "OTHER", "[图片]", "media"),
        ]

        health = assess_health(messages)
        codes = {issue["code"] for issue in health["issues"]}

        self.assertEqual("review-needed", health["readiness"])
        self.assertIn("low_volume", codes)
        self.assertIn("time_gap", codes)
        self.assertIn("out_of_order", codes)
        self.assertIn("duplicate_message", codes)
        self.assertIn("speaker_imbalance", codes)
        self.assertIn("high_media_ratio", codes)


if __name__ == "__main__":
    unittest.main()
