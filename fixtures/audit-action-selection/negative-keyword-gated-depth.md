# NEGATIVE FIXTURE: depth appears only when an activation keyword is present

This fixture describes a defective run. It must fail review; it is a
counter-example, not a model to imitate.

Defective behavior:

Two invocations describe the same broad, high-dependency, evidence-gapped
repair. The first is phrased plainly and the run stays shallow: no recon
widening, no dependency analysis, no decomposition. The second adds the word
"deep" and only then does the run select the stronger action set. The
action-selection record for the second run cites the keyword — not the factor
profile — as the reason for depth.

Why this must fail:

- depth was gated on an activation keyword instead of being derived from
  scope, uncertainty, risk, dependencies, evidence gaps, authorization state,
  and intended executor;
- two factor-identical inputs received different action sets based on
  wording alone;
- the action-selection record names a keyword as the selection reason, which
  the contract forbids.

Expected disposition when reviewed: FAIL — keyword-gated depth violates the
action-selection contract in `references/planning-depth.md`.
