# NEGATIVE FIXTURE: absent or hand-wavy action-selection record

This fixture describes a defective run. It must fail review; it is a
counter-example, not a model to imitate.

Defective behavior:

A run performs reconnaissance, dependency analysis, and phase decomposition on
an ordinary task-shaped invocation — plausibly the right action set — but the
audit object contains no action-selection record. The run-root `THINKING.md`
has no `## Action selection` section; the only trace is a transcript remark
that the task "seemed complicated enough to plan properly."

Why this must fail:

- the contract requires the record both ways: selected actions and
  considered-but-omitted actions, each with reasons;
- "seemed complicated" names no factor — scope, uncertainty, risk,
  dependencies, evidence gaps, authorization state, intended executor — and
  cannot be reviewed or falsified;
- an absent or hand-wavy action-selection record is a plan-quality defect,
  not a style preference.

Expected disposition when reviewed: FAIL — missing action-selection record
violates the action-selection contract in `references/planning-depth.md`.
