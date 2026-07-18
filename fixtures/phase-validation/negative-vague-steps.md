IMPLEMENTAUDIT_PHASE_START
Phase: 1 of 1 — Negative: vague step language
Task: counter-example spec whose steps a fresh executor cannot follow
Type: negative-fixture
Run root: .IMPLEMENTAUDIT/runs/negative-vague-steps
Baseline ref: abc123def456
Owner/source: fixtures/phase-validation/negative-vague-steps.md
Depends on phases: none

## Why

This spec must FAIL validate-phase.sh: its step language is vague, so a
fresh executor cannot reconstruct the work from disk.

## Current state excerpts

- `fixtures/phase-validation/negative-vague-steps.md` exists as a validator counter-example.

## Work

- Update the relevant files so the checker passes

## Implementation steps (ordered)

- Step 1: Improve the code — target: src/utils.ts; change: adjust the helpers in the relevant module until behavior is right; verify: npm test; expected: exit 0

## Scope boundaries

In scope: src/
Out of scope: tests/ — unchanged.

## STOP conditions (plan-specific)

- Stop if `npm test` fails twice after a reasonable fix attempt.

## Acceptance criteria

- `npm test` exits 0

## Mandatory commands

- npm test — property: behavioral; scope: full suite; expected: exit 0

## Evidence required

- test output with exit code
- Markdown fallback: yes

## Rollback / defer path

git checkout -- src/

## Maintenance notes

- Keep this counter-example vague on purpose; the validator must reject it.

IMPLEMENTAUDIT_PHASE_VERIFY
Criteria results recorded here.

AGENTS_UPDATE_DECISION
Decision recorded here.

CONTINUITY_DECISION
Decision recorded here.

IMPLEMENTAUDIT_PHASE_DONE
Status recorded here.
