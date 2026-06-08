# Continuity fixture: no external memory marker boundary crossing

This fixture represents a transcript that is valid because it contains no
external memory markers (MEMORY_SAVED, GOAL_ACHIEVED, or similar external
comparator marker names) in any position.

A transcript that contains such markers has allowed external identity to cross
into the native IMPLEMENTAUDIT surface. This must be detected and rejected.

## Valid transcript (no boundary crossing)

IMPLEMENTAUDIT_PHASE_START
Phase: 1 of 1 — update user schema
Task: Add email_verified column
Type: brownfield
Run root: .IMPLEMENTAUDIT/runs/schema-add-Qq7
Baseline ref: fedcba
Owner/source: db/migrations/
Audit object: .IMPLEMENTAUDIT/runs/schema-add-Qq7/ROADMAP.md
Auditing operation: add column via migration
Terminal object state to prove: migration exits 0 and column exists in schema
Thinking ref: .IMPLEMENTAUDIT/runs/schema-add-Qq7/THINKING.md
Mandatory commands: npm run migrate:test
Acceptance criteria: 1
Evidence required: migration output
Depends on phases: none

IMPLEMENTAUDIT_PHASE_VERIFY

Phase 1 acceptance criteria:
- [pass] migration exits 0: added column email_verified to users table

Mandatory commands:
- npm run migrate:test exit 0: ok

Cleanliness:
- Debug prints added: 0
- Session debug-markers added (todo/fixme/xxx): 0
- Dead imports added: 0

Sidecar: Graphify absent; ActiveGraph absent; Markdown fallback yes
Remaining risk: none
Trust-prior count: 0
Re-verified count: 1

AGENTS_UPDATE_DECISION

Decision: not warranted
Reason: Migration pattern is documented.
Scope: N/A
Evidence location: N/A
Conflict or owner-decision note: none

CONTINUITY_DECISION

Decision: none
Reason: No cross-session learning warranted.
Evidence boundary: N/A

IMPLEMENTAUDIT_PHASE_DONE

Status: done
Evidence: migration ok
Follow-up: none

---

## Check: MEMORY_SAVED must NOT appear in this file

A test that runs: grep -F 'MEMORY_SAVED' <this-file> must return exit code 1
(no match). Any match is a boundary-crossing failure.
