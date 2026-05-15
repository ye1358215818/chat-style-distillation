# v5 Evidence-Grounded Companion Pipeline

This is the contract for the local relationship-memory companion pipeline.

v5 upgrades the bundle from "generated memory artifacts" to "evidence-grounded companion artifacts": every major claim should have paraphrased evidence, every evaluation scene can produce a deterministic test reply, and readiness comes from one shared gate.

## CLI Entrypoints

Use any of these:

```bash
python scripts/run_pipeline.py input.txt --self-name "SELF" --other-name "OTHER" --mode companion --format auto --output-dir bundle/ --generate-eval-replies
python -m chat_style_distillation.cli run input.txt --output-dir bundle/ --self-name "SELF" --other-name "OTHER"
chat-style-distill run input.txt --output-dir bundle/ --self-name "SELF" --other-name "OTHER"
```

`scripts/run_pipeline.py` remains the compatibility entrypoint. `src/chat_style_distillation/pipeline.py` owns implementation logic.

## v5 Options

| Option | Purpose |
| --- | --- |
| `--expected-start YYYY-MM-DD` | Expected earliest coverage date for gap detection. |
| `--expected-end YYYY-MM-DD` | Expected latest coverage date for gap detection. |
| `--min-messages N` | Minimum useful message count for this relationship and export. |
| `--relationship-mode ex|lost-contact|friend|family|other` | Context for health/readiness wording and future tuning. |
| `--locale zh-CN|en-US` | Output locale preference; default is `zh-CN`. |
| `--evidence-limit N` | Maximum evidence windows retained per scene. |
| `--generate-eval-replies` | Generate deterministic scenario replies into `evaluation-transcript.json`. |
| `--publish-redact-names` | In publish mode, redact `--self-name` and `--other-name` as strong identifiers. |

## Parser Formats

| Format | Expected Shape | Notes |
| --- | --- | --- |
| `auto` | Content sniffing before extension fallback | Detects JSON, CSV headers, HTML message nodes, bracket timestamps, and WeChat blocks. |
| `timestamp-text` | Records beginning with `[YYYY-MM-DD HH:MM]` or `[YYYY-MM-DD HH:MM:SS]` | The first content line may be `Speaker: message`; `--self-name` maps that speaker to `SELF`. |
| `wechat-text` | WeChat block text such as `YYYY-MM-DD HH:MM:SS Speaker` followed by message lines | Best for raw text exports that do not use bracketed timestamps. |
| `wechat-txt` | Alias for `wechat-text` | Kept for compatibility. |
| `json` | A list of message objects, or an object with `messages`, `data`, `records`, or `items` | Timestamp keys: `timestamp`, `time`, `createTime`; speaker keys: `speaker`, `sender`, `from`; text keys: `content`, `text`, `message`. |
| `csv` | Header row with timestamp/time, speaker/sender/from, content/text/message | Multiline CSV fields are supported. |
| `html` | Message nodes with `class="message"`, `data-time`, `data-speaker`, and content spans | Useful for simple HTML exports or browser-saved logs. |

If parsing yields no messages, stop and fix the input shape before distilling.

## Pipeline Stages

1. Ingest
   - Record source basename, hash, parser format, parse warnings, and message counts.
   - Never record the full local source path in `manifest.json`.

2. Privacy
   - Apply `companion` or `publish`.
   - Write `sanitized-chat.txt`, `privacy-candidates.json`, and redaction counts.
   - In publish mode, `--publish-redact-names` treats `--self-name` and `--other-name` as strong identifiers.

3. Health
   - Count messages, speakers, date range, media/system rows, duplicate-looking rows, out-of-order rows, and long gaps.
   - Use `--expected-start`, `--expected-end`, and `--min-messages` instead of hard-coded assumptions.
   - Write health into `analysis-summary.json` and `export-health.md`.

4. Evidence
   - Use `evidence.py` to extract scene-specific context windows from parsed messages.
   - Write `evidence-map.json` with scene, count, time range, hash, confidence, signals, and paraphrase.
   - Do not expose raw source text in evidence artifacts.

5. Structured profile
   - Write `style-profile.json` following `references/style-profile.schema.json`.
   - Include `evidence_refs`, `scene_evidence`, `paraphrased_examples`, and `coverage_gaps`.
   - Separate observed patterns, cautious inferences, and unknowns.

6. Relationship-memory artifacts
   - Write `style-card.md`, `emotional-memory-profile.md`, `relationship-texture.md`, `scenario-response-guide.md`, `private-emotional-router.md`, `memory-companion-mode.md`, and `session-memory.md`.
   - Markdown should read like a relationship memory map, not a clinical report.

7. Reply simulation and evaluation
   - Load `assets/evaluation-prompts.json`.
   - If `--generate-eval-replies` is set, write deterministic candidate replies to `evaluation-transcript.json`.
   - Evaluate actual generated replies when present; otherwise evaluate `memory-companion-mode.md` as a fallback.
   - Score source phrase fit, reply shape fit, scene move fit, visible router leakage, generic romance drift, therapy-speak drift, and length drift.

8. Readiness
   - Use `readiness.py` as the only source of `bundle-index.md` readiness.
   - Write `readiness-report.json`.
   - `ready-for-private-companion` requires no severe health issue, no unresolved privacy candidate, sufficient core scene coverage, and no visible label/method narration.

9. Bundle assembly
   - Write `bundle-index.md`, `manifest.json`, and `session-memory.schema.json`.
   - Include known gaps and a concrete next action.

## Readiness States

- `draft`: artifacts exist, but evidence coverage or evaluation still has non-blocking gaps.
- `review-needed`: health, privacy, coverage, or evaluation has a blocking issue.
- `ready-for-private-companion`: private local companion use is reasonable after review.

Readiness never means publishable. Publishing requires `--mode publish`, name redaction when appropriate, and manual review.

## Manual Fallback

If a custom export format needs manual handling, keep the same bundle contract:

```bash
python scripts/anonymize_chat.py input.txt companion.txt --mode companion --audit-output privacy-candidates.json
python scripts/analyze_chat.py companion.txt --self-name "SELF" --other-name "OTHER" --format auto --output analysis-summary.json
python scripts/evaluate_companion.py companion-transcript.txt --output companion-eval.json
```

Then assemble artifacts using `references/output-bundle.md`, `templates/`, and the schema files.

## Non-Goals

- Do not generate public examples from raw private logs.
- Do not treat one command as permission to skip authorization checks.
- Do not replace human review for emotional fidelity.
- Do not show router labels, scene labels, analysis notes, or method explanations inside active companion chat.
