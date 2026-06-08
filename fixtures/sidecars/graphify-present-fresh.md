# Sidecar fixture: Graphify present and fresh — orientation evidence only

When Graphify output is present and fresh (indexed recently, not stale), it
may be used as orientation evidence: a read-only map to identify owner/source
candidates. It is NOT proof of correctness or behavioral claims.

## Expected sidecar block in phase VERIFY section

Sidecar: Graphify used (orientation); ActiveGraph absent; Markdown fallback yes
Remaining risk: Graphify output was used for orientation only; live file reads confirmed owner/source.

## Forbidden claims (must not appear when Graphify is the evidence basis)

The following phrases must NOT appear in a phase transcript that uses Graphify
as its sole evidence basis:

- "Graphify proves..."
- "Graphify confirms..."
- "Graphify output proves correctness"
- "verified by Graphify"

## Required language (must appear when Graphify is used)

- "orientation evidence" OR "orientation only" OR "Graphify output is orientation"

## Rule confirmed by this fixture

- Graphify present and fresh → allowed as orientation evidence.
- Owner/source must be confirmed by live file read (Gemba).
- Graphify does not provide proof; live verification is required for any claim.
- Evidence type in Smoke Before Claim must be "orientation evidence" not "live runtime".
