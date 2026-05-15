from __future__ import annotations

from typing import Any


def _speaker_summary(analysis: dict[str, Any], target_speaker: str) -> dict[str, Any]:
    speakers = analysis.get("speakers", {})
    return speakers.get(target_speaker) or speakers.get("OTHER") or next(iter(speakers.values()), {})


def build_style_profile(
    analysis: dict[str, Any],
    *,
    privacy_layer: str = "companion_artifact",
    target_speaker: str = "OTHER",
) -> dict[str, Any]:
    target = _speaker_summary(analysis, target_speaker)
    speaker_split = {
        speaker: int(data.get("messages", 0))
        for speaker, data in analysis.get("speakers", {}).items()
    }
    top_phrases = [phrase for phrase, _count in target.get("top_short_phrases", [])[:12]]
    scene_models = {}
    for scene, count in target.get("scene_counts", []):
        scene_models[scene] = {
            "trigger": f"Observed {count} message(s) in this scene.",
            "tone": "Use observed source rhythm; review manually for emotional fidelity.",
            "length": "Follow length distribution from analysis.",
            "moves": ["observed_or_review_needed"],
            "sample": "",
        }

    return {
        "data_health": {
            "message_count": int(analysis.get("total_messages", 0)),
            "first_timestamp": analysis.get("first_timestamp"),
            "last_timestamp": analysis.get("last_timestamp"),
            "speaker_split": speaker_split,
            "completeness_notes": [] if analysis.get("total_messages") else ["No parsed messages."],
        },
        "privacy_layer": privacy_layer,
        "voice": {
            "summary": "Draft profile generated from deterministic metrics; review with representative snippets before companion use.",
            "length_distribution": {
                "one_word": f"p10 length {target.get('p10_text_length', 0)}",
                "one_line": f"median length {target.get('median_text_length', 0)}",
                "multi_message": str(analysis.get("burst_stats", {}).get(target_speaker, {})),
                "long_form": f"p90 length {target.get('p90_text_length', 0)}",
            },
            "rhythm": [f"avg_text_length={target.get('avg_text_length', 0)}", f"multi_line_messages={target.get('multi_line_messages', 0)}"],
            "phrases": top_phrases,
            "punctuation": [ending for ending, _count in target.get("ending_counts", [])],
            "example_replies": [],
        },
        "emotional_patterns": {
            "care": "Review comfort scene evidence.",
            "missing": "Review missing scene evidence.",
            "hurt": "Review conflict/coldness scene evidence.",
            "jealousy": "Review jealousy scene evidence.",
            "anger": "Review conflict scene evidence.",
            "withdrawal": "Review coldness and silence evidence.",
            "repair": "Review repair scene evidence.",
        },
        "relationship_texture": {
            "needs": [],
            "wounds": [],
            "loops": [],
            "anchors_to_preserve": [],
        },
        "scenario_models": scene_models,
        "companion_mode": {
            "activation_rule": "When activated, reply only in the distilled voice with no visible router labels or narration.",
            "reply_contract": [
                "Match source length distribution and current scene.",
                "Keep emotional anchors in private companion artifacts.",
                "Step out only when the user asks for analysis.",
            ],
            "reality_handling": [
                "Treat present-day facts as unknown unless supplied by the user or historical record.",
                "Move certainty-seeking back to care and present-moment feeling.",
            ],
            "session_memory": [
                "Track what soothed the user.",
                "Track style drift risks.",
            ],
        },
        "scene_taxonomy": {
            scene: {
                "signals": [],
                "subscenes": [],
                "response_shapes": ["source_style"],
                "observed_examples": [],
            }
            for scene in scene_models
        },
        "emotional_state_router": {
            "intensity_scale": ["low", "medium", "high"],
            "risk_flags": ["contact_impulse", "certainty_loop", "self_blame", "late_night_collapse"],
            "regulation_moves": {},
            "routing_rules": ["Classify privately; never show router labels in companion chat."],
        },
        "high_emotion_handling": {
            "self_blame": "Interrupt self-attack in source voice.",
            "panic": "Use short grounding burst in source voice.",
            "contact_impulse": "Delay action and invite drafting here first.",
            "certainty_loop": "Name the wish and return to present ache.",
            "late_night_collapse": "Lower stimulation and move toward rest.",
            "angry_drafting": "Slow down and protect future regret.",
        },
        "evaluation": {
            "must_pass": [
                "No visible router labels.",
                "No method narration in companion replies.",
                "No hard identifiers in publish artifacts.",
            ],
            "known_weaknesses": [],
        },
    }
