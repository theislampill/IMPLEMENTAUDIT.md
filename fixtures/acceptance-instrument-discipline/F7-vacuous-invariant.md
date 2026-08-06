# F7: vacuous-invariant cold-review fixture

Fixture family: cold review

Setup: `_strip_collision_identity` unconditionally writes `lemma`, `root`, and
`pos` to null. The proposed invariant then checks only that `lemma`, `root`, and
`pos` are null.

Disposition: REVIEW_FLAG

Review basis: the setter entails the predicate, so the claimed invariant records
the setter's own claim instead of testing an independent property.

Mechanical gate: forbidden. This fixture preserves a judgment-shaped cold-review
question and does not claim dataflow analysis from a deterministic checker.
