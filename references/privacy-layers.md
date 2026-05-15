# Privacy Layers

Use layered privacy instead of one-size-fits-all anonymization. The default for this skill is private local companion work: keep the companion emotionally real while keeping publishable material clean.

## Three Layers

| Layer | Use Case | Privacy Posture | Emotional Fidelity |
| --- | --- | --- | --- |
| Local source | Raw export on the user's own machine | Keep private, do not commit or upload | Full fidelity |
| Companion artifact | Private style card and companion mode | Remove hard identifiers, keep emotional anchors | High fidelity |
| Published sample | GitHub, docs, examples, screenshots, shared files | Strong redaction | Low to medium fidelity |

## Emotional Anchors To Preserve In Private Companion Work

Keep these when the artifact stays private and local:

- Pet names and relationship nicknames.
- Inside jokes and repeated phrases.
- Shared place nicknames such as "楼下那家店" or "老地方".
- Anniversaries or emotionally important dates when they matter to the relationship.
- Pet names, song names, game names, food habits, bedtime rituals, and recurring small promises from the historical record.
- The way the person refers to the user, themselves, conflicts, apologies, and comfort.

These details are often where immersion lives. Replacing all of them with `PERSON_A` or `LOCATION_A` can make the companion feel hollow.

## Hard Identifiers To Remove Or Generalize

Remove these from companion artifacts and always remove them from published material:

- wxid, phone number, email, ID card number, exact address, local filesystem path.
- Full account identifiers, QR codes, URLs with personal tokens, database paths.
- Screenshots, voice files, raw images, and exported databases.
- Names of uninvolved third parties when they are not emotionally necessary.

## Natural Generalization

For private companion artifacts, prefer natural memory language over sterile placeholders:

| Raw Detail Type | Better Private Artifact Wording |
| --- | --- |
| Exact address | "你们以前常去的那个地方" |
| Third-party full name | "你以前总提到的那个朋友" |
| School/company full name | "那段上学/上班的日子" |
| URL or file path | "那张图/那个链接" |

The rule: keep the feeling, lower the identifiability.

## Script Modes

Default to `companion` for private local relationship-memory bundles:

```bash
python scripts/run_pipeline.py input.txt --mode companion --format auto --output-dir bundle/
```

Use `publish` for anything that may leave the local machine:

```bash
python scripts/anonymize_chat.py input.txt publish.txt --mode publish --replace "Real Name=PERSON_A" --audit-output audit.json
```

Use `companion` for manual private local companion work:

```bash
python scripts/anonymize_chat.py input.txt companion.txt --mode companion
```

`companion` keeps non-identifying emotional anchors by default and redacts hard identifiers. `publish` adds stronger redaction for public examples and repository material.

Review `--audit-output` before publishing. It lists possible remaining long numbers, dates, account-like numbers, and location-like phrases so a human can decide whether they are meaningful anchors or identifying details.
