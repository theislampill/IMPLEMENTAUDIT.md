# IMPLEMENTAUDIT State

Runtime copy target: `.IMPLEMENTAUDIT/runs/<task-slug>-<id>/STATE.md`

## Current phase

| Field | Value |
|---|---|
| Run root |  |
| Phase |  |
| Status | open |
| Audit object state | open |
| Route |  |
| Owner/source |  |
| Baseline ref |  |
| Last check |  |
| Next action |  |
| Continuity decision | pending |
| Authorization state | no commit / no push / no tag / no release / no provenance unless separately authorized |

## Audit object state

Audit object / record / surface:

Mnemonic: tdqyq-audit-object

Audit object produced/updated by:

Latest auditing operation:

Mnemonic: ydqyq-audit-action

Implementation action against object:

Final auditing operation:

Terminal closure condition:

Handoff state, if any:

Graphify status:

ActiveGraph status:

Markdown fallback:

Capability Ledger:

## Runtime artifacts

| Artifact | Status | Notes |
|---|---|---|
| `<run-root>/ROADMAP.md` | open |  |
| `<run-root>/STATE.md` | open |  |
| `<run-root>/THINKING.md` | open |  |
| `<run-root>/PROTOCOL.md` | open |  |
| `<run-root>/context.md` | open |  |
| `<run-root>/tools.md` | open |  |
| `<run-root>/sidecars.md` | open |  |
| `<run-root>/applied-context.md` or `<run-root>/applied-memories.md` | open |  |
| `<run-root>/repo-map.md` for brownfield | open |  |
| `<run-root>/phases/phase-N.md` | open |  |

## Ledger

| # | Finding | Priority | Action | Status | Evidence | Depends on | Follow-up |
|---|---|---:|---|---|---|---|---|

## AGENTS_UPDATE_DECISION

Status: pending

Reason:

Scope:

Evidence location:

Final audit rule: this must be `updated`, `not warranted`, or `OWNER DECISION` before `IMPLEMENTAUDIT_RUN_COMPLETE`.

## CONTINUITY_DECISION

Status: pending

Reason:

Destination: none / AGENTS.md / memory note / OWNER DECISION

Evidence boundary:

Final audit rule: this must be `none`, `updated`, `deferred`, or `OWNER DECISION` before `IMPLEMENTAUDIT_RUN_COMPLETE`.

## Local git trace

Commit authorized: no

Push authorized: no

Tag/release/publication/provenance authorized: no
