# WeChat Compatibility Notes

Use this alongside `references/wechat-export.md` when a WeChat export looks incomplete or unstable.

## Compatibility Matrix

| Factor | What To Check | Symptom | Move |
| --- | --- | --- | --- |
| WeChat desktop version | version shown in WeChat settings | tool cannot find databases | update export notes and check wx-cli issues |
| Data directory | `xwechat_files` path and active account wxid | wrong account or empty export | verify current logged-in account |
| Database shards | number of DB files found during `init --force` | early years missing | rerun init after WeChat fully loads |
| Key matching | matched keys count | partial decrypt | compare before/after `init --force` |
| Backup packages | `Backup/.../ChatPackage` exists | official backup has older range but export lacks it | restore via official WeChat or explain encrypted package limits |
| wx-cli version | `wx.exe --version` | command options differ | run `--help` and adjust commands |
| Huge export limit | arbitrary `-n 999999` | truncated or inconsistent output | use `stats.total` as export limit |
| Daemon state | background helper running | timeout or stale results | stop daemon and rerun |

## Completeness Checklist

- `stats.total` equals exported message count.
- Timestamp rows equal exported message count or expected text rows.
- First timestamp matches user memory or known backup range.
- Last timestamp is current enough.
- Speaker mapping is correct.
- User-reported missing years are investigated before distillation.

## Version Logging

Record this in the final export health note:

```text
WeChat data path:
wx-cli source:
wx-cli version:
init database count:
matched key count:
stats total:
exported rows:
first timestamp:
last timestamp:
known gaps:
```
