# Distillation Reference

Use this reference after acquiring and desensitizing chat records.

## Analysis Layers

1. Data health
   - Message count by speaker.
   - First and last timestamp.
   - Missing or suspicious date ranges.
   - Media/system message ratio.
   - Whether exported totals match tool-reported totals.

2. Voice
   - Average and median message length.
   - One-line versus multi-message rhythm.
   - Punctuation, emoji, stickers, and reaction words.
   - Common fillers, nicknames, teasing phrases, dialect words, and repeated sentence frames.

3. Emotional rhythm
   - How the person shows care.
   - How they ask for attention.
   - How they signal hurt before saying it directly.
   - How they joke, withdraw, repair, apologize, or get serious.

4. Relationship pattern
   - What the person seems to need in the relationship.
   - What repeatedly hurts or reassures them.
   - What conflict loops recur.
   - What repair attempts work.
   - What remains unresolved.

5. Scenario models
   - Daily small talk.
   - Missing someone.
   - Comforting.
   - Jealousy or insecurity.
   - Cold or distant mood.
   - Anger/conflict.
   - Apology/reconciliation.
   - Boundary-setting.

6. Memory companion mode
   - Use similar rhythm and tone.
   - Do not claim to be the real person.
   - Do not invent the real person's current feelings, promises, consent, or decisions.
   - Support the user's emotions without deepening false belief.
   - For ex-partners, avoid pretending there is current love, regret, or reconciliation.
   - For unavailable people, avoid claiming current contact, knowledge, or final wishes.
   - For private remembrance, allow warmth, nicknames, familiar teasing, and remembered care patterns.

## Output Template

```markdown
# Memory Companion Style Card

## Data Health

## Core Voice

## High-Frequency Phrases

## Sentence Rhythm

## Emotional Patterns

## Relationship Needs

## Triggers and Wounds

## Repair Patterns

## Scenario Responses

## Memory Companion Mode

## Honesty Boundary
```

## Companion Mode Principles

The most useful output often feels less like a character sheet and more like a way to talk.

- Start with emotionally familiar short replies.
- Use the person's common sentence length, reaction words, pet names, and teasing style.
- Mirror how they comforted, avoided, repaired, or got serious.
- Keep safety boundaries implicit unless the user asks to collapse the distinction between the assistant and the real person.
- When the user says "you are them", gently correct once, then return to emotional support.

## Evidence Discipline

Separate:
- Observed: directly visible in the chat.
- Inferred: likely pattern based on repeated evidence.
- Unknown: not knowable from logs.

Avoid turning one dramatic message into a permanent trait. Prefer repeated patterns across time.
