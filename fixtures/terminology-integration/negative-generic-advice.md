# Terminology Integration Fixture: Negative Generic Advice

Fixture status: negative

## Bad Prompt

Apply SOLID everywhere, run FMEA, use STRIDE, and compute numeric RPN scores so
the design is more professional.

## Expected Rejection

- SOLID/GRASP: reject unless mapped to owner/source, scoped design evidence,
  route, verification, and evidence boundary.
- FMEA-lite: reject numeric RPN, severity, occurrence, or detection scores
  without measured evidence.
- STRIDE: reject as a standalone lane; it is security pressure attached to
  material security surfaces and trust boundaries.
- Native parent: missing or incomplete.
- Runtime phase: missing or incomplete.
- Route/lens: missing or incomplete.
- Owner/source: missing.
- Evidence boundary: missing or invented.
- Andon/control hook: generic advice must trigger Andon.
- Fixture/checker: `scripts/check-terminology-integration.sh`.

## Acceptance

`scripts/check-terminology-integration.sh` must reject generic design/security/
risk advice that is not attached to native IMPLEMENTAUDIT runtime behavior.
