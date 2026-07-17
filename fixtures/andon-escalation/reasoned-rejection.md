# Fixture: governing-rule suspicion rejected WITH a recorded reason

ANDON_ESCALATE
Phase: 3
Failing criterion: build succeeds
New evidence: a one-off typo in the phase spec; the validator and taxonomy
behaved correctly.
Governing-rule review (second-order recurrence): suspicion evaluated.
Rejection reason: the defect was a single mistyped path unique to this case;
the validator correctly would have failed a real regression, verified by a
neighboring probe that still fails closed.
Governing-rule judgment: case-defect.
