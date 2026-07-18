# NEGATIVE FIXTURE: unqualified verdict-class wording

This fixture is a counter-example for the proof-level rule; it must fail
the claim-boundary check when its content appears on an active surface.
The file itself is path-exempt (`fixtures/claim-boundaries/negative-*`) so
the counter-example can exist; the test injects its content into an active
probe location and expects the checker to fail.

Defective active-surface content:

    Capability parity is PROVEN.
    The competitor milestone is SURPASSED.

Why this must fail: verdict-class wording on an active/current surface with
no same-line proof-level qualification and no negating context conflates
structural evidence with behavioral proof — the exact rediscovery cycle the
taxonomy exists to prevent.

Expected disposition when checked: FAIL — unqualified verdict-class wording
violates the proof-level rule in `docs/audits/RETENTION.md`.
