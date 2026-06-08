# Fixture: DMADV greenfield new runtime helper

Route: DMADV (greenfield — new governed runtime artifact)

## Define
New capability: `skills/scripts/check-lean-discipline.sh` — poka-yoke gate verifying
Lean discipline is implemented as runtime behavior, not glossary-only prose.
Users: IMPLEMENTAUDIT runtime; CI; pre-release gates.
Constraints: must not claim Lean/TPS certification; must be concise; must not bloat package.
Non-scope: full Lean audit/assessment; domain-specific Lean implementations beyond IMPLEMENTAUDIT.
Owner/source of truth: `scripts/check-lean-discipline.sh` (checker); `scripts/verify-package.sh` (calls it).
Success boundary: exits 0 when lean-operating-discipline.md exists + 5S appears in PROTOCOL.md +
Muda/Mura/Muri appears in THINKING.md + Hansei/Kaizen/Jidoka chain appears in PROTOCOL.md +
no sigma-level/certification/DPMO claim present in skills/.

## Measure
CtQ acceptance:
- Checker exits 0 on a well-formed repo with Lean discipline present.
- Checker exits non-zero (with informative message) when any required section is absent.
- Checker does not flag the evidence-boundary statements in lean-operating-discipline.md.
Baseline: no checker exists; absence means Lean concepts could remain glossary-only.
Risk: checker too strict (false positives) or too loose (misses absent sections).

## Analyze
Design alternatives:
A) Python-based (like check-routing.sh) — flexible, consistent with existing checkers.
B) Bash grep chain — simpler, less maintainable.
Selected: Python (A), consistent with existing checker pattern.
Dependencies: python/python3/py -3 (same requirement as other checkers).
Package boundary: checker lives in `scripts/` (repo-only, not in `skills/`).
Rollback: delete `scripts/check-lean-discipline.sh`; remove call from `verify-package.sh`.

## Design
Phase spec: single greenfield phase.
Template: follow check-routing.sh / check-host-claims.sh pattern.
Fixtures: `fixtures/lean/` — valid and invalid examples for test.
Validation: `tests/lean-discipline.test.sh` (20 min pass/fail cases).

## Verify
Smoke B: `bash scripts/check-lean-discipline.sh` exits 0 on current repo.
Final audit: `bash tests/lean-discipline.test.sh` all cases pass.
Package check: `bash scripts/verify-package.sh` includes lean discipline check.
Boundary: checker in `scripts/`, not `skills/`; does not ship to consumers.
