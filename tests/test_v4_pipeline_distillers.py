from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "scripts" / "distill_chat_pipeline.py"


class V4PipelineDistillerTests(unittest.TestCase):
    def run_pipeline(self, source_text: str, *extra_args: str):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        tmp_path = Path(temp.name)
        source_dir = tmp_path / "private-source-folder"
        source_dir.mkdir()
        source = source_dir / "chat.txt"
        output_dir = tmp_path / "bundle"
        source.write_text(source_text, encoding="utf-8")
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
        return source, output_dir

    def test_bundle_contains_real_distilled_markdown_not_placeholders(self) -> None:
        _source, output_dir = self.run_pipeline(
            "[2026-05-14 09:00] Me: 早\n"
            "[2026-05-14 09:01] Her: 早哦\n"
            "[2026-05-14 09:02] Me: 我好累\n"
            "[2026-05-14 09:03] Her: 那你别硬撑\n"
            "[2026-05-14 09:04] Her: 我听着呢\n"
            "[2026-05-14 09:05] Me: 我想你\n"
            "[2026-05-14 09:06] Her: 笨蛋\n"
            "[2026-05-14 09:07] Her: 过来抱一下\n"
        )

        for name in ("emotional-memory-profile.md", "relationship-texture.md", "scenario-response-guide.md", "session-memory.md"):
            text = (output_dir / name).read_text(encoding="utf-8")
            self.assertNotIn("Review and complete", text)
            self.assertIn("Evidence", text)
            self.assertIn("Observed", text)

        style_profile = json.loads((output_dir / "style-profile.json").read_text(encoding="utf-8"))
        for key in ("observed_traits", "emotional_moves", "relationship_loops", "reply_shapes", "evidence_notes", "confidence"):
            self.assertIn(key, style_profile)
        self.assertGreater(style_profile["confidence"]["overall"], 0)

    def test_manifest_omits_full_source_path_and_privacy_candidates_are_truncated_by_default(self) -> None:
        source, output_dir = self.run_pipeline(
            "[2026-05-14 09:00] Me: 我的号码是 13812345678\n"
            "[2026-05-14 09:01] Her: 记得 123456789012345 这个单号\n"
        )

        manifest_text = (output_dir / "manifest.json").read_text(encoding="utf-8")
        manifest = json.loads(manifest_text)
        self.assertEqual("chat.txt", manifest["source"]["name"])
        self.assertNotIn("path", manifest["source"])
        self.assertNotIn(str(source.parent), manifest_text)

        privacy_text = (output_dir / "privacy-candidates.json").read_text(encoding="utf-8")
        self.assertNotIn("123456789012345", privacy_text)
        self.assertIn("hash", privacy_text)

    def test_full_privacy_audit_can_keep_raw_candidates_locally(self) -> None:
        _source, output_dir = self.run_pipeline(
            "[2026-05-14 09:00] Me: 记得 123456789012345 这个单号\n",
            "--full-privacy-audit",
        )

        privacy_text = (output_dir / "privacy-candidates.json").read_text(encoding="utf-8")
        self.assertIn("123456789012345", privacy_text)


if __name__ == "__main__":
    unittest.main()
