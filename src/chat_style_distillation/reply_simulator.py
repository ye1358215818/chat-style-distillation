from __future__ import annotations

from typing import Any

from .evaluate import evaluate


def _base_phrase(profile: dict[str, Any]) -> str:
    phrases = profile.get("voice", {}).get("phrases", [])
    if phrases:
        return str(phrases[0])
    return "我在呢"


def simulate_reply(prompt: dict[str, Any], profile: dict[str, Any]) -> str:
    phrase = _base_phrase(profile)
    scene = str(prompt.get("scene", "daily"))
    if scene in {"comfort", "missing", "certainty_seeking", "impulse"}:
        return phrase
    if scene in {"conflict", "coldness"}:
        return phrase.split()[0] if " " in phrase else phrase[: max(1, min(len(phrase), 4))]
    if scene == "apology":
        return phrase if len(phrase) <= 12 else phrase[:12]
    return phrase


def generate_evaluation_transcript(prompts: list[dict[str, Any]], profile: dict[str, Any], analysis: dict[str, Any] | None = None) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for prompt in prompts:
        reply = simulate_reply(prompt, profile)
        report = evaluate(reply, profile=profile, analysis=analysis)
        items.append(
            {
                "scene": prompt.get("scene", "daily"),
                "prompt": prompt.get("prompt", ""),
                "generated_reply": reply,
                "expected_shape": profile.get("reply_shapes", {}).get("ordinary", "source-shaped reply"),
                "score": report.get("overall_score", 0),
                "warnings": report.get("warnings", []),
            }
        )
    return {"version": "0.5.0", "items": items}
