# Continuity fixture: safe note write — correct frontmatter required

This transcript shows a case where a CONTINUITY_DECISION write is warranted.
The note is bounded (repo-specific, non-secret, non-diagnostic), and follows
the correct frontmatter format.

AGENTS_UPDATE_DECISION

Decision: updated
Reason: Discovered that this repo's integration tests require a running local DB on port 5432; this is not documented anywhere. Adding to AGENTS.md.
Scope: tests/integration/
Evidence location: tests/integration/setup.ts:14
Conflict or owner-decision note: none

CONTINUITY_DECISION

Decision: run-local applied-context note
Reason: The local DB requirement on port 5432 is non-obvious and would cause future sessions to fail integration tests without explanation. Worth persisting as a bounded repo note.
Evidence boundary: tests/integration/setup.ts:14 — confirmed present at run time, not inferred.

IMPLEMENTAUDIT_CONTINUITY_SAVED
Target: .IMPLEMENTAUDIT/runs/add-rate-limit-Ab2K/applied-context.md
Reason: Port-5432 local DB requirement is non-obvious; persisting for continuity on this task
Evidence: tests/integration/setup.ts:14 — confirmed at run time
Boundary: run-local note only; not broad project memory; not a secrets file; diagnostic: false
Authorization: CONTINUITY_DECISION option "run-local applied-context note" selected; no external marker used
Not saved: raw integration test logs; session debug output; build artifacts

---

## Required memory note frontmatter (must be present for safe write)

```yaml
---
type: repo-note
scope: tests/integration
source: .IMPLEMENTAUDIT/runs/add-rate-limit-Ab2K/phases/phase-2.md
evidence: tests/integration/setup.ts:14
session: bounded
secret: false
diagnostic: false
---
Integration tests require a local PostgreSQL instance on port 5432.
Run `docker compose up -d db` before `npm run test:integration`.
```

The note is safe to write because:
- secret: false (no credentials)
- diagnostic: false (no raw logs or error dumps)
- scope: limited to tests/integration/
- evidence: line-referenced, not inferred
- session: bounded (not broad competence claim from one run)
