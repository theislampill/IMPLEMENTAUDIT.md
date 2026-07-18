# NEGATIVE FIXTURE: deepening justified by request size alone

This fixture describes a defective run. It must fail review; it is a
counter-example, not a model to imitate.

Defective behavior:

A long, wordy request describes what is actually one bounded, single-owner
repair with no material uncertainty, dependency density, or evidence gap. The
run selects goal synthesis, phase decomposition, and a multi-phase roadmap
anyway. The action-selection record justifies the depth with "the request is
large" and names no factor that deeper structure would improve.

Why this must fail:

- the depth rule says: do not add a planning layer merely because the work is
  large; add it when the extra structure improves evidence, sequencing,
  rollback, or owner decisions;
- request size alone never deepens the action set — the factor profile does;
- the omitted-action reasoning is inverted: restraint was warranted and was
  neither selected nor honestly considered.

Expected disposition when reviewed: FAIL — size-only deepening violates the
action-selection contract and the depth rule in
`references/planning-depth.md`.
