# Phase 1 — Fix greeting casing

IMPLEMENTAUDIT_PHASE_START
Task: fix greeting casing in app.txt
Type: brownfield
Run root: .IMPLEMENTAUDIT/runs/example-greeting-fix-a1b2c3
Baseline ref: HEAD
Owner/source: app.txt
Audit object: greeting casing finding ledger
Depends on phases: none

## Work

Change 'hello' to 'Hello' in app.txt.

## Current state excerpts

- `app.txt` first line is `hello` at baseline HEAD.
- No generated artifacts participate in this phase.

## Acceptance criteria

- [ ] app.txt first line reads 'Hello'

## Mandatory commands

- grep -q '^Hello' app.txt — property: behavioral; scope: the greeting file's first line after the work; expected: exit 0 and first line matches `Hello`

## Evidence required

- grep output showing the corrected line, evidence type: static checker
- Markdown fallback: yes (no sidecars configured)

## Rollback / defer path

git checkout -- app.txt

## Maintenance notes

- Keep this fixture minimal and validator-passing when phase spec requirements change.

IMPLEMENTAUDIT_PHASE_VERIFY
Criteria results, mandatory command outputs, cleanliness readback recorded here.

AGENTS_UPDATE_DECISION
Decision recorded here.

CONTINUITY_DECISION
Decision recorded here.

IMPLEMENTAUDIT_PHASE_DONE
Status recorded here.
