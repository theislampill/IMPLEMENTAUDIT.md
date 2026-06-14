# Improve Comparator Matrix Negative Fixture

Purpose: prove the competitor-surpass checker rejects an Improve matrix that
omits a load-bearing prompt-injection boundary token.

Canonical status vocabulary: SURPASSED, COVERED, REJECTED_WITH_REASON,
DEFERRED, OWNER_DECISION, UNVERIFIED, FAIL.

Detail status vocabulary: ADOPTED, ALREADY_MET, STRENGTHENED, SUPERSEDED,
REJECTED_INVALID, DEFERRED_OWNER_DECISION, OBSERVATION_ONLY.

This fixture keeps nearby required terms such as self-contained plans, drift check,
STOP conditions, and machine-checkable done criteria, but intentionally
omits the required data-boundary token that the positive matrix must carry.

| ID | Comparator claim | Verified source/evidence | IMPLEMENTAUDIT verdict | Canonical status | Detail status | Closure evidence |
|---|---|---|---|---|---|---|
| IMP-01 | self-contained plans. | Synthetic negative fixture. | Present only to prove rejection. | COVERED | ALREADY_MET | This negative fixture is intentionally incomplete. |
