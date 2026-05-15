from __future__ import annotations

import unittest
from datetime import datetime, timedelta
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from chat_style_distillation.evidence import build_evidence_map  # noqa: E402
from chat_style_distillation.health import assess_health  # noqa: E402
from chat_style_distillation.models import Message  # noqa: E402
from chat_style_distillation.readiness import compute_readiness  # noqa: E402


class V5EvidenceTests(unittest.TestCase):
    def msg(self, minute: int, speaker: str, content: str) -> Message:
        return Message(
            timestamp=datetime.strptime("2026-05-14 09:00", "%Y-%m-%d %H:%M") + timedelta(minutes=minute),
            speaker=speaker,
            content=content,
            raw=content,
        )

    def test_evidence_map_uses_hashes_and_paraphrases_without_raw_source_text(self) -> None:
        messages = [
            self.msg(0, "SELF", "I miss you"),
            self.msg(1, "Her", "come here, I am listening"),
            self.msg(2, "SELF", "I am tired"),
            self.msg(3, "Her", "do not push yourself"),
        ]

        evidence = build_evidence_map(messages, target_speaker="Her", limit=3)

        self.assertIn("comfort", evidence["scenes"])
        comfort_item = evidence["scenes"]["comfort"]["items"][0]
        self.assertIn("hash", comfort_item)
        self.assertIn("paraphrase", comfort_item)
        serialized = str(evidence)
        self.assertNotIn("come here, I am listening", serialized)
        self.assertNotIn("do not push yourself", serialized)


class V5ReadinessTests(unittest.TestCase):
    def msg(self, minute: int, speaker: str, content: str) -> Message:
        return Message(
            timestamp=datetime.strptime("2026-05-14 09:00", "%Y-%m-%d %H:%M") + timedelta(minutes=minute),
            speaker=speaker,
            content=content,
            raw=content,
        )

    def test_readiness_combines_health_privacy_coverage_and_evaluation(self) -> None:
        messages = [self.msg(i, "Her" if i % 2 else "SELF", f"message {i}") for i in range(80)]
        health = assess_health(messages, min_messages=50)
        evidence = {"coverage": {"covered_scenes": ["daily", "comfort", "missing"], "missing_core_scenes": []}}
        privacy_candidates = {}
        evaluation = {"warnings": [], "dimensions": {"visible_router_leakage": {"score": 100}}}

        ready = compute_readiness(
            health=health,
            privacy_candidates=privacy_candidates,
            evidence_map=evidence,
            evaluation_report=evaluation,
        )
        self.assertEqual("ready-for-private-companion", ready["state"])

        blocked = compute_readiness(
            health=health,
            privacy_candidates={"LONG_NUMBER": [{"hash": "abc"}]},
            evidence_map=evidence,
            evaluation_report=evaluation,
        )
        self.assertEqual("review-needed", blocked["state"])
        self.assertIn("privacy_candidates", {item["code"] for item in blocked["blocks"]})


if __name__ == "__main__":
    unittest.main()
