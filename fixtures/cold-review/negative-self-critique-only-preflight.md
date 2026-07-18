# NEGATIVE FIXTURE: preflight reached with self-critique only

This fixture describes a defective run. It must fail review; it is a
counter-example, not a model to imitate.

Defective behavior:

A run produces an executor-facing handoff plan, performs a thorough Stage 6
self-critique ("Self-critique: clean"), and proceeds directly to Stage 6.5
preflight and dispatch. No independent cold review ran; no disposition was
recorded. The plan carried a hidden-context assumption the author mentally
filled — the executor failed on it downstream.

Why this must fail:

- self-critique is the author reviewing its own plan; it cannot surface the
  gaps the author's context fills invisibly;
- the lifecycle requires an independent cold-review disposition
  (PASS / GAP-REVISE / BLOCKED / OWNER DECISION) recorded in the audit
  object before preflight, dispatch, or handoff of an executor-ready
  artifact;
- "Self-critique: clean" is a Stage 6 record, not a Stage 6.2 disposition.

Expected disposition when reviewed: FAIL — handoff readiness claimed on
self-critique alone violates the independent cold-review gate in
`plan-lifecycle.md`.
