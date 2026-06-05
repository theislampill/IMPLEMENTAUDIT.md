# Expected Ledger

| # | Finding | Priority | Owner/source | Action | Status | Evidence | Depends on |
|---|---|---:|---|---|---|---|---|
| 1 | README collapses local commit and push authorization. | P1 | README.md derived from IMPLEMENTAUDIT.md | Restore separate-gate wording. | changed | Smoke B grep/manual inspection | - |

## Expected closure

- Smoke A records the pre-change README wording.
- Smoke B confirms the separate-gate wording.
- `AGENTS_UPDATE_DECISION` states whether a durable repo-local rule was updated,
  not warranted, or requires OWNER DECISION.
- No commit, push, tag, release, publication, or provenance claim is made unless
  separately authorized.
- Final audit prints `AUDIT_COMPLETE` before `IMPLEMENTAUDIT_RUN_COMPLETE`.
- `AUDIT_HANDOFF` is printed only if gaps, blockers, or handoff-required caveats
  remain.
