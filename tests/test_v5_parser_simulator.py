from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from chat_style_distillation.models import ParseOptions  # noqa: E402
from chat_style_distillation.parsers import parse_chat  # noqa: E402
from chat_style_distillation.reply_simulator import generate_evaluation_transcript  # noqa: E402


class V5ParserSniffingTests(unittest.TestCase):
    def write_txt(self, text: str) -> Path:
        temp = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False, newline="")
        with temp:
            temp.write(text)
        self.addCleanup(Path(temp.name).unlink, missing_ok=True)
        return Path(temp.name)

    def test_auto_sniffs_json_csv_html_and_wechat_text_inside_txt_files(self) -> None:
        cases = [
            ('[{"timestamp":"2026-05-14 09:00","speaker":"Me","content":"json"}]', "json"),
            ("timestamp,speaker,content\n2026-05-14 09:00,Me,csv\n", "csv"),
            ('<div class="message" data-time="2026-05-14 09:00" data-speaker="Me"><span class="content">html</span></div>', "html"),
            ("2026-05-14 09:00:00 Me\nwechat\n", "wechat-text"),
        ]
        for text, expected_format in cases:
            with self.subTest(expected_format=expected_format):
                result = parse_chat(self.write_txt(text), ParseOptions(self_name="Me", other_name="Her"), fmt="auto")
                self.assertEqual(expected_format, result.format)
                self.assertEqual(1, len(result.messages))


class V5ReplySimulatorTests(unittest.TestCase):
    def test_simulator_generates_replies_without_visible_router_labels(self) -> None:
        prompts = [{"scene": "comfort", "prompt": "I am tired"}]
        profile = {
            "voice": {"phrases": ["I am listening"]},
            "scenario_models": {"comfort": {"length": "short", "moves": ["source_rhythm"]}},
            "reply_shapes": {"ordinary": "short"},
        }

        transcript = generate_evaluation_transcript(prompts, profile)

        self.assertEqual(1, len(transcript["items"]))
        reply = transcript["items"][0]["generated_reply"]
        self.assertIn("I am listening", reply)
        self.assertNotIn("[comfort", reply.lower())
        self.assertIn("score", transcript["items"][0])


if __name__ == "__main__":
    unittest.main()
