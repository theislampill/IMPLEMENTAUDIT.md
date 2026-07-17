# Fixture: same-class recurrence -> second-order governing-rule judgment

ANDON_ESCALATE
Phase: 3
Failing criterion: canonicalization output stable across reruns
Prior ANDON_PROBE history: cites #4 (same class: regression)
New evidence: the same canonicalization defect class recurred (cites #4)
Governing-rule review (second-order recurrence): same-class recurrence.
Governing-rule judgment: governing-rule-defect (validator) — the validator
accepts unnormalized output, so the class keeps recurring; routing repair to
poka-yoke + AGENTS_UPDATE_DECISION.
