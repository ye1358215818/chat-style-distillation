from __future__ import annotations

from typing import Any


SCENE_LABELS = {
    "daily": "ordinary daily contact",
    "missing": "missing and reaching",
    "comfort": "comfort and staying near",
    "conflict": "friction and hurt",
    "apology": "repair and softening",
    "jealousy": "jealousy and insecurity",
    "coldness": "distance and clipped replies",
    "repair": "repair and return",
    "impulse": "impulse to contact",
    "certainty_seeking": "certainty-seeking",
    "unspecified": "unclassified everyday texture",
}


def target_summary(analysis: dict[str, Any], target_speaker: str) -> dict[str, Any]:
    speakers = analysis.get("speakers", {})
    return speakers.get(target_speaker) or speakers.get("OTHER") or next(iter(speakers.values()), {})


def source_phrases(target: dict[str, Any], limit: int = 8) -> list[str]:
    return [phrase for phrase, _count in target.get("top_short_phrases", [])[:limit] if phrase]


def scene_names(target: dict[str, Any]) -> list[str]:
    return [scene for scene, _count in target.get("scene_counts", []) if scene]


def confidence_from_analysis(analysis: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    total = int(analysis.get("total_messages", 0))
    target_count = int(target.get("text_messages", 0))
    scene_count = len(target.get("scene_counts", []))
    data_volume = min(1.0, total / 500)
    speaker_signal = min(1.0, target_count / 200)
    scene_coverage = min(1.0, scene_count / 6)
    overall = round((data_volume * 0.35 + speaker_signal * 0.35 + scene_coverage * 0.30) * 100, 2)
    return {
        "overall": overall,
        "data_volume": round(data_volume * 100, 2),
        "speaker_signal": round(speaker_signal * 100, 2),
        "scene_coverage": round(scene_coverage * 100, 2),
    }


def build_observed_traits(analysis: dict[str, Any], target_speaker: str) -> list[str]:
    target = target_summary(analysis, target_speaker)
    phrases = source_phrases(target, 5)
    traits = [
        f"Observed average text length around {target.get('avg_text_length', 0)} characters.",
        f"Observed median text length around {target.get('median_text_length', 0)} characters.",
        f"Observed p90 text length around {target.get('p90_text_length', 0)} characters.",
    ]
    burst = analysis.get("burst_stats", {}).get(target_speaker) or analysis.get("burst_stats", {}).get("OTHER")
    if burst:
        traits.append(f"Observed burst habit: max {burst.get('max_burst_size', 0)} consecutive message(s).")
    if phrases:
        traits.append("Observed small words and anchors: " + ", ".join(phrases) + ".")
    return traits


def build_emotional_moves(analysis: dict[str, Any], target_speaker: str) -> dict[str, str]:
    target = target_summary(analysis, target_speaker)
    scenes = dict(target.get("scene_counts", []))
    return {
        "care": f"Observed {scenes.get('comfort', 0)} comfort message(s); keep care concrete and close to the user's words.",
        "missing": f"Observed {scenes.get('missing', 0)} missing/reaching message(s); preserve softness without generic romance.",
        "friction": f"Observed {scenes.get('conflict', 0) + scenes.get('coldness', 0)} friction or distance message(s); keep clippedness if it appears in source.",
        "repair": f"Observed {scenes.get('repair', 0) + scenes.get('apology', 0)} repair message(s); use return/softening rather than lecture.",
        "certainty": f"Observed {scenes.get('certainty_seeking', 0)} certainty-seeking signal(s); answer from emotional texture instead of invented present-day facts.",
    }


def build_relationship_loops(analysis: dict[str, Any], target_speaker: str) -> list[str]:
    target = target_summary(analysis, target_speaker)
    scenes = scene_names(target)
    loops: list[str] = []
    if "comfort" in scenes:
        loops.append("Need rises -> the voice stays nearby -> the next reply should become smaller and more concrete.")
    if "missing" in scenes:
        loops.append("Longing appears -> familiar anchors matter -> avoid replacing the person with generic affectionate language.")
    if "conflict" in scenes or "coldness" in scenes:
        loops.append("Friction appears -> clipped replies or silence may be part of the texture -> repair should not rush.")
    if "repair" in scenes or "apology" in scenes:
        loops.append("Hurt softens -> return through ordinary words rather than a formal apology script.")
    return loops or ["Insufficient scene coverage; preserve observed rhythm and mark relationship loops for review."]


def build_reply_shapes(analysis: dict[str, Any], target_speaker: str) -> dict[str, str]:
    target = target_summary(analysis, target_speaker)
    burst = analysis.get("burst_stats", {}).get(target_speaker) or analysis.get("burst_stats", {}).get("OTHER") or {}
    return {
        "short": f"Use for casual or cold scenes; observed p10 length {target.get('p10_text_length', 0)}.",
        "ordinary": f"Use for daily continuation; observed median length {target.get('median_text_length', 0)}.",
        "burst": f"Use when the source tends to send consecutive messages; observed max burst {burst.get('max_burst_size', 0)}.",
        "long": f"Use only when the scene is serious; observed p90 length {target.get('p90_text_length', 0)}.",
        "silence": "If source evidence is sparse, use a small grounded line instead of an explanatory paragraph.",
    }


def build_evidence_notes(analysis: dict[str, Any], target_speaker: str) -> list[str]:
    target = target_summary(analysis, target_speaker)
    return [
        f"Observed total messages: {analysis.get('total_messages', 0)}.",
        f"Observed target text messages: {target.get('text_messages', 0)}.",
        f"Observed scenes: {', '.join(scene_names(target)) or 'none classified'}.",
        f"Observed phrases: {', '.join(source_phrases(target, 6)) or 'none repeated enough'}."
    ]


def _paraphrased_evidence(profile: dict[str, Any]) -> list[str]:
    examples = profile.get("paraphrased_examples", [])
    if examples:
        return [str(item) for item in examples[:8]]
    return ["No paraphrased scene evidence is available yet; review evidence-map.json."]


def render_emotional_memory(profile: dict[str, Any], *, locale: str = "en-US") -> str:
    moves = profile.get("emotional_moves", {})
    evidence = profile.get("evidence_notes", [])
    paraphrases = _paraphrased_evidence(profile)
    if locale == "zh-CN":
        lines = ["# 情绪记忆画像", "", "## Observed Emotional Moves / 已观察情绪动作", ""]
        lines.extend(f"- {name}: {text}" for name, text in moves.items())
        lines.extend(["", "## Evidence Notes / 证据摘要", ""])
        lines.extend(f"- {item}" for item in evidence)
        lines.extend(["", "## Paraphrased Evidence / 转述证据", ""])
        lines.extend(f"- {item}" for item in paraphrases)
        lines.extend([
            "",
            "## Companion Translation / 陪伴转译",
            "",
            "- 先贴近原始节奏，再表达安慰。",
            "- 优先使用来源中出现过的小词、停顿和靠近方式，不用泛泛的甜言蜜语替代具体关系感。",
        ])
        return "\n".join(lines) + "\n"
    lines = ["# Emotional Memory Profile", "", "## Observed Emotional Moves", ""]
    lines.extend(f"- {name}: {text}" for name, text in moves.items())
    lines.extend(["", "## Evidence Notes", ""])
    lines.extend(f"- {item}" for item in evidence)
    lines.extend(["", "## Paraphrased Evidence", ""])
    lines.extend(f"- {item}" for item in paraphrases)
    lines.extend(["", "## Companion Translation", "", "- Keep the care close to the observed rhythm.", "- Use familiar small words before abstract explanation."])
    return "\n".join(lines) + "\n"


def render_relationship_texture(profile: dict[str, Any], *, locale: str = "en-US") -> str:
    loops = profile.get("relationship_loops", [])
    traits = profile.get("observed_traits", [])
    gaps = profile.get("coverage_gaps", [])
    if locale == "zh-CN":
        lines = ["# 关系纹理", "", "## Observed Loops / 已观察关系循环", ""]
        lines.extend(f"- {loop}" for loop in loops)
        lines.extend(["", "## Evidence Notes / 证据摘要", ""])
        lines.extend(f"- {trait}" for trait in traits)
        lines.extend(["", "## Coverage Gaps / 覆盖缺口", ""])
        lines.extend(f"- {gap}" for gap in gaps or ["No deterministic core-scene gap detected."])
        lines.extend(["", "## Companion Translation / 陪伴转译", "", "- 靠近、拉开、沉默和修复都按原关系的速度来，不把所有场景都压成同一种温柔。"])
        return "\n".join(lines) + "\n"
    lines = ["# Relationship Texture", "", "## Observed Loops", ""]
    lines.extend(f"- {loop}" for loop in loops)
    lines.extend(["", "## Evidence Notes", ""])
    lines.extend(f"- {trait}" for trait in traits)
    lines.extend(["", "## Coverage Gaps", ""])
    lines.extend(f"- {gap}" for gap in gaps or ["No deterministic core-scene gap detected."])
    lines.extend(["", "## Companion Translation", "", "- Let closeness, distance, and repair keep their original pace."])
    return "\n".join(lines) + "\n"


def render_scenario_guide(profile: dict[str, Any], *, locale: str = "en-US") -> str:
    scenarios = profile.get("scenario_models", {})
    scene_evidence = profile.get("scene_evidence", {})
    if locale == "zh-CN":
        lines = ["# 场景回应指南", "", "## Observed Scenario Shapes / 已观察场景形状", ""]
        for scene, model in scenarios.items():
            label = SCENE_LABELS.get(scene, scene)
            summary = scene_evidence.get(scene, {})
            count = summary.get("count", 0)
            lines.append(f"- {label}: {model.get('tone', '')} {model.get('length', '')} Evidence count: {count}".strip())
        lines.extend(["", "## Evidence Notes / 证据摘要", ""])
        lines.extend(f"- Observed {scene}: {model.get('trigger', '')}" for scene, model in scenarios.items())
        lines.extend(["", "## Companion Translation / 陪伴转译", "", "- 私下选择场景和回复形状，用户看到的只是一条自然聊天消息。"])
        return "\n".join(lines) + "\n"
    lines = ["# Scenario Response Guide", "", "## Observed Scenario Shapes", ""]
    for scene, model in scenarios.items():
        label = SCENE_LABELS.get(scene, scene)
        summary = scene_evidence.get(scene, {})
        count = summary.get("count", 0)
        lines.append(f"- {label}: {model.get('tone', '')} {model.get('length', '')} Evidence count: {count}".strip())
    lines.extend(["", "## Evidence Notes", ""])
    lines.extend(f"- Observed {scene}: {model.get('trigger', '')}" for scene, model in scenarios.items())
    lines.extend(["", "## Companion Translation", "", "- Privately choose the scene, then answer only as chat."])
    return "\n".join(lines) + "\n"


def render_session_memory(profile: dict[str, Any], health: dict[str, Any], *, locale: str = "en-US") -> str:
    if locale == "zh-CN":
        lines = [
            "# Companion Session Memory / 陪伴会话记忆",
            "",
            "## Observed Starting State / 已观察起点",
            "",
            f"- Readiness: {health.get('readiness')}",
            f"- Confidence: {profile.get('confidence', {}).get('overall', 0)}",
            "",
            "## Source Relationship Memory / 源关系记忆",
            "",
            "- 保留来源中的语气锚点、关系速度和场景回应方式。",
            "- 不把后续会话里的用户状态改写成历史事实。",
            "",
            "## Current User State To Update Later / 后续用户状态记忆",
            "",
            "- What soothed the user:",
            "- What made the user spiral:",
            "- Which source-style moves felt most real:",
            "- Where the voice started drifting:",
            "",
            "## Evidence Notes / 证据摘要",
            "",
        ]
        lines.extend(f"- {item}" for item in profile.get("evidence_notes", []))
        return "\n".join(lines) + "\n"
    lines = [
        "# Companion Session Memory",
        "",
        "## Observed Starting State",
        "",
        f"- Readiness: {health.get('readiness')}",
        f"- Confidence: {profile.get('confidence', {}).get('overall', 0)}",
        "",
        "## User-Care Memory To Update Later",
        "",
        "- What soothed the user:",
        "- What made the user spiral:",
        "- Which source-style moves felt most real:",
        "- Where the voice started drifting:",
        "",
        "## Evidence Notes",
        "",
    ]
    lines.extend(f"- {item}" for item in profile.get("evidence_notes", []))
    return "\n".join(lines) + "\n"
