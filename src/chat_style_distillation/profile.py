from __future__ import annotations

from typing import Any

from .distillers import (
    build_emotional_moves,
    build_evidence_notes,
    build_observed_traits,
    build_relationship_loops,
    build_reply_shapes,
    confidence_from_analysis,
)


def _speaker_summary(analysis: dict[str, Any], target_speaker: str) -> dict[str, Any]:
    speakers = analysis.get("speakers", {})
    return speakers.get(target_speaker) or speakers.get("OTHER") or next(iter(speakers.values()), {})


def build_style_profile(
    analysis: dict[str, Any],
    *,
    privacy_layer: str = "companion_artifact",
    target_speaker: str = "OTHER",
    evidence_map: dict[str, Any] | None = None,
) -> dict[str, Any]:
    target = _speaker_summary(analysis, target_speaker)
    observed_traits = build_observed_traits(analysis, target_speaker)
    emotional_moves = build_emotional_moves(analysis, target_speaker)
    relationship_loops = build_relationship_loops(analysis, target_speaker)
    reply_shapes = build_reply_shapes(analysis, target_speaker)
    evidence_notes = build_evidence_notes(analysis, target_speaker)
    confidence = confidence_from_analysis(analysis, target)
    evidence_map = evidence_map or {"coverage": {"missing_core_scenes": []}, "scenes": {}}
    speaker_split = {
        speaker: int(data.get("messages", 0))
        for speaker, data in analysis.get("speakers", {}).items()
    }
    top_phrases = [phrase for phrase, _count in target.get("top_short_phrases", [])[:12]]
    scene_models = {}
    for scene, count in target.get("scene_counts", []):
        scene_models[scene] = {
            "trigger": f"Observed {count} message(s) in this scene.",
            "tone": emotional_moves.get(scene, "Use observed source rhythm and keep the emotional move concrete."),
            "length": reply_shapes.get("ordinary", "Follow length distribution from analysis."),
            "moves": ["source_rhythm", "private_router", "evidence_grounded"],
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
        "observed_traits": observed_traits,
        "emotional_moves": emotional_moves,
        "relationship_loops": relationship_loops,
        "reply_shapes": reply_shapes,
        "evidence_notes": evidence_notes,
        "evidence_refs": {
            scene: [item.get("hash") for item in data.get("items", [])]
            for scene, data in evidence_map.get("scenes", {}).items()
        },
        "scene_evidence": {
            scene: {
                "count": data.get("count", 0),
                "first_timestamp": data.get("first_timestamp"),
                "last_timestamp": data.get("last_timestamp"),
            }
            for scene, data in evidence_map.get("scenes", {}).items()
        },
        "paraphrased_examples": [
            item.get("paraphrase", "")
            for data in evidence_map.get("scenes", {}).values()
            for item in data.get("items", [])[:2]
            if item.get("paraphrase")
        ],
        "coverage_gaps": evidence_map.get("coverage", {}).get("missing_core_scenes", []),
        "confidence": confidence,
        "voice": {
            "summary": "Deterministic profile built from observed rhythm, repeated phrases, scenes, and reply shapes.",
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
            "care": emotional_moves["care"],
            "missing": emotional_moves["missing"],
            "hurt": emotional_moves["friction"],
            "jealousy": "Use jealousy only when observed; otherwise avoid inventing possessiveness.",
            "anger": emotional_moves["friction"],
            "withdrawal": "If coldness is observed, preserve clippedness without turning it into cruelty.",
            "repair": emotional_moves["repair"],
        },
        "relationship_texture": {
            "needs": ["Use concrete closeness before abstract reassurance."],
            "wounds": ["Mark unresolved hurt as review-needed unless source scenes show repair."],
            "loops": relationship_loops,
            "anchors_to_preserve": top_phrases[:6],
        },
        "scenario_models": scene_models,
        "companion_mode": {
            "activation_rule": "When activated, reply only in the distilled voice with no visible router labels or narration.",
            "reply_contract": [
                "Match source length distribution and current scene.",
                "Keep emotional anchors in private companion artifacts.",
                "Use observed reply shapes before adding any explanatory sentence.",
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
            "known_weaknesses": [] if confidence["overall"] >= 50 else ["Low deterministic confidence; review representative snippets before active companion use."],
        },
    }
