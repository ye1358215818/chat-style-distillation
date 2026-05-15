# v4 Local Pipeline Contract

This is the contract for the local relationship-memory companion pipeline.

## CLI Entrypoint

Use:

```bash
python scripts/run_pipeline.py input.txt --self-name "SELF" --other-name "OTHER" --mode companion --format auto --output-dir bundle/
```

`scripts/run_pipeline.py` is the public entrypoint. `scripts/distill_chat_pipeline.py` holds the implementation.

## Parser Formats

| Format | Expected Shape | Notes |
| --- | --- | --- |
| `auto` | Choose from file extension and content shape | Default for normal use. |
| `timestamp-text` | Records beginning with `[YYYY-MM-DD HH:MM]` or `[YYYY-MM-DD HH:MM:SS]` | The first content line may be `Speaker: message`; `--self-name` maps that speaker to `SELF`. |
| `wechat-text` | WeChat block text such as `YYYY-MM-DD HH:MM:SS Speaker` followed by message lines | Best for raw text exports that do not use bracketed timestamps. |
| `wechat-txt` | Alias for `wechat-text` | Kept for compatibility with earlier docs and scripts. |
| `json` | A list of message objects, or an object with `messages`, `data`, `records`, or `items` | Timestamp keys: `timestamp`, `time`, `createTime`; speaker keys: `speaker`, `sender`, `from`; text keys: `content`, `text`, `message`. |
| `csv` | Header row with timestamp/time, speaker/sender/from, content/text/message | Multiline CSV fields are supported. |
| `html` | Message nodes with `class="message"`, `data-time`, `data-speaker`, and content spans | Useful for simple HTML exports or browser-saved chat logs. |

If parsing yields no messages, stop and fix the input shape before distilling.

## Privacy Defaults

- Default mode is `companion`.
- `companion` removes hard identifiers and keeps non-identifying emotional anchors for local private use.
- `publish` is required for anything leaving the local machine and should be followed by manual review of `privacy-candidates.json`.
- Raw exports, `sanitized-chat.txt`, and session notes are not publishable artifacts.

## Pipeline Stages

1. Ingest
   - Record source hash, parser format, parse warnings, and basic row/message counts.
   - Never print raw chat content by default.

2. Privacy
   - Apply `companion` or `publish`.
   - Write `sanitized-chat.txt`, `privacy-candidates.json`, and redaction counts in `manifest.json`.

3. Export health
   - Count messages, speakers, first and last timestamp, media/system rows when detectable, burst behavior, response latency, parse warnings, and missing-looking ranges.
   - Write `analysis-summary.json` and `export-health.md`.

4. Structured profile
   - Write `style-profile.json` following `references/style-profile.schema.json`.
   - Separate observed patterns, cautious inferences, and unknowns.

5. Relationship-memory artifacts
   - Write `style-card.md`.
   - Write `emotional-memory-profile.md` from `templates/emotional-memory-profile.template.md`.
   - Write `relationship-texture.md` from `templates/relationship-texture.template.md`.
   - Write `scenario-response-guide.md` from `templates/scenario-response-guide.template.md`.
   - Write `private-emotional-router.md` as internal routing guidance.
   - Write `memory-companion-mode.md` and `session-memory.md`.

6. Evaluation
   - Check immersion, no visible narrator text, no visible scene/router labels, generic romance drift, therapy-speak drift, privacy fit, scene fit, and length distribution.
   - Write `evaluation-report.json` and `evaluation-report.md`.

7. Bundle assembly
   - Write `bundle-index.md` from `templates/output-bundle.template.md`.
   - Mark readiness from the health and evaluation signals.

## Readiness From Health

- `draft`: artifacts exist, but voice, privacy, and scene coverage have not been reviewed.
- `review-needed`: any health or safety input is unresolved, including parse warnings, too few messages, severe speaker imbalance, unknown date range, suspected export gaps, privacy candidates, missing key scenes, generic examples, visible router labels, or evaluation warnings.
- `ready-for-private-companion`: export health is acceptable, privacy candidates were reviewed, key scenes are covered, examples are paraphrased, active chat has no visible labels or method explanations, and the user accepts known gaps.

Readiness is for private local companion use only. It never means publishable.

## Manual Fallback

If a custom export format needs manual handling, run substeps and assemble the same bundle shape:

```bash
python scripts/anonymize_chat.py input.txt companion.txt --mode companion --audit-output privacy-candidates.json
python scripts/analyze_chat.py companion.txt --self-name "SELF" --other-name "OTHER" --format auto --output analysis-summary.json
python scripts/evaluate_companion.py companion-transcript.txt --output companion-eval.json
```

Then write the Markdown artifacts with `references/output-bundle.md` and `templates/`.

## Non-Goals

- Do not generate public examples from raw private logs.
- Do not treat one command as permission to skip authorization checks.
- Do not replace human review for emotional fidelity.
- Do not show router labels, scene labels, analysis notes, or safety explanations inside active companion chat.
