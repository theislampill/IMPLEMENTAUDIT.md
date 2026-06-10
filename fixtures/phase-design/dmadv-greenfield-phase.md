# Phase 1 — New CONTRIBUTING quickstart fragment (DMADV greenfield exemplar)

Validator-passing example of a greenfield, DMADV-routed phase spec. Pair with
the brownfield exemplar in fixtures/run-root-example/.

IMPLEMENTAUDIT_PHASE_START
Task: create docs/quickstart-fragment.md as a new governed artifact
Type: greenfield
Quality route: DMADV
Run root: .IMPLEMENTAUDIT/runs/example-quickstart-dmadv-d4e5f6
Baseline ref: HEAD
Owner/source: docs/quickstart-fragment.md (new; owner defined at intake)
Audit object: greenfield quickstart-fragment intake record
Depends on phases: none

## Work

Define (capability, users, constraints) -> Measure (CtQ acceptance below) ->
Analyze (alternatives: inline README section rejected as duplication) ->
Design (this spec + template) -> Verify (mandatory command + Smoke B).
Create docs/quickstart-fragment.md with a 4-step first-run path.

## Acceptance criteria

- [ ] docs/quickstart-fragment.md exists, non-empty, with exactly 4 numbered steps

## Mandatory commands

- test -s docs/quickstart-fragment.md
- grep -c '^[0-9]\.' docs/quickstart-fragment.md

## Evidence required

- command outputs above, evidence type: static checker
- Markdown fallback: yes (no sidecars configured)
- rollback evidence: file removal restores baseline (greenfield removal path)

## Rollback / defer path

git rm --cached docs/quickstart-fragment.md && rm docs/quickstart-fragment.md
(removal path: greenfield artifacts roll back by deletion, not revert)

IMPLEMENTAUDIT_PHASE_VERIFY
Criteria results, mandatory command outputs, cleanliness readback recorded here.

AGENTS_UPDATE_DECISION
Decision recorded here.

CONTINUITY_DECISION
Decision recorded here.

IMPLEMENTAUDIT_PHASE_DONE
Status recorded here.
