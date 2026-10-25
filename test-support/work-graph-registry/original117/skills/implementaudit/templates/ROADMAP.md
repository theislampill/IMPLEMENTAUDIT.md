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

## Action selection

Selected ydqyq-audit-actions:

Omitted-but-considered actions (with reasons):

Depth rationale (warranted / not warranted because):

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

| Phase | Objective | Owner/source | Depends on | Smoke A | Smoke B | Review | Status |
|---|---|---|---|---|---|---|---|
| 1 |  |  | - |  |  |  | open |

Review column: independent cold-review disposition for executor-facing
artifacts — PASS / GAP-REVISE / BLOCKED / OWNER DECISION / not applicable.

After canonical migration, read this roadmap through claim-run using the same
expected pointer token as STATE; root files and archived plans are historical
context. Preserve the complete DONE/ACTIVE/READY/BLOCKED population, obligations,
deferrals, dependencies, compensations and selected/omitted planning rationale.
The paired protected `native_guards` profile retains this role's exact native
phase table and source lines. Native phase validation consumes the selected
`native-ROADMAP.md` derivative through `read-canonical-pair.py --native-guards`,
then rechecks the complete native snapshot with `--verify-current` before
accepting its result. Every artifact input must retain its owner-bound bytes.
The pending completed-boundary audit-state obligation remains continuity-owned
when currentness or epoch is unresolved. Archives and historical refusal scopes
survive retirement; a projection or plan does not grant execution authority.

## Execution index (projection)

This roadmap — execution order, dependencies, phase status, and review
disposition — is a human-facing projection of the audit object. It is
derivative, never canonical: on divergence, the run root and phase specs
govern, and this projection is corrected to match them.

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
