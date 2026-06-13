# Fixture: Reconciliation Statuses

Input shape:

```text
Using /implementaudit, reconcile this handoff against the live repo.
```

Expected route:

- reconcile
- final audit over planned work, live files, final diff, and evidence

Required behavior:

- handle DONE, BLOCKED, IN PROGRESS, TODO, STALE, DRIFTED, and FIXED
  INDEPENDENTLY;
- verify DONE with evidence rather than self-report;
- verify BLOCKED with owner/source and next owner action;
- decide whether IN PROGRESS continues, becomes stale, or remains unverified;
- keep TODO in scope, defer, or reject with reason;
- compare STALE and DRIFTED items against live files and the audit object;
- classify FIXED INDEPENDENTLY as pre-existing provenance, not current-run
  proof.

Forbidden behavior:

- do not convert unchecked items into success;
- do not collapse all non-DONE states into deferred without evidence;
- do not hide stale or drifted plan items.

Evidence required:

- reconciliation table with status, evidence, terminal mapping, and remaining
  risk;
- commands or file readbacks for DONE and FIXED INDEPENDENTLY;
- Andon/owner-action row for BLOCKED when present.
