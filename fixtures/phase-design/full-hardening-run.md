# Phase shape: full hardening run

**Shape:** Operational parity / multi-gap hardening across a codebase.
**Phases:** 5
**P4-1 hardening:** the entire run is a hardening run; Phase 5 is the final audit
**P4-2 visual polish:** N/A (hardening run, no new UI — documented skip)
**P4-3 brownfield safety-net:** implicit in Phase 1 (audit ledger captures current state as baseline)
**P4-4 package/release split:** enforced if release is conditional (see conditional-release gate in Phase 5)
**P4-5 provenance boundary:** enforced at conditional-release gate

---

## Phase 1 — Audit ledger

Owner/source: docs/audits/<run-name>.md
Work: Classify all gap classes; document ADAPTED/REJECTED/DEFERRED per gap;
      establish baseline ref; record identity hygiene check.
Acceptance criteria:
- Audit ledger file created with all gap classes
- Each gap has status (ADAPTED/INTENTIONALLY REJECTED/DEFERRED/OUT OF SCOPE)
- Identity hygiene check section present with PASS/FAIL for forbidden terms
- Baseline ref recorded
Mandatory commands: git rev-parse HEAD, grep -r <forbidden-term> (run at audit time)
Rollback: rm docs/audits/<run-name>.md
Depends on: none

## Phase 2 — Implementation (core gaps)

Owner/source: (varies per gap)
Work: Implement all ADAPTED gaps. Each sub-item is a tracked finding in the
      audit ledger. Scope creep logged as new findings.
Acceptance criteria:
- All ADAPTED gaps have an implementation record in the ledger
- All mandatory commands for each gap exit 0
- verify-package.sh exits 0 (or failures documented as follow-on findings)
Mandatory commands: bash scripts/verify-package.sh
Rollback: git checkout HEAD -- <changed files>
Depends on: Phase 1

## Phase 3 — Validate

Owner/source: tests/, scripts/
Work: Full test suite; checker suite; cleanliness check.
Acceptance criteria:
- All tests pass
- check-added-lines-clean exits 0
- No new FIXME or placeholder in tracked files
Mandatory commands: bash scripts/verify-package.sh, git diff --check
Rollback: git checkout HEAD -- <test files>
Depends on: Phase 2

## Phase 4 — Hardening

Owner/source: scripts/, docs/, AGENTS.md
Work: Operational concerns not covered by implementation phases:
      identity hygiene checker, AGENTS.md anti-repeat rules, error handling,
      release-gate instructions, changelog.
Acceptance criteria:
- Generic forbidden-terms checker wired into release gate (not source-embedded)
- AGENTS.md updated with anti-repeat rules for this run's decisions
- CHANGELOG.md entry for this version written
- verify-package.sh exits 0 after hardening changes
Mandatory commands: bash scripts/verify-package.sh
Rollback: git checkout HEAD -- scripts/ docs/ AGENTS.md CHANGELOG.md
Depends on: Phase 3

## Phase 5 — Final audit + conditional release

Owner/source: docs/audits/<run-name>.md, release surface
Work: Final audit loop (audit-fix rounds until closed or audited handoff);
      dogfood; superiority proof;
      conditional release if all gates pass.
Acceptance criteria:
- AUDIT_COMPLETE printed with coverage math (re_verified / total)
- trust_prior <= 30% (or documented exception)
- Dogfood: skill installed and /implementaudit invoked; output recorded
- Superiority over prior version documented (at least 3 specific improvements)
- Identity hygiene check: 0 forbidden-term occurrences in tracked files
- Release performed only after all above pass
Mandatory commands: bash scripts/verify-package.sh, bash scripts/build-release-asset.sh
Rollback: skip release; tag release as pre-release
Depends on: Phase 4

---

P4-2 skip rationale: This is a tooling/operational run; no new user-facing UI output introduced.
