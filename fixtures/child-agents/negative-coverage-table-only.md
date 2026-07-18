# NEGATIVE FIXTURE: coverage table with no executed lanes

This fixture describes a defective run. It must fail review; it is a
counter-example, not a model to imitate.

Defective behavior:

A materially broad audit prints a polished nine-category coverage matrix in
the audit object — every row marked "covered" — but the run contains zero
executed or serialized specialist lane records. No lane was dispatched, no
bounded written pass ran, no per-lane findings exist; the matrix cells were
filled from the single main-pass impression of the repo.

Why this must fail:

- fanout means actual bounded specialist actions where warranted; a coverage
  table alone is not proof (umbrella invariant 6);
- a coverage table documents executed lanes — it never substitutes for
  them;
- the audit object carries no coverage-lane records, so the "covered" cells
  are unfalsifiable and the final audit's broad-coverage claim is
  unsupported.

Expected disposition when reviewed: FAIL — table-only coverage violates the
Deep Category Review Loop contract in `audit-category-matrix.md` and the
coverage-lane record requirement in `child-agents.md`.
