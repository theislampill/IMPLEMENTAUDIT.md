IMPLEMENTAUDIT_PHASE_START
Phase: 1 of 1 — Negative: multi-step without per-step verification
Task: counter-example spec with commands only at the end of the phase
Type: negative-fixture
Run root: .IMPLEMENTAUDIT/runs/negative-multistep-no-verify
Baseline ref: abc123def456
Owner/source: fixtures/phase-validation/negative-multistep-no-per-step-verify.md
Depends on phases: none

## Why

This spec must FAIL validate-phase.sh: it is multi-step but its steps carry
no per-step verification; commands appear only at the end of the phase, so
an executor cannot confirm each step before moving on.

## Current state excerpts

- `fixtures/phase-validation/negative-multistep-no-per-step-verify.md` exists as a validator counter-example.

## Work

- Add the parser and switch the callers

## Implementation steps (ordered)

- Step 1: Add the parser — target: src/parser.ts (parseConfig); change: add a strict config parser with typed errors
- Step 2: Switch the callers — target: src/loader.ts (loadConfig); change: call parseConfig and remove the inline parsing block

## Scope boundaries

In scope: src/parser.ts, src/loader.ts
Out of scope: src/legacy-loader.ts — deprecated path scheduled for deletion.

## STOP conditions (plan-specific)

- Stop if `src/loader.ts` inline parsing differs from the current-state excerpt — baseline drifted.

## Acceptance criteria

- `npm test` exits 0 with parser tests passing

## Mandatory commands

- npm test — property: behavioral; scope: full suite after both steps; expected: exit 0

## Evidence required

- test output with exit code
- Markdown fallback: yes

## Rollback / defer path

git checkout -- src/parser.ts src/loader.ts

## Maintenance notes

- Keep this counter-example verification-free in its steps on purpose.

IMPLEMENTAUDIT_PHASE_VERIFY
Criteria results recorded here.

AGENTS_UPDATE_DECISION
Decision recorded here.

CONTINUITY_DECISION
Decision recorded here.

IMPLEMENTAUDIT_PHASE_DONE
Status recorded here.
