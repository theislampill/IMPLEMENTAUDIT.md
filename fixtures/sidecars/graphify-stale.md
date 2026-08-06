# Sidecar fixture: Graphify stale — record stale, require live confirmation

When `graph.json` `built_at_commit` differs from `git rev-parse HEAD`, the
packaged freshness command exits nonzero with `stale-sidecar`. The terrain is
unusable and must be recorded as stale/avoided. Ordinary live-file Gemba is the
only path for owner/source claims.

## Expected sidecar block in phase VERIFY section

Sidecar: Graphify stale (avoided); ActiveGraph absent; Markdown fallback yes
Remaining risk: Graphify was stale at run time; all owner/source confirmed via live file reads.

## Required recording when Graphify is stale

The phase transcript must include at least one of:
- "Graphify: present-and-stale"
- "Graphify stale"
- "Graphify avoided"

And must include evidence that owner/source was confirmed by live file read:
- "live file confirmed" OR "read from disk" OR "direct inspection"

## Forbidden when Graphify is stale

- Using stale Graphify output as orientation evidence for any purpose.
- Claiming owner/source was confirmed without a live Gemba read.
- Omitting the stale status from the sidecar block.

## Rule confirmed by this fixture

- Graphify stale → executable SHA mismatch, `stale-sidecar`, record avoided.
- All owner/source must be confirmed by live file reads (Gemba).
- "Graphify: present-and-stale" recorded in the ## Graphify / ActiveGraph section.
- Evidence type for any claim must be "live file read" not "Graphify orientation".
