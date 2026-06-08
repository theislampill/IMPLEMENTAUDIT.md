# Phase shape: simple greenfield

**Shape:** New isolated feature, no UI output, no release artifact.
**Phases:** 3
**P4-1 hardening:** included (Phase 3)
**P4-2 visual polish:** N/A (CLI/backend only — documented skip)
**P4-3 brownfield safety-net:** N/A (greenfield — documented skip)
**P4-4 package/release split:** N/A (no release — documented skip)
**P4-5 provenance boundary:** N/A (no release — documented skip)

---

## Phase 1 — Implement

Owner/source: src/features/new-feature.ts
Work: Write the feature module and unit tests.
Acceptance criteria:
- `npm run build` exits 0
- `npm test -- --testPathPattern=new-feature` exits 0, all tests pass
- Feature function returns expected output for 3 representative inputs
Mandatory commands: npm run build, npm test -- --testPathPattern=new-feature
Rollback: git checkout HEAD -- src/features/new-feature.ts tests/new-feature.test.ts
Depends on: none

## Phase 2 — Integration validate

Owner/source: src/app.ts (integration point)
Work: Wire feature into app entry point; run integration smoke.
Acceptance criteria:
- Integration test exits 0
- No regression in existing tests (full test suite passes)
Mandatory commands: npm test, npm run lint
Rollback: git checkout HEAD -- src/app.ts
Depends on: Phase 1

## Phase 3 — Hardening

Owner/source: src/features/new-feature.ts, docs/
Work: Error-handling edge cases, cleanliness check, doc update.
Acceptance criteria:
- check-added-lines-clean exits 0 (no debug prints, no session markers)
- Error input returns structured error (not uncaught exception)
- docs/features/ updated with new feature description
Mandatory commands: bash scripts/verify-package.sh, npm test
Rollback: git checkout HEAD -- src/features/new-feature.ts docs/
Depends on: Phase 2

---

P4-2 skip rationale: Feature is a pure backend function with no user-facing output.
P4-3 skip rationale: Greenfield feature; no existing code mutated.
P4-4 skip rationale: No release artifact in scope.
P4-5 skip rationale: No provenance boundary in scope.
