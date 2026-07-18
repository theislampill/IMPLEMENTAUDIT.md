# NEGATIVE FIXTURE: warranted lane silently dropped under low concurrency

This fixture describes a defective run. It must fail review; it is a
counter-example, not a model to imitate.

Defective behavior:

A broad pre-release audit warrants correctness, security, tests, and docs
lanes. The host cannot run concurrent subagents. The run executes
correctness, tests, and docs as serialized written passes but silently
omits the security lane — no skipped-with-reason record, no residual-risk
row — and the final audit implies full category coverage.

Why this must fail:

- host concurrency limits may change scheduling, but they never silently
  erase a warranted lane;
- a skipped warranted lane requires an explicit skipped-with-reason
  coverage-lane record and its residual risk carried into the final audit;
- implying full coverage while a warranted security lane is unexecuted is a
  false-closure hazard, not a scheduling detail.

Expected disposition when reviewed: FAIL — silent lane drop violates the
serialized-fallback mandate in `child-agents.md` and
`audit-category-matrix.md`.
