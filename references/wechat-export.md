# WeChat Export Reference

Use this reference only for authorized exports from the user's own logged-in WeChat desktop client or from backups the user created from their own account/device.

Do not use this workflow to access someone else's messages, shared computers, unattended sessions, or accounts the user cannot prove they control.

If export completeness or version support is unclear, also read `references/wechat-compatibility.md`.

## Decision Tree

1. User already has a readable export.
   - Use it directly.
   - Desensitize before analysis.

2. User has official WeChat PC backup files.
   - Treat these as restore-oriented backups, not guaranteed readable text exports.
   - Backup folders may contain `Backup/.../files/.../ChatPackage`, `Index`, `Media`, `pkg_info.dat`, or `tar_index.dat`.
   - These can prove date coverage but may remain encrypted and not directly parseable on PC.
   - Prefer restoring through official WeChat if the user needs the messages visible again.

3. User has desktop WeChat currently logged in with visible history.
   - Use a local export tool only with explicit consent and risk warning.
   - First acquire the tool from an official source, then verify it.
   - Keep everything local.
   - Do not upload database files or chat logs to websites or strangers.

## Safe Third-Party Tool Rules

- Prefer open-source tools with official GitHub/npm releases.
- Avoid random cloud-drive packages, reposted executables, and "remote recovery" services.
- Download from official source only.
- Verify checksums when the release provides them.
- Do not run tools that require uploading databases, scanning another user's QR login, or remote assistance.
- Save tools under a local `tools/` or `downloads/` folder that is not committed to Git.

## wx-cli End-to-End Pattern

This pattern is for `jackwener/wx-cli`-style local desktop exports. Commands may differ across versions; always run `--help` first.

### 0. Prepare A Local Tools Folder

```powershell
New-Item -ItemType Directory -Force -Path .\tools | Out-Null
New-Item -ItemType Directory -Force -Path .\exports | Out-Null
```

### 1. Acquire wx-cli From GitHub Releases

Use the official GitHub repository/release page. Prefer the latest stable release and the asset matching the user's OS/architecture.

For Windows x86_64, the asset is typically named similar to `wx-windows-x86_64.exe`.

Example PowerShell pattern:

```powershell
$repo = "jackwener/wx-cli"
$release = Invoke-RestMethod "https://api.github.com/repos/$repo/releases/latest"
$asset = $release.assets | Where-Object { $_.name -like "*windows*x86_64*.exe" -or $_.name -like "*win*x64*.exe" } | Select-Object -First 1
if (-not $asset) { throw "No Windows x86_64 asset found in latest release." }
Invoke-WebRequest -Uri $asset.browser_download_url -OutFile .\tools\wx.exe
Get-Item .\tools\wx.exe | Select-Object FullName,Length,LastWriteTime
```

If GitHub provides a digest/checksum in the release API or release notes, verify it:

```powershell
Get-FileHash -Algorithm SHA256 .\tools\wx.exe
```

Then verify the binary starts:

```powershell
.\tools\wx.exe --version
.\tools\wx.exe --help
```

### 2. Fallback: Acquire From npm Platform Package

Use this when GitHub Release CDN downloads fail but npm registry is reachable. Prefer `npm pack` into the workspace over global install.

```powershell
npm.cmd view @jackwener/wx-cli version dist.tarball dist.integrity --json
npm.cmd view @jackwener/wx-cli-win32-x64 version dist.tarball dist.integrity --json
npm.cmd pack @jackwener/wx-cli-win32-x64 --pack-destination .\tools
```

Extract the package and copy the binary:

```powershell
tar -xzf .\tools\jackwener-wx-cli-win32-x64-*.tgz -C .\tools
Copy-Item .\tools\package\bin\wx.exe .\tools\wx.exe -Force
Get-FileHash -Algorithm SHA256 .\tools\wx.exe
.\tools\wx.exe --help
```

Do not commit `.exe`, `.tgz`, extracted packages, raw exports, or WeChat database files.

### 3. Confirm WeChat Is Running And Logged In

```powershell
Get-Process | Where-Object { $_.ProcessName -match 'WeChat|Weixin' } | Select-Object ProcessName,Id,Path
```

If WeChat is not running, ask the user to open it and keep it logged in.

### 4. Initialize And Scan Local Data

```powershell
.\tools\wx.exe init --force
```

Watch for:
- Detected data directory.
- Number of encrypted databases found.
- Number of keys matched.
- Any warnings about permissions or unsupported versions.

If later output seems incomplete, rerun `init --force`. New database shards may appear after WeChat loads, after migration/backup operations, or when the tool cache gets stale.

### 5. Identify The Contact

```powershell
.\tools\wx.exe contacts -q "Contact Remark" -n 20 --json
.\tools\wx.exe sessions --limit 50 --json
```

Use the user's exact remark/name when possible. If fuzzy matching returns multiple people, ask the user before exporting.

### 6. Check Total Count Before Export

```powershell
.\tools\wx.exe stats "Contact Remark" --json
```

Use the reported `total` as the export limit. Avoid arbitrary huge values such as `999999`; some tools handle them poorly.

### 7. Export To A Local File

```powershell
.\tools\wx.exe export "Contact Remark" -n <TOTAL_FROM_STATS> -f txt -o .\exports\contact-chat.txt
```

Use `txt` or `json` for downstream distillation. `txt` is convenient for language analysis; `json` is better for structured pipelines.

### 8. Verify Completeness

Check:
- Tool-reported exported count equals `stats.total`.
- Timestamp row count equals expected count.
- First timestamp matches the user's memory or backup coverage.
- Last timestamp is current enough.
- Speaker mapping is correct.

If the user expects older records:
- Search for older `Backup/.../ChatPackage` ranges.
- Rerun `init --force`.
- Check whether local database shards changed.
- Compare key/database counts before and after reinitialization.
- Explain clearly when official backup contains older encrypted packages that the current local readable database does not expose.

### 9. Stop Background Helpers

```powershell
.\tools\wx.exe daemon stop
```

Avoid running many `wx` commands in parallel. Some versions start a daemon over a named pipe; parallel calls can cause timeout or response parsing failures.

## Verification Snippet

Use a local script or shell to count timestamped rows and first/last dates. Do not print chat content.

Expected report format:

```text
TimestampRows: 107441
FirstTimestamp: 2022-08-20 12:42
LastTimestamp: 2026-05-14 17:31
```

## Publishing Safety

Never commit:
- Raw chat exports.
- Screenshots.
- WeChat databases.
- Backup folders.
- Downloaded executables or package archives.
- Contact names, wxids, phone numbers, ID cards, addresses, or local filesystem paths.

Commit only:
- The skill instructions.
- General scripts.
- Fake sample data.
- Desensitized examples.
