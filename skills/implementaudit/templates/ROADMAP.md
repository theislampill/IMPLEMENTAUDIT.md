# IMPLEMENTAUDIT Roadmap

Runtime copy target: `.IMPLEMENTAUDIT/runs/<task-slug>-<id>/ROADMAP.md`

## Goal

<!-- State the bounded work target. -->

## Audit object

<!-- State the evidence-bearing audit record/surface this roadmap closes. -->

Audit object source:

Audit object mnemonic: tdqyq-audit-object

Audit object terminal closure condition:

Double-audit sequence, if release-affecting or high-risk:

1. ydqyq-audit-action -> tdqyq-audit-object:
2. ydqyq-audit-action against tdqyq-audit-object:
3. Final ydqyq-audit-action -> terminal tdqyq-audit-object state:

## Baseline ref

<!-- Commit hash, branch, or file snapshot used for diff-based final audit. -->

## Run root

IMPLEMENTAUDIT_BASE:

IMPLEMENTAUDIT_RUN_ROOT:

IMPLEMENTAUDIT_BASELINE_REF:

Legacy flat `.IMPLEMENTAUDIT/` state:

Run claim command:

```bash
bash "${IMPLEMENTAUDIT_SKILL_DIR:-skills/implementaudit}"/scripts/claim-run.sh "<task summary>"
```

## Planning evidence

Thinking file: `<run-root>/THINKING.md`

Protocol file: `<run-root>/PROTOCOL.md`

Context file: `<run-root>/context.md`

Tools file: `<run-root>/tools.md`

Sidecars file: `<run-root>/sidecars.md`

Applied context file: `<run-root>/applied-context.md` or `<run-root>/applied-memories.md`

Repo map file for brownfield work: `<run-root>/repo-map.md`

## Phases

| Phase | Objective | Owner/source | Depends on | Smoke A | Smoke B | Status |
|---|---|---|---|---|---|---|
| 1 |  |  | - |  |  | open |

## Scope boundaries

- No commit unless explicitly authorized.
- No push unless explicitly authorized.
- No tag unless explicitly authorized.
- No release unless explicitly authorized.
- No publication unless explicitly authorized.
- No provenance claim unless explicitly authorized and evidenced.
- No optional tool install, indexing, setup, config, or export unless separately
  authorized.

## Scope-creep register

| # | Issue | Location | Recommendation | Status |
|---|---|---|---|---|
