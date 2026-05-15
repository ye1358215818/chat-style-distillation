# Output Bundle Contract

The v5 output bundle is the handoff unit for a private relationship-memory companion. It should tell the user what was processed, how healthy the export is, what evidence supports the profile, what privacy layer was used, what emotional-memory artifacts are available, how generated replies evaluated, and whether active companion chat is ready.

It should feel like a careful memory companion product, not a cold audit packet.

## Required Files

| File | Purpose |
| --- | --- |
| `bundle-index.md` | Entry point, parser format, privacy layer, readiness state, artifact links, next action |
| `export-health.md` | Message count, date range, speaker split, parse warnings, completeness notes |
| `analysis-summary.json` | Deterministic metrics, scene counts, burst behavior, latency, input format |
| `sanitized-chat.txt` | Local intermediate text after privacy processing; not for publishing |
| `privacy-candidates.json` | Remaining privacy candidates for manual review |
| `evidence-map.json` | Scene evidence windows with hashes, paraphrases, signals, counts, and time ranges |
| `style-profile.json` | Structured profile following `references/style-profile.schema.json` |
| `style-card.md` | Human-readable voice, rhythm, phrase, punctuation, silence, and anchor map |
| `emotional-memory-profile.md` | How the person expressed care, missing, hurt, jealousy, withdrawal, repair, softness |
| `relationship-texture.md` | Approach, distance, conflict loops, repair, unresolved tenderness, boundary notes |
| `scenario-response-guide.md` | Scene-specific response shapes, emotional moves, length choices, evidence notes |
| `private-emotional-router.md` | Hidden routing rules for scene, intensity, action risk, reality risk, and reply shape |
| `memory-companion-mode.md` | Activation contract and active in-chat behavior |
| `session-memory.md` | Ongoing user-care memory, separate from source voice |
| `evaluation-transcript.json` | Evaluation prompts, deterministic generated replies, expected shapes, scores, and warnings |
| `evaluation-report.json` | Machine-readable fidelity, immersion, privacy, usefulness, and drift checks |
| `evaluation-report.md` | Human-readable evaluation summary |
| `readiness-report.json` | Unified readiness state, blocking issues, warnings, and next action |
| `session-memory.schema.json` | Schema separating source relationship memory from current user-state memory |
| `manifest.json` | Source hash, parser format, date range, privacy mode, redaction counts, artifact list |

## Readiness States

Readiness must come from `readiness.py`, not optimism or a single artifact.

- `draft`: artifacts exist, but evidence coverage or evaluation has non-blocking gaps.
- `review-needed`: data health, parser warnings, privacy candidates, scene coverage, evidence discipline, or evaluation has blocking gaps.
- `ready-for-private-companion`: private local use is reasonable after review; export health is acceptable, privacy candidates are handled, core scenes are covered, and active chat has no visible narrator, method, scene, intensity, or router labels.

None of these readiness states means publishable. Publishing requires `--mode publish` plus separate manual review.

## Health Inputs For Readiness

Use these signals when choosing the state:

- Total messages and target-speaker message count.
- Date range and known missing ranges.
- Speaker split and speaker mapping confidence.
- Parser format and parse warnings.
- Scene coverage for daily, missing, comfort, conflict, apology, coldness, repair, impulse, and certainty-seeking.
- Evidence map coverage, hash references, and paraphrased examples.
- Privacy candidates and redaction counts.
- Evaluation transcript warnings for visible labels, narrator text, generic romance, therapy-speak drift, source phrase mismatch, scene move mismatch, and length drift.
- Human review notes on whether the voice feels specific rather than generic.

## Bundle Index Requirements

Use `templates/output-bundle.template.md`.

The index should include:

- Input summary without raw chat excerpts.
- Parser format and parse warnings.
- Privacy mode, anchors retained, and whether publishing is allowed.
- Export health summary.
- Companion readiness state from `readiness-report.json` and why.
- Links to artifacts.
- Known gaps and suggested next action.

## Artifact Writing Requirements

- `emotional-memory-profile.md` should read like an emotional memory map, not a personality diagnosis.
- `relationship-texture.md` should preserve closeness, friction, unfinished tenderness, repair habits, and boundaries.
- `scenario-response-guide.md` should help the companion choose reply shape without exposing scene labels to the user.
- `session-memory.md` should track what helps the user now and must not rewrite the source voice.
- `evidence-map.json` should use hashes and paraphrases, never raw private message text.
- Examples should be paraphrased and source-shaped; do not copy raw private messages into publishable docs.

## Privacy Rule

A bundle can be emotionally rich and still private. For local companion use, preserve anchors that make the voice feel real. For publishing, remove or generalize names, accounts, locations, identifiers, raw examples, screenshots, and session notes.

Never mark a bundle publishable just because hard identifiers were removed. Emotional anchors can still identify people.

## Companion Use Rule

When `memory-companion-mode.md` is activated, the assistant should not expose bundle mechanics. The user should see a natural chat reply, not labels such as scene, intensity, router decision, privacy layer, readiness state, or evaluation status.
