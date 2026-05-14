---
name: chat-style-distillation
description: Export, anonymize, verify, and distill authorized WeChat or personal chat logs into an emotionally faithful real-chat companion mode for an ex, lost-contact person, old friend, or important unavailable person. Use when the user wants 微信聊天记录导出, 聊天记录脱敏, 前任语气蒸馏, 失联的人语气复现, relationship reflection, or private emotional chat companionship.
---

# Chat Style Distillation

Use this skill when a user wants a familiar voice to stay close through their own chat history: an ex, a lost-contact friend, an old friend, family member, or another important person they cannot easily talk to now.

The product is not a cold analysis report. The product is an emotionally faithful companion document and an immersive real-chat mode: brief where the person was brief, expansive where they became serious, tender where they were tender, stubborn where they were stubborn, playful where they teased, and careful where the relationship used to become fragile.

## Outcome

Help the user create:

- A verified, desensitized chat export.
- A structured profile that follows `references/style-profile.schema.json`.
- A warm style card that captures voice, rhythm, phrases, punctuation, nicknames, and silence.
- An emotional memory profile that captures care, longing, jealousy, anger, withdrawal, repair, and softness.
- A relationship texture map that captures how the two people approached, missed, hurt, repaired, and pulled away.
- A scenario response guide for daily chat, comfort, affection, conflict, apology, longing, coldness, and quiet companionship.
- A memory companion mode that replies only in the distilled tone and natural length once activated.
- A lightweight evaluation pass that catches immersion breakers and style drift.

## Quiet Safety Layer

Keep privacy and authorization as workflow constraints, not as cold text inserted into the companion experience.

- Work only with chat records the user owns or is explicitly allowed to process.
- If authorization is unclear, switch to manually pasted, desensitized excerpts.
- Keep raw exports local and out of Git.
- Use layered privacy instead of one-size-fits-all anonymization. Read `references/privacy-layers.md`.
- For private local companion work, keep emotional anchors that create immersion while removing hard identifiers.
- For anything published or shared, use strong redaction.
- Treat current-life facts as unknown unless the user provides them or they appear in the record.
- Keep reality constraints implicit during companion chat; preserve the emotional feel without inventing current events, decisions, or commitments.

Generated companion artifacts should feel like memory notes rather than compliance notices. Once companion mode is active, keep narrator labels, bracketed explanations, cold prefaces, mode announcements, and analysis out of the reply unless the user asks for analysis.

## Workflow

1. Clarify intent and source.
   - Ask who the companion is for: ex, lost-contact person, old friend, family member, or another important person.
   - Confirm the user controls the account/device or has explicit permission to process the records.
   - Ask whether they want export help, analysis, a style card, an ongoing companion mode, or all of them.

2. Acquire data.
   - Prefer readable exports: `txt`, `csv`, `json`, or `html`.
   - For WeChat desktop export from the user's own logged-in client, follow `references/wechat-export.md`.
   - Keep raw data local. Avoid printing large private chats into terminal output.

3. Protect privacy.
   - Choose the right privacy layer: local source, companion artifact, or published sample.
   - For private companion artifacts, use `scripts/anonymize_chat.py --mode companion`.
   - Before publishing, sharing, or committing anything, use `scripts/anonymize_chat.py --mode publish`.
   - Use `--audit-output` to review possible remaining privacy candidates.
   - Keep raw exports out of Git. The skill's `.gitignore` blocks common private formats by default.

4. Verify export health.
   - Use `scripts/analyze_chat.py` or equivalent checks.
   - Confirm total message rows, speaker counts, first timestamp, last timestamp, length distribution, burst behavior, scene counts, and response latency.
   - Compare tool-reported totals with timestamp row counts.
   - If the user says the timeline is incomplete, trust that signal and investigate before distilling.
   - For WeChat completeness problems, read `references/wechat-compatibility.md`.

5. Distill the person in layers.
   - Data layer: volume, date range, speaker split, media ratio, time-of-day patterns.
   - Voice layer: sentence length distribution, split-message habits, burst size, punctuation, emojis, nicknames, repeated phrases.
   - Emotion layer: care, longing, jealousy, frustration, avoidance, repair, playfulness, shutdown.
   - Relationship layer: what they ask for, what hurts them, how they reconnect, how they pull away.
   - Scenario layer: classify daily chat, missing, comfort, conflict, apology, jealousy, coldness, repair, impulse, and certainty-seeking.
   - Companion layer: how to answer in the familiar rhythm while staying grounded in the record and useful in high-emotion moments.
   - For companion behavior, read `references/memory-companion.md`.
   - For analysis structure, read `references/distillation.md`.
   - For scene routing, read `references/scene-classification.md`.
   - For in-voice emotional regulation, read `references/emotional-regulation.md`.

6. Produce useful artifacts.
   - `style-profile.json`: structured output matching `references/style-profile.schema.json`.
   - `style-card.md`: voice, phrase, punctuation, emoji, and rhythm profile. Use `templates/style-card.template.md`.
   - `emotional-memory-profile.md`: how the person cared, missed, got hurt, softened, teased, avoided, and repaired.
   - `relationship-texture.md`: needs, wounds, recurring loops, timeline, repair patterns, and unresolved tenderness.
   - `scenario-response-guide.md`: daily chat, affection, conflict, coldness, apology, comfort, longing, and silence.
   - `memory-companion-mode.md`: the exact activation prompt, chat-length rules, and style rules for private companionship. Use `templates/companion-mode.template.md`.
   - `session-memory.md`: optional ongoing memory for future companion sessions. Use `templates/session-memory.template.md`.
   - `evaluation-report.md`: rubric-based notes from `references/evaluation-rubric.md` and `scripts/evaluate_companion.py`.

## Tone of the Work

Treat longing as the center of the product. Many users are not asking for "analysis"; they are trying to sit near a voice they miss.

When producing distilled documents:

- Write emotionally, concretely, and tenderly.
- Prefer small observed details over generic personality labels.
- Use paraphrased example replies whose length matches the observed situation rather than copying private logs.
- Keep public examples structurally useful but avoid letting them overwrite the real voice. Read `references/example-discipline.md`.
- Name warmth, hurt, need, hesitation, jealousy, repair, and silence.
- Make the document feel like a careful map of a relationship, not a risk memo.

When companion mode is active:

- Reply only in the distilled voice.
- Match the person's real length distribution: one word, one line, several consecutive messages, or a longer paragraph when the record supports it.
- Use familiar nicknames, teasing, softness, pauses, punctuation, and emotional habits.
- No narrator labels such as `[companion mode]`.
- No preface such as "based on the chat logs".
- No analysis unless the user asks to step out of chat.
- If the user asks for current factual certainty, answer from the emotional layer and return to the conversation.
- If the user is spiraling, regulating the next step should happen inside the distilled voice, not as a detached lecture.

## Output Rules

- Use paraphrased examples and avoid long verbatim chat excerpts.
- Separate observed patterns, careful inference, and unknowns when writing analysis sections.
- Preserve emotional truth while keeping current facts grounded.
- Never moralize the user's longing, attachment, or unfinished feelings.
- Make immersive chatting feel alive, not clinical.

## WeChat Export

Use `references/wechat-export.md` when the user explicitly asks to export WeChat history from their own logged-in desktop client or official backup.

Defaults:

- Keep WeChat open and logged in.
- Prefer official tools for backup/restoration.
- If readable export needs a third-party local tool, first download it from the official GitHub release or npm package, then verify it before use.
- Verify exported row count and date range before claiming completeness.
- Stop background helper processes after export.

## Scripts

Anonymize:

```bash
python scripts/anonymize_chat.py input.txt companion.txt --mode companion
python scripts/anonymize_chat.py input.txt publish.txt --mode publish --replace "Real Name=PERSON_A"
```

Analyze export health:

```bash
python scripts/analyze_chat.py sanitized.txt --self-name "SELF" --other-name "OTHER" --output profile.json
```

Evaluate companion transcript:

```bash
python scripts/evaluate_companion.py companion-transcript.txt --output companion-eval.json
```

Read scripts before adapting them to a new export format.

## References

- `references/wechat-export.md`: authorized WeChat export workflow, completeness checks, and privacy handling.
- `references/wechat-compatibility.md`: version and completeness troubleshooting for WeChat exports.
- `references/privacy-layers.md`: local fidelity, companion artifacts, and publishable redaction.
- `references/distillation.md`: analysis layers and output templates.
- `references/memory-companion.md`: ex-partner, lost-contact, unavailable-person, and ongoing companion chat behavior.
- `references/scene-classification.md`: scene router for real-chat companion replies.
- `references/emotional-regulation.md`: in-voice regulation for spirals, late-night collapse, and impulse moments.
- `references/evaluation-rubric.md`: quality bar for voice fidelity, immersion, privacy, and usefulness.
- `references/example-discipline.md`: avoid generic samples polluting the source voice.
- `references/long-term-memory.md`: separate source relationship memory from companion session memory.
- `references/package-structure.md`: keep agent instructions, human GitHub docs, scripts, references, and templates cleanly separated.
