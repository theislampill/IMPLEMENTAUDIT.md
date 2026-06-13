# Transcript Fixture: Reconcile Statuses

AUDIT_START

Input:

```text
Using /implementaudit, reconcile this handoff against the live repo.
```

Expected route:

- reconcile
- final audit over planned work, live files, final diff, and evidence
- run-root plan index adaptation

Evidence row:

| Field | Value |
|---|---|
| Statuses | DONE / BLOCKED / IN PROGRESS / TODO / STALE / DRIFTED / FIXED INDEPENDENTLY |
| Backlog owner | `ROADMAP.md`, `STATE.md`, and phase specs, not root `plans/README.md` |
| Blocked row | owner/source and next action |
| Fixed independently | live evidence, pre-existing provenance classification |

Forbidden behavior:

- Do not convert unchecked rows into success.
- Do not hide stale or drifted rows.
- Forbidden: create GitHub issues.

AUDIT_VERIFY

Expected close: every row maps to done, changed, blocked, deferred, or
unverified with evidence and remaining risk.
