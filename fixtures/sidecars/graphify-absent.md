# Sidecar fixture: Graphify absent — ordinary Gemba passes

When Graphify is absent (graphify-out/ does not exist or is empty), the run
proceeds using ordinary Gemba: reading files directly from disk. This is the
first-class path. Absence of Graphify must not block the run.

## Expected sidecar block in phase VERIFY section

Sidecar: Graphify absent; ActiveGraph absent; Markdown fallback yes
Remaining risk: none

## Expected IMPLEMENTAUDIT_PHASE_VERIFY content (sidecar section)

Graphify: absent
ActiveGraph: absent
Markdown fallback: yes

## Rule confirmed by this fixture

- Graphify absent is valid and non-blocking.
- Gemba proceeds via direct file reads.
- No orientation or proof claim is made from absent output.
- "Markdown fallback: yes" is recorded when both sidecars are absent.
