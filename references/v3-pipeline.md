# v3 One-Command Pipeline

This is the contract for the one-command local pipeline.

## Goal

Turn authorized chat records into a private emotional companion bundle with one auditable command:

```bash
python scripts/run_pipeline.py input.txt --self-name "SELF" --other-name "OTHER" --mode companion --output-dir bundle/
```

The command should not flatten the emotional work into automation. It should automate repeatable steps, preserve evidence, and leave clear places for human review.

## Pipeline Stages

1. Ingest
   - Accept `txt`, `csv`, `json`, or `html`.
   - Record source type, file hash, row estimate, and parsing warnings.
   - Never print raw chat content by default.

2. Privacy
   - Apply `companion` or `publish` privacy mode.
   - Remove hard identifiers.
   - Preserve local emotional anchors in `companion` mode.
   - Produce `privacy-candidates.json` and redaction counts in `manifest.json`.

3. Export health
   - Count messages, speakers, first timestamp, last timestamp, media/system rows, burst behavior, and missing-looking ranges.
   - Produce `analysis-summary.json` and `export-health.md`.
   - Stop if the input is too incomplete for trustworthy distillation unless the user explicitly accepts the gap.

4. Analysis
   - Produce `style-profile.json` following `references/style-profile.schema.json`.
   - Separate observed patterns, cautious inferences, and unknowns.

5. Distillation
   - Produce the style card, emotional memory profile, relationship texture, scenario guide, private emotional router, and companion mode.
   - Use templates where available.
   - Keep examples paraphrased and source-shaped.

6. Evaluation
   - Check immersion, no visible旁白, generic romance drift, therapy-speak drift, privacy layer fit, scene fit, and length distribution.
   - Produce `evaluation-report.json` and `evaluation-report.md`.

7. Bundle assembly
   - Produce `bundle-index.md`.
   - Mark readiness as `draft`, `review-needed`, or `ready-for-private-companion`.
   - Link every artifact and list known gaps.

## Manual v3 Fallback

If a custom export format needs manual handling, agents can run the substeps and assemble the same bundle shape:

```bash
python scripts/anonymize_chat.py input.txt companion.txt --mode companion --audit-output privacy-candidates.json
python scripts/analyze_chat.py companion.txt --self-name "SELF" --other-name "OTHER" --output style-profile.json
python scripts/evaluate_companion.py companion-transcript.txt --output companion-eval.json
```

Then write the Markdown artifacts by following `references/output-bundle.md` and the templates.

## Non-Goals

- Do not generate public examples from raw private logs.
- Do not treat one command as permission to skip authorization checks.
- Do not replace human review for emotional fidelity.
- Do not show router labels, analysis notes, or safety explanations inside active companion chat.
