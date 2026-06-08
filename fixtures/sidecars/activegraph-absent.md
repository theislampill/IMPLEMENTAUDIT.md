# Sidecar fixture: ActiveGraph absent — Markdown fallback is first-class

When ActiveGraph is absent (.activegraph/ does not exist), the run uses
Markdown fallback for all state recording. This is not a degraded mode;
Markdown fallback is a first-class path. ActiveGraph absence must not block
the run.

## Expected sidecar block in phase VERIFY section

Sidecar: Graphify absent; ActiveGraph absent; Markdown fallback yes
Remaining risk: none

## Expected recording

- STATE.md, ROADMAP.md, THINKING.md, and phase specs serve as the audit object.
- No event write is attempted (ActiveGraph absent).
- No capability ledger entry is written.

## Rule confirmed by this fixture

- ActiveGraph absent → Markdown fallback is used; run is not blocked.
- STATE.md and phase specs are the authoritative audit object.
- "Markdown fallback: yes" recorded in the ## Graphify / ActiveGraph section.
- No capability ledger entry is claimed when ActiveGraph is absent.
