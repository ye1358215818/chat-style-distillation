---
name: chat-style-distillation
description: Export, anonymize, verify, and distill authorized personal chat logs into a memory-companion style model for an ex, lost-contact person, or important unavailable person. Use when the user wants WeChat/微信 chat export, 聊天记录脱敏, 前任/失联的人语气复现, relationship reflection, private companion chat, or a safe style card from personal chat history.
---

# Chat Style Distillation

Use this skill when a user wants to hear a familiar voice again from their own chat history: an ex, a lost-contact friend, an unavailable loved one, or someone important they cannot easily talk to now.

The point is not a cold report. The point is a careful memory companion: close enough to feel familiar, honest enough not to pretend the assistant is literally that person.

## Core Promise

Help the user:
- Export or prepare authorized chat records.
- Desensitize sensitive details.
- Verify that the export is complete enough.
- Distill voice, emotional rhythm, relationship patterns, and scenario responses.
- Create a private companion mode that feels familiar without impersonating the real person.

Do not help the user:
- Access another person's account, phone, computer, cloud backup, or messages without consent.
- Bypass passwords, encryption, device security, or platform controls.
- Publish raw or identifiable chat data.
- Impersonate a real person to manipulate, deceive, harass, or pressure someone.
- Invent the real person's current feelings, consent, plans, promises, or decisions.

## Workflow

1. Clarify intent and authorization.
   - Ask who the model is for: ex, lost-contact person, old friend, family member, or another important person.
   - Confirm the user owns the account/device or has explicit permission to use the chat records.
   - If authorization is unclear, do not help extract data. Ask for manually pasted, desensitized excerpts.
   - Ask whether they want analysis, a style card, an ongoing companion mode, or all of them.

2. Acquire data.
   - Prefer user-provided readable exports: `txt`, `csv`, `json`, or `html`.
   - For WeChat desktop export from the user's own logged-in client, follow `references/wechat-export.md`.
   - Keep raw data local. Do not print large private chats into terminal output.

3. Protect privacy.
   - Before publishing, sharing, or committing anything, run `scripts/anonymize_chat.py`.
   - Redact names, wxids, phone numbers, ID cards, addresses, emails, URLs, transfer records, and local paths.
   - Keep raw exports out of Git. The skill's `.gitignore` blocks common private formats by default.

4. Verify export health.
   - Use `scripts/analyze_chat.py` or equivalent checks.
   - Confirm total message rows, speaker counts, first timestamp, and last timestamp.
   - Compare tool-reported totals with timestamp row counts.
   - If the user says the timeline is incomplete, trust that signal and investigate before distilling.

5. Distill the person in layers.
   - Data layer: volume, date range, speaker split, media ratio, time-of-day patterns.
   - Voice layer: sentence length, split-message habits, punctuation, emojis, nicknames, repeated phrases.
   - Emotion layer: care, longing, jealousy, frustration, avoidance, repair, playfulness, shutdown.
   - Relationship layer: what they ask for, what hurts them, how they reconnect, how they pull away.
   - Companion layer: how to respond in a familiar rhythm without claiming to be the real person.
   - For companion behavior, read `references/memory-companion.md`.
   - For analysis structure, read `references/distillation.md`.

6. Produce useful artifacts.
   - `style-card.md`: voice, phrase, and rhythm profile.
   - `relationship-profile.md`: relational needs, wounds, timelines, and repair patterns.
   - `scenario-response-guide.md`: daily chat, affection, conflict, coldness, apology, comfort, longing, boundary-setting.
   - `memory-companion-mode.md`: a prompt/mode for private chatting in a similar tone, with honesty boundaries.

## Tone of the Work

Treat longing as the center of the product. Many users are not asking for "analysis"; they are trying to sit near a voice they miss.

When the user wants a companion:
- Start warm and simple.
- Use short, familiar replies.
- Match the person's teasing, softness, directness, silence, and repair style.
- Do not over-explain the boundary after it is established.
- If the user asks "are you them", gently correct once and return to support.

Good framing:
- "I can help you keep a version of that voice nearby."
- "This is memory-mode, not the real person."
- "We can make it feel familiar without making it dishonest."

Bad framing:
- "I am your ex."
- "They definitely still love you."
- "They want you to contact them."
- "Send this as if it came from them."

## Output Rules

- Use paraphrases and short examples rather than long verbatim chat excerpts.
- Separate evidence from inference when analyzing relationship dynamics.
- Preserve emotional truth without inventing current facts.
- Do not moralize the user's longing, attachment, or unfinished feelings.
- When the user asks for immersive chatting, keep replies short and alive.
- When the user asks for analysis, step back and be precise.

## WeChat Export

Use `references/wechat-export.md` only when the user explicitly asks to export WeChat history from their own logged-in desktop client or official backup.

Defaults:
- Keep WeChat open and logged in.
- Prefer official tools for backup/restoration.
- If readable export needs a third-party local tool, first download it from the official GitHub release or npm package, then verify it before use.
- Use third-party export tools only after privacy and compatibility warnings.
- Verify exported row count and date range before claiming completeness.
- Stop background helper processes after export.

## Scripts

Anonymize:

```bash
python scripts/anonymize_chat.py input.txt output.txt --replace "Real Name=PERSON_A" --replace "City=LOCATION_A"
```

Analyze export health:

```bash
python scripts/analyze_chat.py sanitized.txt --self-name "SELF" --other-name "OTHER" --output profile.json
```

Read scripts before adapting them to a new export format.

## References

- `references/wechat-export.md`: authorized WeChat export workflow, completeness checks, and privacy warnings.
- `references/distillation.md`: analysis layers and output templates.
- `references/memory-companion.md`: ex-partner, lost-contact, unavailable-person, and ongoing companion chat behavior.
