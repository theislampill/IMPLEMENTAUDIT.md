# Fixture: Roadmap execution index is a derivative projection

Scenario:

A phased run maintains its run-root `ROADMAP.md` phases table — execution
order, dependencies, Smoke A/B, Review disposition, Status — while the
audit object evolves through phase execution.

Required behavior:

- the phases table shows execution order, dependencies, current status, and
  the independent cold-review disposition for each executor-facing phase;
- the roadmap states that it is a human-facing projection of the audit
  object — derivative, never canonical;
- when the live run-root state and the projection diverge, the run root and
  phase specs govern, and the projection is corrected to match them;
- a consumer (human or executor agent) can read dependency order and
  current status from the projection without opening every phase spec.

Forbidden behavior:

- editing the projection to a state the audit object does not support
  (status theater);
- treating the projection as the authority when it conflicts with run-root
  state;
- maintaining the projection as a second, hand-curated planning document
  that drifts independently.

Negative control:

- a projection showing a phase DONE while the audit object records it
  blocked fails;
- a projection whose Review cell shows PASS with no recorded disposition in
  the audit object fails.

Evidence required:

- phases table with order, dependencies, status, and review disposition;
- the derivative-not-canonical statement in the roadmap;
- on divergence: a correction to the projection, never a silent override of
  the run root.
