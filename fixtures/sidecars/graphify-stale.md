# Sidecar fixture: Graphify stale — record stale, require live confirmation

When Graphify output is present but stale (indexed before recent commits or
config changes), it must be recorded as stale/avoided. Live-file confirmation
is required before any owner/source claim is made.

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

- Using Graphify stale output as orientation evidence without noting it is stale.
- Claiming owner/source was confirmed without a live Gemba read.
- Omitting the stale status from the sidecar block.

## Rule confirmed by this fixture

- Graphify stale → record stale/avoided in sidecar block.
- All owner/source must be confirmed by live file reads (Gemba).
- "Graphify: present-and-stale" recorded in the ## Graphify / ActiveGraph section.
- Evidence type for any claim must be "live file read" not "Graphify orientation".
