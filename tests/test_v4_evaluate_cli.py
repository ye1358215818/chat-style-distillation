from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from chat_style_distillation.evaluate import evaluate  # noqa: E402


class V4EvaluationTests(unittest.TestCase):
    def test_evaluation_scores_length_phrase_and_scene_drift(self) -> None:
        analysis = {
            "speakers": {
                "Her": {
                    "p90_text_length": 8,
                    "avg_text_length": 3,
                    "top_short_phrases": [["早哦", 3], ["我听着呢", 2]],
                    "scene_counts": [["comfort", 4]],
                }
            }
        }
        profile = {"voice": {"phrases": ["早哦", "我听着呢"]}, "scenario_models": {"comfort": {}}}
        report = evaluate(
            "As an AI based on chat logs, I will provide emotional support. "
            "我会永远爱你，你是我的全世界，这是一段很长很长完全不像聊天的说明文字。",
            profile=profile,
            analysis=analysis,
        )

        self.assertIn("phrase_fit", report["dimensions"])
        self.assertIn("length_drift", report["dimensions"])
        self.assertLess(report["dimensions"]["phrase_fit"]["score"], 80)
        self.assertLess(report["dimensions"]["length_drift"]["score"], 80)
        self.assertTrue(any("source phrase" in warning for warning in report["warnings"]))


class V4CliTests(unittest.TestCase):
    def test_module_cli_runs_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "chat.txt"
            output_dir = tmp_path / "out"
            source.write_text(
                "[2026-05-14 09:00] Me: hi\n"
                "[2026-05-14 09:01] Her: hey\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["PYTHONPATH"] = str(SRC)
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "chat_style_distillation.cli",
                    "run",
                    str(source),
                    "--self-name",
                    "Me",
                    "--other-name",
                    "Her",
                    "--output-dir",
                    str(output_dir),
                ],
                check=False,
                text=True,
                capture_output=True,
                env=env,
            )

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["manifest"].endswith("manifest.json"))
            self.assertTrue((output_dir / "bundle-index.md").exists())


if __name__ == "__main__":
    unittest.main()
