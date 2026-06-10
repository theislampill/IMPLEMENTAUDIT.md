# IMPLEMENTAUDIT State — exemplar run root

Tracked exemplar (sanitized) of a dispatched run root. Real runs copy the
full `templates/STATE.md`; this fixture shows the minimum structure
`validate-run-root.sh` requires, with contract-true values.

## Current phase

| Field | Value |
|---|---|
| Run root | .IMPLEMENTAUDIT/runs/example-greeting-fix-a1b2c3 |
| Phase | 1 |
| Status | READY_TO_DISPATCH |
| Route | brownfield |
| Baseline ref | (git rev-parse HEAD at dispatch) |

Status values: `open` / `READY_TO_DISPATCH` / `IN_PHASE` / `PAUSED` /
`BLOCKED` / `INTERRUPTED` / `DONE`.

## Andon log

| # | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |
|---|---|---|---|---|---|---|

## Ledger

| # | Finding | Priority | Action | Status | Evidence | Depends on | Follow-up |
|---|---|---:|---|---|---|---|---|
| 1 | greeting casing wrong in app.txt | P1 | patch owner/source | open | — | — | — |
