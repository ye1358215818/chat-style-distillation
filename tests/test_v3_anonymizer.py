from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANONYMIZER = ROOT / "scripts" / "anonymize_chat.py"


class V3AnonymizerCliTests(unittest.TestCase):
    def test_replace_file_applies_literal_replacements(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "input.txt"
            output = tmp_path / "output.txt"
            replace_file = tmp_path / "replacements.txt"
            source.write_text("Real Name sent email real@example.com\n", encoding="utf-8")
            replace_file.write_text(
                "# comments and blank lines are ignored\n"
                "\n"
                "Real Name=PERSON_A\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ANONYMIZER),
                    str(source),
                    str(output),
                    "--mode",
                    "publish",
                    "--replace-file",
                    str(replace_file),
                ],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            self.assertEqual("PERSON_A sent email [EMAIL]\n", output.read_text(encoding="utf-8"))

    def test_keep_anchor_preserves_named_emotional_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "input.txt"
            output = tmp_path / "output.txt"
            replace_file = tmp_path / "replacements.txt"
            source.write_text("Old Cafe is our tiny ritual. Real Name paid 88 yuan.\n", encoding="utf-8")
            replace_file.write_text(
                "Old Cafe=LOCATION_A\n"
                "Real Name=PERSON_A\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ANONYMIZER),
                    str(source),
                    str(output),
                    "--mode",
                    "companion",
                    "--replace-file",
                    str(replace_file),
                    "--keep-anchor",
                    "Old Cafe",
                ],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            self.assertIn("Old Cafe is our tiny ritual.", output.read_text(encoding="utf-8"))
            self.assertNotIn("Real Name", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
