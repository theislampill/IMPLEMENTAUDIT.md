# Fixture: Native Compatibility Plan Lifecycle

Classification: imported behavior through the `tdqyq-audit-object` lifecycle.

Self-contained plan fields:

- planned-at baseline ref and working-tree state
- objective, non-scope, owner/source, and route
- branch/diff scope with base ref, changed files, dependent importers/callers
  when material, introduced-vs-pre-existing classification, and fallback path
- phase order, dependencies, acceptance criteria, STOP / Andon conditions,
  rollback/defer path, and mandatory commands
- sidecar non-proof status and explicit authorization boundaries

Review-plan semantics:

- cold reader: a fresh agent can execute from disk without chat context
- weak executor: a literal executor cannot overclaim, mutate the wrong owner, or
  cross authorization gates

Execute / dispatch / review semantics:

- APPROVE means criteria are met with evidence
- REVISE means a bounded fix is needed
- BLOCK means owner/source, safety, or authorization prevents closure
- no hidden commit, push, merge, release, publication, provenance, install,
  index, export, or issue creation

Reconciliation statuses:

- DONE
- BLOCKED
- IN PROGRESS
- TODO
- STALE
- DRIFTED
- FIXED INDEPENDENTLY
