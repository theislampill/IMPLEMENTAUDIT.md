# Phase shape: brownfield mutation

**Shape:** Risky mutation of existing brownfield code (schema or API change).
**Phases:** 4
**P4-1 hardening:** included (Phase 4)
**P4-2 visual polish:** N/A (no UI — documented skip)
**P4-3 brownfield safety-net:** included (Phase 1)
**P4-4 package/release split:** N/A (no release — documented skip)
**P4-5 provenance boundary:** N/A (no release — documented skip)

---

## Phase 1 — Characterization (brownfield safety-net)

Owner/source: src/db/schema.ts, tests/
Work: Snapshot current behavior; capture coverage baseline; test rollback.
Acceptance criteria:
- Full test suite passes at HEAD (current baseline documented)
- Rollback command tested dry: `git stash pop` returns clean state
- Known-failing tests catalogued in run root (THINKING.md)
Mandatory commands: npm test, git stash, git stash pop
Rollback: N/A (read-only phase)
Depends on: none

## Phase 2 — Mutation

Owner/source: src/db/schema.ts
Work: Apply schema change; update all callers; add migration script.
Acceptance criteria:
- Migration script exits 0 against test database
- All callers updated (grep confirms zero old schema references)
- Full test suite passes after migration
Mandatory commands: npm run migrate:test, npm test, grep -r OldColumnName src/
Rollback: git checkout HEAD -- src/db/schema.ts; run down-migration
Depends on: Phase 1

## Phase 3 — Validate

Owner/source: tests/, src/
Work: Regression check; confirm characterization-phase baseline is intact.
Acceptance criteria:
- No previously-passing test now fails
- Schema diff matches THINKING.md snapshot
- No dead code introduced (lint passes)
Mandatory commands: npm test, npm run lint
Rollback: git checkout HEAD -- src/
Depends on: Phase 2

## Phase 4 — Hardening

Owner/source: src/db/schema.ts, docs/
Work: Error-handling for migration failures; cleanliness; doc update.
Acceptance criteria:
- check-added-lines-clean exits 0
- Migration failure triggers structured error (not uncaught exception)
- docs/schema-changelog.md updated
Mandatory commands: bash scripts/verify-package.sh
Rollback: git checkout HEAD -- src/db/schema.ts docs/
Depends on: Phase 3

---

P4-2 skip rationale: Schema change has no user-facing UI output.
P4-4 skip rationale: No release artifact in scope.
P4-5 skip rationale: No provenance boundary in scope.
