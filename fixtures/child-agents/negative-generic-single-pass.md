# NEGATIVE FIXTURE: broad scope collapsed into one generic written pass

This fixture describes a defective run. It must fail review; it is a
counter-example, not a model to imitate.

Defective behavior:

A materially broad audit warrants distinct specialist lanes, and the host
cannot parallelize. Instead of serializing bounded per-lane passes, the run
performs one undifferentiated written review of the whole repo — no
per-lane bounded questions, no per-lane evidence boundaries, no per-lane
findings rows — and labels the single blob "serialized fanout" without any
justification for the collapse.

Why this must fail:

- a serialized lane is a separate bounded written review pass carrying the
  same per-lane contract; one generic mega-pass has no lane boundaries and
  defeats the independent-evidence purpose of fanout;
- collapsing specialty work into one pass requires explicit justification
  recorded in the audit object, not a relabel;
- without per-lane records, skipped coverage is undetectable and the final
  audit cannot state honest residual risk.

Expected disposition when reviewed: FAIL — unjustified collapse violates
the serialized-fallback contract in `child-agents.md`.
