# Fixture: Ordinary task-shaped invocation deepens without keywords

Input shape:

```text
Using /implementaudit, get the flaky release pipeline fixed across the repo.
```

The input contains no activation keyword: the user never says "deep", "plan",
or "review". The factor profile alone warrants depth: broad scope, high
dependency density (pipeline scripts, checkers, CI, package gates), material
evidence gaps (flakiness is unmeasured), and a possibly weaker fresh-context
executor downstream.

Expected route:

- ordinary task-shaped intake binds the `tdqyq-audit-object`;
- the action-selection contract derives the warranted `ydqyq-audit-action`
  set from scope, uncertainty, risk, dependencies, evidence gaps,
  authorization state, and intended executor;
- reconnaissance, dependency analysis, and phase decomposition are selected
  because the factors warrant them — with no activation keyword present.

Required behavior:

- an action-selection record is written into the audit object
  (`## Action selection` in the run-root `THINKING.md`);
- the record names input shape, intended executor, uncertainty, dependency
  density, evidence gaps, and authorization state;
- the record lists the selected `ydqyq-audit-actions` and the
  considered-but-omitted actions with reasons;
- reference loading follows selection: `phase-design.md` loads because
  decomposition was selected;
- phase decomposition produces dependency-ordered phases with Smoke A/B and
  rollback paths.

Forbidden behavior:

- waiting for an activation keyword before selecting depth;
- deepening justified by request size alone rather than the factor profile;
- performing deep actions with no action-selection record.

Negative control:

- a run on this input that stays shallow and cites "no keyword present" as
  the reason fails;
- a run that deepens but records no action-selection rationale fails.

Evidence required:

- action-selection record with all fields non-empty;
- selected-versus-omitted action list with reasons;
- dependency-ordered phase specs;
- no activation keyword anywhere in the trigger chain.
