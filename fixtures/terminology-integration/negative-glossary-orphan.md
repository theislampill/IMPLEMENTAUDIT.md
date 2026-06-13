# Terminology Integration Fixture: Negative Glossary / Orphan Term

Fixture status: negative

## Bad Prompt

Use VOC, CTQ, SIPOC, FMEA, Strangler, ACL, Bounded Context, STRIDE, SOLID,
GRASP, Control Plan, Poka-yoke, Standard Work, and A3.

## Expected Rejection

This is glossary theater. It has no native parent, runtime phase, route/lens,
owner/source, evidence boundary, Andon/control hook, fixture/checker, or final
audit role.

- Native parent: missing.
- Runtime phase: missing.
- Route/lens: missing.
- Owner/source: missing.
- Evidence boundary: missing.
- Andon/control hook: missing.
- Fixture/checker: `scripts/check-terminology-integration.sh`.

## Acceptance

`scripts/check-terminology-integration.sh` must reject any runtime-shaping file
that accepts this style of term accumulation as implementation guidance.
