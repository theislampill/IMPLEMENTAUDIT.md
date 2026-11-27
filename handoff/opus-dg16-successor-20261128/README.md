# DG16 successor operator: reviewed package (published under #209 §6)

This is file publication only. Publishing it launches no run, issues no grant, and does not reissue Root's records (owner decision #209 comment 7225938202, §6).

## What failed, and why

Run 46046841410 used operator `2af600fad0e80fa71d9f808741bd74db792308b2` on branch `engineering/pro-dg16-image23-main-20261127-02`, which is SPENT. It failed at "Prepare original core". Its artifact `FAILURE.json` records a `ValueError` whose message sha256 `a53078887f660a89b754edf277c39601f813209febf29773ba8b165a5dd23289` equals the literal `SELECTED_ENGINE_BINDINGS_DIFFER_FROM_ASSEMBLY` (`packet/operation.py:116`, `load_selected`).

The cause is a stale row in `EXECUTING_SOURCE_BINDINGS`, which `operation.py`, `g3_receiving.py` and `proof_consumer.py` each carry:
- The row pins `scripts/work-graph-c5-executor.py` at 83099 B / `d9b9ad23…`.
- The pinned V24 loader of source `fc2e416c` maps that member to `test-support/r5-runtime-directory-mode-source/work-graph-c5-executor.py`, which is 108100 B / `5c74e75e6a88121918d0c254c5964f6efe950c09fcc5560ef698080254839b20`.
- This mapping is intentional for revisions V8 through V24. Operators V21 (`09d14249`), V22 (`5426802e`) and V23 (`54aa3c9f`) bound the correct value.
- Operator `68e701d3` introduced the stale value.

## The successor

- **Commit:** `bcd6e8974edd71e214fbacf381dfa1ddab8d96da`, tree `ebae278fb84dbe599d16902b77df22fc4a4f3bc2`, parent `2af600fa`.
- **Bundle:** `dg16-image23-successor-20261128-v4.bundle`, sha256 `b6d52aee8aea7fc77945dfdde4179de998e52a6556e656f19267cc0c319a99c9`. It requires `2af600fa`. Fetch that commit, then fetch from the bundle.

Its changes are limited to:
- the trigger branch renamed to `engineering/dg16-image23-main-20261128-01` (22 occurrences in 13 files);
- the executor row repinned to the engine-derived 108100 / `5c74e75e…` in all three modules;
- the new offline control `tests/test_load_selected.py`;
- the cascaded pins.

The trigger is unchanged: `on: create`, with the same guards.

## Review

A fresh non-author delta review returned **GO**. It independently confirmed:
- the intended directory-mode mapping;
- the exact change set;
- every pin, recomputed from bytes;
- that `load_selected` refuses on `2af600fa` with the run's message hash and passes on `bcd6e897`;
- that the builder reproduces the commit;
- that the create trigger fires exactly once;
- that only image `20261122.23.1` passes.

The operator's older offline tests are partly stale (they expect earlier sources, pins and branches). Their results are identical on `2af600fa` and `bcd6e897`. Turning them green is DG16 executor work.

## Root records

The `drafts/` folder holds DRAFTS. Their times (2026-11-27T18:30Z to 2026-11-28T01:00Z) are expired placeholders. Root issues fresh records and rebuilds as described in `ROOT_INSTRUCTIONS.md`. When only the records and times change, the rebuilt commit needs only a records-diff check.

## Trigger rules

- Trigger only with `git push origin <sha>:refs/heads/<new branch>`, using a personal credential (never GITHUB_TOKEN), one ref per push.
- Never delete or recreate a trigger branch.
- Review copies travel only as bundles.

Running `rebuild_successor.py` requires Linux and a git checkout of `fc2e416c` (`--source-root`). Keep `test_load_selected.py` beside it.
