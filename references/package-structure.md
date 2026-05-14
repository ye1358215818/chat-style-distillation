# Package Structure

This repository serves two audiences:

1. Codex agents that need concise operational instructions.
2. Humans browsing GitHub who need emotional context and usage guidance.

Keep those layers separate.

## Agent Layer

- `SKILL.md`: core trigger, workflow, and routing instructions.
- `references/`: deeper guidance loaded only when needed.
- `scripts/`: deterministic local tools for export health, privacy, and evaluation.
- `templates/`: output shapes for repeatable artifacts.

## Human Layer

- `README.md`: public explanation, emotional positioning, and quick usage.
- `assets/fake-sample.txt`: fake sample only.
- `LICENSE`: repository license.

## Maintenance Rules

- Keep `SKILL.md` concise and action-oriented.
- Put long emotional/product explanation in `README.md`.
- Put detailed operational rules in `references/`.
- Put repeatable output formats in `templates/`.
- Keep raw exports, real profiles, and session memory files out of the repository unless fully synthetic.
