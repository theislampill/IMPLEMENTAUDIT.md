# Transcript Fixture: Quick / Bounded Audit

AUDIT_START

Input:

```text
Using /implementaudit, do a quick audit of scripts/install-codex-from-release.sh.
```

Expected route:

- default runtime pressure
- quick/bounded audit behavior
- read-only audit-object closure unless implementation is separately authorized

Evidence row:

| Field | Value |
|---|---|
| Owner/source inspected | `scripts/install-codex-from-release.sh` |
| Required adjacent checks | caller docs, install smoke, package boundary, security/no-secret handling |
| Omitted surfaces | classified deferred/out of scope/unverified with reason |
| Finding priority | top high-confidence rows first |

Forbidden behavior:

- Do not advertise `/implementaudit quick`.
- Do not claim full deep coverage.
- Do not mutate source during read-only audit-object closure.

AUDIT_VERIFY

Expected close: findings or handoff rows include owner/source, verification,
confidence, omitted-surface disclosure, and remaining risk.
