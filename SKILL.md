---
name: chat-style-distillation
description: Export, anonymize, verify, and distill authorized WeChat or personal chat logs into a private relationship-memory companion bundle. Use when the user wants WeChat chat export, chat anonymization, ex/lost-contact voice distillation, relationship reflection, emotional memory artifacts, scenario response guides, output bundles, or active private companion chat with no visible router labels.
---

# Chat Style Distillation

Use this skill to turn authorized chat history into a private relationship-memory companion: a bundle that preserves how a person sounded, cared, withdrew, repaired, teased, missed, and stayed silent.

The output should feel like a warm memory handoff for future chat, not a cold report.

## Workflow

1. Confirm scope and permission.
   - Work only with records the user owns or is explicitly allowed to process.
   - Keep raw exports, databases, screenshots, voice files, and full transcripts local and out of Git.
   - Ask whether the user needs export help, a one-command bundle, bundle review, or active companion chat.

2. Prepare input and choose parser format.
   - Prefer readable `txt`, `json`, `csv`, or `html`; normalize custom formats before distillation.
   - For WeChat desktop export, use `references/wechat-export.md`; if incomplete, use `references/wechat-compatibility.md`.
   - CLI formats: `auto`, `timestamp-text`, `wechat-text`, `wechat-txt`, `json`, `csv`, `html`. See `references/v4-pipeline.md`.

3. Run the local pipeline.
   - Use `python scripts/run_pipeline.py input.txt --self-name "SELF" --other-name "OTHER" --mode companion --format auto --output-dir bundle/`.
   - `scripts/run_pipeline.py` is the public entrypoint; `scripts/distill_chat_pipeline.py` is the implementation target.
   - Default to `--mode companion` for private local use. Use `--mode publish` only for material that may leave the machine.

4. Check health and readiness before style claims.
   - Read `export-health.md`, `analysis-summary.json`, `privacy-candidates.json`, `evaluation-report.*`, and `manifest.json`.
   - Readiness comes from health: `draft`, `review-needed`, or `ready-for-private-companion`.
   - Do not mark anything publishable by default. Publishing requires `publish` mode plus manual privacy review.

5. Build the relationship-memory artifacts.
   - Required human-facing artifacts: `style-card.md`, `emotional-memory-profile.md`, `relationship-texture.md`, `scenario-response-guide.md`, `private-emotional-router.md`, `memory-companion-mode.md`, and `session-memory.md`.
   - Use the templates in `templates/` and the contracts in `references/output-bundle.md`.
   - Separate observed evidence, cautious inference, and unknowns.

6. Activate companion chat only when requested.
   - Route privately through `references/private-emotional-router.md`.
   - The visible reply must be only the distilled voice: no narrator label, no scene/intensity/router labels, no method explanation, no mode preface, and no analysis unless the user asks to step out.
   - Use `references/memory-companion.md` and `references/emotional-regulation.md` for high-emotion moments.

7. Evaluate and hand off.
   - Check voice fidelity, scene fit, emotional usefulness, privacy fit, immersion, and drift.
   - Run `scripts/evaluate_companion.py` on a short test transcript when available.
   - Hand off the bundle index, readiness state, known gaps, and next action.

## Expected Bundle

- `bundle-index.md`
- `export-health.md`
- `analysis-summary.json`
- `sanitized-chat.txt`
- `privacy-candidates.json`
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
- `manifest.json`

Do not print large private chats into terminal output. Read scripts before adapting them to a new export format.

## References

- `references/v4-pipeline.md`: CLI entrypoint, parser formats, pipeline stages, readiness gates.
- `references/output-bundle.md`: bundle contract and required artifacts.
- `references/privacy-layers.md`: local source, companion artifact, and publishable redaction defaults.
- `references/distillation.md`: relationship-memory analysis layers.
- `references/private-emotional-router.md`: hidden routing for active companion replies.
- `references/memory-companion.md`: active private companion behavior.
- `references/scene-classification.md`: scene inputs and reply-shape selection.
- `references/emotional-regulation.md`: in-voice grounding for high-emotion states.
- `references/evaluation-rubric.md`: quality bar before ongoing use.
