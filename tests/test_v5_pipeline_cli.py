from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "scripts" / "distill_chat_pipeline.py"


class V5PipelineCliTests(unittest.TestCase):
    def run_pipeline(self, text: str, *extra_args: str):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        tmp_path = Path(temp.name)
        source = tmp_path / "chat.txt"
        output_dir = tmp_path / "bundle"
        source.write_text(text, encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(PIPELINE),
                str(source),
                "--self-name",
                "Me",
                "--other-name",
                "Her",
                "--output-dir",
                str(output_dir),
                *extra_args,
            ],
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)
        return output_dir

    def test_pipeline_outputs_v5_artifacts_and_profile_evidence(self) -> None:
        output_dir = self.run_pipeline(
            "[2026-05-14 09:00] Me: I miss you\n"
            "[2026-05-14 09:01] Her: come here\n"
            "[2026-05-14 09:02] Me: I am tired\n"
            "[2026-05-14 09:03] Her: I am listening\n",
            "--generate-eval-replies",
            "--min-messages",
            "1",
            "--locale",
            "zh-CN",
        )

        for name in ("evidence-map.json", "evaluation-transcript.json", "readiness-report.json", "session-memory.schema.json"):
            self.assertTrue((output_dir / name).exists(), name)

        manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual("0.5.0", manifest["version"])
        self.assertNotIn("path", manifest["source"])
        self.assertIn("evidence-map.json", manifest["artifacts"])

        profile = json.loads((output_dir / "style-profile.json").read_text(encoding="utf-8"))
        for key in ("evidence_refs", "scene_evidence", "paraphrased_examples", "coverage_gaps"):
            self.assertIn(key, profile)

        transcript = json.loads((output_dir / "evaluation-transcript.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(transcript["items"]), 1)
        self.assertNotIn("[", transcript["items"][0]["generated_reply"])

    def test_publish_mode_redacts_self_and_other_names_by_default(self) -> None:
        output_dir = self.run_pipeline(
            "[2026-05-14 09:00] Me: Her should not appear in publish mode\n"
            "[2026-05-14 09:01] Her: Me should not appear either\n",
            "--mode",
            "publish",
            "--publish-redact-names",
        )

        sanitized = (output_dir / "sanitized-chat.txt").read_text(encoding="utf-8")
        self.assertNotIn(" Me", sanitized)
        self.assertNotIn(" Her", sanitized)


if __name__ == "__main__":
    unittest.main()
