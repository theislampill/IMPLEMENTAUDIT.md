# Goal Format

Use this reference when goal synthesis mode needs to return a ready-to-paste
goal runner handoff.

## Embedded governance rule

If the current session is already inside a supplied `/goal using /implementaudit`
run, do not print a second `/goal`. Continue governing the active target.

## Ready-to-paste shape

```text
/goal Using /implementaudit, in <repo path>, implement <bounded target>.

Input basis:
- <audit/handoff/checklist/review/gap source>

Owner/source candidates:
- <files/artifacts to inspect first>

Required phases:
- Phase 1: <smallest coherent slice>
- Phase 2: <next coherent slice, if needed>

Safety boundaries:
- No commit.
- No push.
- No tag.
- No release.
- No publication.
- No provenance claim.
- No optional tool install/index/setup/export unless separately authorized.

Required checks:
- Smoke A: <baseline command or inspection>
- Smoke B: <post-change command or inspection>
- Complete repo-state comparison: <baseline ref or reason unavailable>

Final audit:
- Print AUDIT_COMPLETE before IMPLEMENTAUDIT_RUN_COMPLETE.
- Print AUDIT_HANDOFF only when gaps, blockers, or handoff-required caveats remain.
- Close every ledger item terminally.
```

Slash commands fire only from user input. Agent text containing `/goal ...` is a
handoff for the user to paste, not automatic dispatch.
