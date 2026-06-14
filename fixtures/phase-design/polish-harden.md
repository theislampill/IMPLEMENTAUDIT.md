# Phase design fixture: Polish & Harden (optional terminal phase)

This fixture documents the Polish & Harden phase shape (Rule P4-8 in
`skills/implementaudit/references/phase-design.md`). It shows two variants:
1. Polish & Harden included — default-recommended condition
2. Polish & Harden skipped — with documented rationale

---

## Variant A: Polish & Harden included (default-recommended)

**When:** Full plan with new feature, public docs, and generated artifacts.

```text
IMPLEMENTAUDIT_PHASE_START
Phase: 4 of 4 — Polish & Harden
Task: Terminal cleanliness, identity hygiene, and generated-artifact freshness pass
Type: polish-harden
Run root: .IMPLEMENTAUDIT/runs/add-docs-portal-Xq9Pm/
Baseline ref: a1b2c3d
Owner/source: all files changed since baseline
Audit object: .IMPLEMENTAUDIT/runs/add-docs-portal-Xq9Pm/ROADMAP.md
Auditing operation: Verify cleanliness and identity hygiene post-implementation
Terminal object state to prove: all smoke checks pass; no debug debris; no
  foreign command identity in tracked surfaces; generated portal is fresh
Thinking ref: .IMPLEMENTAUDIT/runs/add-docs-portal-Xq9Pm/THINKING.md
Mandatory commands: 4
Acceptance criteria: 5
Evidence required: local static checker output; visual inspection of generated portal
Depends on phases: 1, 2, 3
Quality route: 5S / PDCA

## Why

Full plan with new public docs portal and CI workflow requires a cleanliness
and identity hygiene pass before final audit. Rule P4-8 applies.

## Work

- Run all smoke checks: lean-discipline.test.sh, continuity.test.sh,
  sidecars.test.sh, phase-validation.test.sh, routing.test.sh,
  docs-portal.test.sh, verify-package.sh
- Run check-added-lines-clean.sh to verify no debug prints, session markers,
  or dead imports were added since baseline
- Verify no foreign command identity in tracked surfaces
  (check-routing.sh scan passes)
- Verify docs-portal/index.html is fresh (generated at build time, not stale)
- Verify proof-boundary wording: no sigma/DPMO claims, no broad competence claims

## Acceptance criteria (all must pass)

- All smoke test suites pass (6/6)
- check-added-lines-clean.sh: 0 debug prints, 0 session markers, 0 dead imports added
- No foreign command identity in routing.md, SKILL.md, README.md, AGENTS.md
- docs-portal/index.html exists and was generated from source by build script
- No new feature scope introduced in this phase

## Mandatory commands

- bash tests/lean-discipline.test.sh
- bash tests/docs-portal.test.sh
- bash scripts/check-added-lines-clean.sh HEAD
- bash scripts/check-routing.sh

## Evidence required in transcript

- Each test suite exit-0 output
- check-added-lines-clean.sh summary line
- Grep result confirming no foreign command identity in tracked surfaces
```

---

## Variant B: Polish & Harden skipped — documented rationale required

**When:** Small single-surface hotfix with no public output and no generated artifacts.

```text
## Phase 9 (optional) — Polish & Harden

Skipped.

Rationale: This run is a single-surface fix to one checker script
(scripts/check-planner-stages.sh) with no public docs, no generated artifacts,
and no UI output. Rule P4-8 recommends Polish & Harden for full plans and
public surfaces; neither condition applies here.

Alternative coverage:
- check-added-lines-clean.sh passed in Phase 1 immediately after the fix
- check-routing.sh passed (identity hygiene confirmed)
- Final audit re-runs all smoke checks

Owner decision: not required — documented rationale satisfies Rule P4-7 skip
documentation requirement.
```

---

## Invariants documented

- Polish & Harden never introduces new feature scope.
- When included, it covers: cleanliness, identity hygiene, generated artifact
  freshness, proof-boundary wording.
- When skipped, rationale documents: which P4-8 conditions do not apply, and
  what alternative coverage (or owner decision) justifies the skip.
- Undocumented omission is treated as an unverified gap per Rule P4-7.
