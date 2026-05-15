# Output Bundle Contract

The output bundle is the handoff unit for v3. It should let a user understand what was processed, what is safe to use privately, what should not be published, and how to enter companion mode without losing the emotional texture.

## Required Files

| File | Purpose |
| --- | --- |
| `bundle-index.md` | Entry point, readiness state, artifact links, next action |
| `export-health.md` | Message count, date range, speaker split, completeness notes |
| `analysis-summary.json` | Deterministic metrics, scene counts, burst behavior, latency |
| `privacy-candidates.json` | Remaining privacy candidates for review |
| `style-profile.json` | Structured profile following `references/style-profile.schema.json` |
| `style-card.md` | Human-readable voice, rhythm, phrase, punctuation, and silence map |
| `emotional-memory-profile.md` | Care, missing, hurt, jealousy, withdrawal, repair, softness |
| `relationship-texture.md` | Approach, distance, conflict loops, repair, unresolved tenderness |
| `scenario-response-guide.md` | Scene-specific response shapes and evidence notes |
| `private-emotional-router.md` | Hidden routing rules for scene, intensity, and reply length |
| `memory-companion-mode.md` | Activation contract and in-chat behavior |
| `session-memory.md` | Optional ongoing user-care memory, separate from source voice |
| `evaluation-report.json` | Machine-readable fidelity, immersion, privacy, usefulness, and drift checks |
| `evaluation-report.md` | Human-readable evaluation summary |
| `manifest.json` | Source hash, date range, privacy mode, redaction counts, artifact list |

## Readiness States

- `draft`: artifacts exist but need human voice review.
- `review-needed`: data health, privacy, or scene coverage has unresolved gaps.
- `ready-for-private-companion`: private use is reasonable after review; not automatically safe for publishing.

## Bundle Index Requirements

Use `templates/output-bundle.template.md`.

The index should include:

- Input summary without raw chat excerpts.
- Privacy layer and whether publishing is allowed.
- Export health summary.
- Companion readiness state.
- Links to artifacts.
- Known gaps and suggested next step.

## Privacy Rule

A bundle can be emotionally rich and still private. For local companion use, preserve anchors that make the voice feel real. For publishing, remove or generalize names, accounts, locations, identifiers, raw examples, and session notes.

Never mark a bundle publishable just because hard identifiers were removed. Emotional anchors can still identify people.

## Companion Use Rule

When `memory-companion-mode.md` is activated, the assistant should not expose bundle mechanics. The user should see a natural chat reply, not labels such as scene, intensity, router decision, privacy layer, or evaluation status.
