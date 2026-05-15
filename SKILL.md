---
name: chat-style-distillation
description: Export, anonymize, verify, and distill authorized WeChat or personal chat logs into an evidence-grounded private relationship-memory companion bundle. Use when the user wants WeChat chat export, chat anonymization, ex/lost-contact voice distillation, relationship reflection, emotional memory artifacts, scenario response guides, readiness review, or active private companion chat with no visible router labels.
---

# Chat Style Distillation

Use this skill to turn authorized chat history into a private relationship-memory companion bundle. The bundle should preserve how a person sounded, cared, withdrew, repaired, teased, missed, and stayed silent, while grounding claims in paraphrased evidence.

## Workflow

1. Confirm scope and permission.
   - Work only with records the user owns or is explicitly allowed to process.
   - Keep raw exports, databases, screenshots, voice files, full transcripts, and generated private bundles local and out of Git.
   - Ask whether the user needs export help, a one-command bundle, bundle review, or active companion chat.

2. Prepare input and parser format.
   - Prefer readable `txt`, `json`, `csv`, or `html`.
   - For WeChat desktop export, use `references/wechat-export.md`; if incomplete, use `references/wechat-compatibility.md`.
   - CLI formats: `auto`, `timestamp-text`, `wechat-text`, `wechat-txt`, `json`, `csv`, `html`. `auto` sniffs content shape before falling back to extension.

3. Run the v5 local pipeline.
   - Use `python scripts/run_pipeline.py input.txt --self-name "SELF" --other-name "OTHER" --mode companion --format auto --output-dir bundle/ --generate-eval-replies`.
   - Optional gates: `--expected-start`, `--expected-end`, `--min-messages`, `--relationship-mode`, `--locale`, `--evidence-limit`.
   - Default to `--mode companion` for private local use. Use `--mode publish --publish-redact-names` for anything that may leave the machine.

4. Review evidence and readiness.
   - Read `export-health.md`, `evidence-map.json`, `privacy-candidates.json`, `evaluation-transcript.json`, `evaluation-report.*`, `readiness-report.json`, and `manifest.json`.
   - Readiness comes only from `readiness.py`: `draft`, `review-needed`, or `ready-for-private-companion`.
   - Do not treat readiness as publishability.

5. Use the relationship-memory artifacts.
   - Required human-facing artifacts: `style-card.md`, `emotional-memory-profile.md`, `relationship-texture.md`, `scenario-response-guide.md`, `private-emotional-router.md`, `memory-companion-mode.md`, and `session-memory.md`.
   - Use `references/output-bundle.md` for artifact contract and `references/v5-pipeline.md` for pipeline details.
   - Separate observed evidence, cautious inference, and unknowns. Do not copy raw private messages into public docs.

6. Activate companion chat only when requested.
   - Route privately through `private-emotional-router.md`.
   - The visible reply must be only the distilled voice: no narrator label, no scene/intensity/router labels, no method explanation, no mode preface, and no analysis unless the user asks to step out.
   - Match reply length to the distilled profile: short when the source is short, longer when the source becomes specific and careful.

7. Evaluate and hand off.
   - Check source phrase fit, reply shape fit, scene move fit, visible router leakage, generic romance drift, therapy-speak drift, and length drift.
   - Hand off the bundle index, readiness state, known gaps, next action, and any manual review items.

## Expected Bundle

- `bundle-index.md`
- `sanitized-chat.txt`
- `privacy-candidates.json`
- `evidence-map.json`
- `analysis-summary.json`
- `style-profile.json`
- `export-health.md`
- `style-card.md`
- `emotional-memory-profile.md`
- `relationship-texture.md`
- `scenario-response-guide.md`
- `private-emotional-router.md`
- `memory-companion-mode.md`
- `session-memory.md`
- `evaluation-transcript.json`
- `evaluation-report.json`
- `evaluation-report.md`
- `readiness-report.json`
- `session-memory.schema.json`
- `manifest.json`

Do not print large private chats into terminal output. Read scripts before adapting them to a new export format.

## References

- `references/v5-pipeline.md`: CLI entrypoints, parser formats, evidence chain, evaluation transcript, readiness gates.
- `references/output-bundle.md`: bundle contract and required artifacts.
- `references/privacy-layers.md`: local source, companion artifact, and publishable redaction defaults.
- `references/distillation.md`: relationship-memory analysis layers.
- `references/private-emotional-router.md`: hidden routing for active companion replies.
- `references/memory-companion.md`: active private companion behavior.
- `references/scene-classification.md`: scene inputs and reply-shape selection.
- `references/emotional-regulation.md`: in-voice grounding for high-emotion states.
- `references/evaluation-rubric.md`: quality bar before ongoing use.
