# NEGATIVE FIXTURE: cold review gated on a "review" keyword

This fixture describes a defective run. It must fail review; it is a
counter-example, not a model to imitate.

Defective behavior:

Two factor-identical invocations each produce an executor-facing handoff
artifact. The first is phrased plainly; the run hands off with no
independent cold review and no disposition. The second includes the word
"review", and only then does the run dispatch the cold reviewer. The
lifecycle record cites the keyword as the trigger.

Why this must fail:

- the independent cold-review gate binds to the artifact class — an
  executor-facing handoff or materially risky phase plan — not to request
  wording;
- ordinary task-shaped invocations that generate executor-facing specs run
  the gate without any special keyword;
- keyword-gated review is the same activation defect the action-selection
  contract forbids for depth, applied to the review gate.

Expected disposition when reviewed: FAIL — keyword-gated cold review
violates the ordinary-lifecycle binding in `plan-lifecycle.md` and the
umbrella architecture (no keyword-activated modes).
