# IMPLEMENTAUDIT State

Runtime copy target: `.IMPLEMENTAUDIT/runs/<task-slug>-<id>/STATE.md`

This is the bounded hot projection. Keep only current/open records and custody
pointers here. Closed history and detailed evidence remain queryable through the
current immutable generation and its exact archive.

## Current phase

| Field | Value |
|---|---|
| Run root |  |
| Phase |  |
| Status | open |
| Audit object state | open |
| Route |  |
| Route decision projection | PENDING |
| Route decision record | none |
| Owner/source |  |
| Baseline ref |  |
| Last check |  |
| Next action |  |
| Continuity decision | pending |
| Authorization state | no commit / no push / no tag / no release / no provenance unless separately authorized |

Status values: `open` / `READY_TO_DISPATCH` / `IN_PHASE` / `PAUSED` /
`BLOCKED` / `INTERRUPTED` / `DONE`.

## Audit object state

Audit object / record / surface:

Latest auditing operation:

Terminal closure condition:

Handoff state, if any:

## Runtime artifacts

Record only current artifact pointers and status.

| Artifact | Status | Notes |
|---|---|---|
| `<run-root>/ROADMAP.md` | open |  |
| `<run-root>/STATE.md` | open |  |
| `<run-root>/PROTOCOL.md` | open |  |
| `<run-root>/WORK_GRAPH.json` | open | authoritative DAG; record exact digest |
| `<run-root>/state-generations/<generation>/` | open | immutable history/query custody |

## Ledger

Open findings only. Closed rows migrate to immutable events and are queried on
demand rather than retained here.

| # | Finding | Priority | Action | Status | Evidence | Depends on | Follow-up |
|---|---|---:|---|---|---|---|---|

## Andon log

Open reruns, escalations, and handoff conditions only. One abnormality class per
row; linked defects share an `Occ` id.

| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |
|---|---|---|---|---|---|---|---|

## Occurrence resolution and residuals

Occurrence resolution: not-applicable

Keep unresolved or otherwise consequential current residuals only. A terminal
row is represented by its immutable event and exact history-query pointer.

| Residual | Consequential | Disposition | Owner / policy ref | Evidence |
|---|---|---|---|---|

## Execution identity

Current execution identity pointer:

## Context epochs and instruction applicability

Current epoch: G0001

Canonical projection generation: root-v2

Current-generation pointer: none

Migration marker: absent

Current continuity receipt: none

The four identity values above move together. Partial or mixed migrated state is
STOP and cannot fall back to root-v2.

| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |
|---|---|---|---|---|---|

Only the current epoch stays hot; prior epochs remain immutable query records.

| Instr | Reference | Kind | Authority | Subject | Issued epoch | Status | Status evidence | Supersedes/by | Scope end |
|---|---|---|---|---|---|---|---|---|---|

Only active, ambiguous, or otherwise still-applicable instructions stay hot.

## AGENTS_UPDATE_DECISION

Status: pending

Reason:

Scope:

Evidence location:

## CONTINUITY_DECISION

Status: pending

Reason:

Destination: none / AGENTS.md / memory note / OWNER DECISION

Evidence boundary:

## Local git trace

Commit authorized: no

Push authorized: no

Tag/release/publication/provenance authorized: no

## Run terminal disposition

Append the emitted terminal marker as the final nonblank line when the current
run becomes terminal. Closed detail remains in immutable event/archive custody.
