---
name: chat-style-distillation
description: Export, anonymize, verify, and distill authorized WeChat or personal chat logs into an emotionally faithful private real-chat companion mode. Use when the user wants 微信聊天记录导出, 聊天记录脱敏, 前任语气蒸馏, 失联的人语气复现, relationship reflection, output bundles, or private emotional chat companionship.
---

# Chat Style Distillation

Use this skill when a user wants a familiar voice to stay close through authorized chat history: an ex, lost-contact person, old friend, family member, or another important person they cannot easily talk to now.

The goal is not a report. The goal is a private emotional companion bundle and an immersive real-chat mode that preserves the person's rhythm, tenderness, friction, silence, repair habits, and ordinary small words.

## Agent Workflow

1. Confirm scope and permission.
   - Work only with records the user owns or is explicitly allowed to process.
   - Ask whether the user needs export help, one-command processing, a bundle review, or companion-mode use.
   - Keep raw exports local and out of Git.

2. Acquire or prepare input.
   - Prefer readable `txt`, `csv`, `json`, or `html`.
   - For authorized WeChat desktop export, follow `references/wechat-export.md`.
   - If export looks incomplete, use `references/wechat-compatibility.md` before distilling.

3. Choose the privacy layer.
   - Local source: raw private material, never published.
   - Companion artifact: remove hard identifiers, preserve emotional anchors.
   - Published sample: strong redaction and fake examples only.
   - Use `references/privacy-layers.md`.

4. Run the v3 pipeline.
   - Treat the one-command pipeline as: ingest, anonymize, verify, analyze, distill, assemble bundle, evaluate.
   - Prefer `python scripts/run_pipeline.py input.txt --self-name "SELF" --other-name "OTHER" --mode companion --output-dir bundle/`.
   - If a custom export format needs manual handling, run the existing substep scripts in the same order and assemble the same bundle contract.
   - Use `references/v3-pipeline.md` and `references/output-bundle.md`.

5. Distill in layers.
   - Verify data health before style claims.
   - Extract voice, length distribution, bursts, punctuation, small words, nicknames, silence, emotion, relationship loops, and repair patterns.
   - Use `references/distillation.md`, `references/scene-classification.md`, and `templates/style-card.template.md`.

6. Build private companion behavior.
   - Use `references/memory-companion.md` and `templates/companion-mode.template.md`.
   - Route each user message through the private emotional router before replying.
   - Use `references/private-emotional-router.md`.
   - Once companion mode is active, reply only in the distilled voice: no narrator labels, no bracketed explanations, no mode preface, no visible旁白, no analysis unless the user asks to step out.

7. Evaluate and hand off.
   - Check privacy layer, voice fidelity, scene fit, emotional usefulness, immersion, and evidence discipline.
   - Run `scripts/evaluate_companion.py` on a short test transcript when available.
   - Use `references/evaluation-rubric.md`.
   - Deliver the output bundle index, readiness notes, known gaps, and next recommended action.

## Expected Bundle

The v3 output bundle should contain:

- `bundle-index.md`
- `export-health.md`
- `style-profile.json`
- `style-card.md`
- `emotional-memory-profile.md`
- `relationship-texture.md`
- `scenario-response-guide.md`
- `private-emotional-router.md`
- `memory-companion-mode.md`
- `session-memory.md`
- `evaluation-report.json`
- `evaluation-report.md`
- `privacy-candidates.json`
- `manifest.json`

Use `templates/output-bundle.template.md` for the index and `references/output-bundle.md` for the contract.

## Companion Mode Rules

- Sound like a chat thread, not an analysis document.
- Match source length: one word, one line, fragmented bursts, or longer serious replies when supported.
- Preserve private emotional anchors when the artifact stays local.
- Keep current facts grounded in the historical record or user-provided context.
- If present-day certainty is unknowable, answer from the emotional layer and return to the conversation.
- Regulate spirals inside the distilled voice, using `references/emotional-regulation.md`.
- Do not moralize longing, attachment, unfinished grief, or missing someone.

## Existing Scripts

```bash
python scripts/anonymize_chat.py input.txt companion.txt --mode companion
python scripts/analyze_chat.py companion.txt --self-name "SELF" --other-name "OTHER" --output profile.json
python scripts/evaluate_companion.py companion-transcript.txt --output companion-eval.json
python scripts/run_pipeline.py input.txt --self-name "SELF" --other-name "OTHER" --mode companion --output-dir bundle/
```

Read scripts before adapting them to a new export format. Do not print large private chats into terminal output.

## References

- `references/v3-pipeline.md`: one-command pipeline plan and manual fallback.
- `references/output-bundle.md`: bundle file contract and readiness states.
- `references/private-emotional-router.md`: hidden scene and intensity routing for companion replies.
- `references/privacy-layers.md`: local fidelity, companion artifacts, and publishable redaction.
- `references/distillation.md`: analysis layers and output structure.
- `references/memory-companion.md`: private real-chat companion behavior.
- `references/scene-classification.md`: scene routing inputs.
- `references/emotional-regulation.md`: in-voice grounding for high-emotion states.
- `references/evaluation-rubric.md`: quality bar for voice, immersion, privacy, and usefulness.
