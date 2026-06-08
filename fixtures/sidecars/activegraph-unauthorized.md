# Sidecar fixture: ActiveGraph configured but unauthorized — no event write

When ActiveGraph is configured (.activegraph/ exists or is referenced in
sidecars.md) but the current run is NOT authorized to write events (owner has
not granted write authorization), no event write may occur.

## Expected behavior

- ActiveGraph is detected (configured).
- The run reads sidecars.md; ActiveGraph is listed as "configured-not-authorized".
- No event is written to the ActiveGraph store.
- The phase transcript records "ActiveGraph: configured-not-authorized" or "ActiveGraph skipped".
- Markdown fallback is used for all state.

## Expected sidecar block in phase VERIFY section

Sidecar: Graphify absent; ActiveGraph configured-not-authorized (no event write); Markdown fallback yes
Remaining risk: none

## Forbidden when ActiveGraph is unauthorized

- Writing any event to the ActiveGraph store.
- Claiming capability ledger entries derived from this run.
- Treating configuration as authorization.

## Rule confirmed by this fixture

- ActiveGraph configured but not authorized → no event write, no capability ledger entry.
- "ActiveGraph: configured-not-authorized" recorded in the sidecar block.
- Markdown fallback is first-class.
- Configuration ≠ authorization.
