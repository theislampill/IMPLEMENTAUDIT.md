# NEGATIVE FIXTURE: projection contradicts the audit object

This fixture describes a defective run. It must fail review; it is a
counter-example, not a model to imitate.

Defective behavior:

The roadmap phases table shows phase 3 as Status done with Review PASS. The
audit object records phase 3 blocked on an unresolved owner decision, and no
cold-review disposition exists for it. The projection was hand-edited to
look complete for a status report and never corrected.

Why this must fail:

- the roadmap/index is a derivative projection of the audit object, never
  canonical; a projection state the object does not support is status
  theater;
- a Review cell may only mirror a disposition actually recorded in the
  audit object;
- on divergence the run root and phase specs govern and the projection must
  be corrected — the divergence itself is an abnormality to record, not a
  presentation choice.

Expected disposition when reviewed: FAIL — a projection that contradicts
the audit object violates the derivative-projection contract in the
roadmap template and `plan-lifecycle.md`.
