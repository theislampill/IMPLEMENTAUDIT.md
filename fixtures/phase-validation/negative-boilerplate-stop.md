IMPLEMENTAUDIT_PHASE_START
Phase: 1 of 1 — Negative: boilerplate STOP conditions
Task: counter-example spec whose STOP conditions reflect no actual risk
Type: negative-fixture
Run root: .IMPLEMENTAUDIT/runs/negative-boilerplate-stop
Baseline ref: abc123def456
Owner/source: fixtures/phase-validation/negative-boilerplate-stop.md
Depends on phases: none

## Why

This spec must FAIL validate-phase.sh: its STOP conditions are generic
boilerplate tied to no concrete file, command, marker, or assumption of the
phase, so they cannot stop an executor at the moments that matter.

## Current state excerpts

- `fixtures/phase-validation/negative-boilerplate-stop.md` exists as a validator counter-example.

## Work

- Rename the export and update its imports

## Implementation steps (ordered)

- Step 1: Rename the export — target: src/index.ts (createClient); change: rename createClient to makeClient, keep a deprecated alias; verify: npm run build; expected: exit 0 with no errors

## Scope boundaries

In scope: src/index.ts
Out of scope: published API docs — regenerated separately.

## STOP conditions (plan-specific)

- Something goes wrong.
- Unexpected error occurs.

## Acceptance criteria

- `npm run build` exits 0

## Mandatory commands

- npm run build — property: behavioral; scope: compile after rename; expected: exit 0

## Evidence required

- build output with exit code
- Markdown fallback: yes

## Rollback / defer path

git checkout -- src/index.ts

## Maintenance notes

- Keep the STOP items generic on purpose; the validator must reject them.

IMPLEMENTAUDIT_PHASE_VERIFY
Criteria results recorded here.

AGENTS_UPDATE_DECISION
Decision recorded here.

CONTINUITY_DECISION
Decision recorded here.

IMPLEMENTAUDIT_PHASE_DONE
Status recorded here.
