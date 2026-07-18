# Fixture: allowed proof wording (positive examples)

These lines demonstrate verdict-class wording carried correctly on active
surfaces. This file is scanned by `check-public-claim-boundaries.sh` like
any active surface and must pass as written.

- The parity milestone is `PROVEN_WITH_WEAKNESSES` [proof level: PL4 structural validation + PL5 fixture demonstration; not PL6 behaviorally observed, not PL7 fresh-executor proven].
- The rerun verdict `PROVEN` rests on runtime instruction and package evidence [proof level: PL2 + PL4 + PL5; not PL6/PL7].
- The surpass ledger is a source-milestone record; its `SURPASSED` rows are source-milestone claims, not behavioral ones.
- A future behavioral upgrade example: capability X is `PROVEN` at PL6 behaviorally observed (owner-approved A-series run, bundle hash recorded), not yet PL7 fresh-executor proven.
- Negated context stays legal without a qualifier: this capability is not PROVEN and must not be described as such.
