from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "scripts" / "distill_chat_pipeline.py"


class V3PipelineTests(unittest.TestCase):
    def test_pipeline_writes_expected_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "chat.txt"
            output_dir = tmp_path / "out"
            source.write_text(
                "[2026-05-14 09:00] Me: hi\n"
                "[2026-05-14 09:01] Her: hey\n",
                encoding="utf-8",
            )

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
                ],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)

            expected_files = {
                "sanitized-chat.txt",
                "privacy-candidates.json",
                "evidence-map.json",
                "analysis-summary.json",
                "style-profile.json",
                "bundle-index.md",
                "style-card.md",
                "export-health.md",
                "emotional-memory-profile.md",
                "relationship-texture.md",
                "scenario-response-guide.md",
                "private-emotional-router.md",
                "memory-companion-mode.md",
                "session-memory.md",
                "evaluation-report.json",
                "evaluation-report.md",
                "evaluation-transcript.json",
                "readiness-report.json",
                "session-memory.schema.json",
                "manifest.json",
            }
            actual_files = {path.name for path in output_dir.iterdir() if path.is_file()}
            self.assertTrue(expected_files.issubset(actual_files))

            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(sorted(expected_files), sorted(manifest["artifacts"]))
            self.assertEqual("2026-05-14 09:00", manifest["source"]["first_timestamp"])
            self.assertEqual("2026-05-14 09:01", manifest["source"]["last_timestamp"])


if __name__ == "__main__":
    unittest.main()
