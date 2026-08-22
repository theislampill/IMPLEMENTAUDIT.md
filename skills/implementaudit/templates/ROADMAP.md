# IMPLEMENTAUDIT Roadmap

Runtime copy target: `.IMPLEMENTAUDIT/runs/<task-slug>-<id>/ROADMAP.md`

This is the bounded hot roadmap. Keep the current objective, active work,
applicable instructions, and exact custody pointers here. Completed phases and
planning evidence remain queryable through immutable history.

## Goal

<!-- State the bounded current work target. -->

## Audit object

Audit object source:

Audit object terminal closure condition:

Current auditing operation:

## Action selection

Selected current ydqyq-audit-actions:

Omitted current actions (with reasons):

Depth rationale:

## Baseline ref

<!-- Exact current commit, tree, or immutable snapshot pointer. -->

## Run root

IMPLEMENTAUDIT_BASE:

IMPLEMENTAUDIT_RUN_ROOT:

IMPLEMENTAUDIT_BASELINE_REF:

Canonical projection generation: root-v2

Current-generation pointer: none

Migration marker: absent

Current continuity receipt: none

These four values move together. Partial or mixed migrated state is STOP and
cannot fall back to root-v2.

## Planning evidence

Current pointers only:

- Thinking: `<run-root>/THINKING.md`
- Protocol: `<run-root>/PROTOCOL.md`
- Context: `<run-root>/context.md`
- Tools: `<run-root>/tools.md`
- Sidecars: `<run-root>/sidecars.md`
- WORK_GRAPH: `<run-root>/WORK_GRAPH.json` plus exact digest
- History query: current generation manifest/query contract

## Phases

Active/open phases only. Completed rows migrate to immutable events.

| Phase | Objective | Owner/source | Depends on | Smoke A | Smoke B | Review | Status |
|---|---|---|---|---|---|---|---|
| 1 |  |  | - |  |  |  | open |

## Execution index (projection)

Derivative of exact `WORK_GRAPH.json`; record its digest. WORK_GRAPH remains the
sole governed DAG authority.

## Scope boundaries

- No commit unless explicitly authorized.
- No push, tag, release, publication, or provenance effect unless separately
  authorized.
- No optional tool install, indexing, setup, config, or export unless separately
  authorized.

## Scope-creep register

Open rows only. Resolved rows migrate to immutable events.

| # | Issue | Location | Recommendation | Status |
|---|---|---|---|---|
