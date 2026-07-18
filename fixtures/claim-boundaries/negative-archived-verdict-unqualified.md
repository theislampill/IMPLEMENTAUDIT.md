# NEGATIVE FIXTURE: archived verdict surfaced without qualification

This fixture is a counter-example for the proof-level rule; it must fail
the claim-boundary check when its content appears on an active surface.
The file itself is path-exempt (`fixtures/claim-boundaries/negative-*`).

Defective active-surface content (an active summary quoting an archived
verdict bare):

    Per the archived rerun audit, the donor capability set is PROVEN and
    the program can build on that as settled behavior.

Why this must fail: the archive body legitimately carries the bare verdict
as history, but an ACTIVE summary that re-surfaces it without its
proof-level qualification launders structural evidence into
settled-behavior language.

Expected disposition when checked: FAIL — an active summary quoting an
archived verdict requires the same-line proof-level qualification.
