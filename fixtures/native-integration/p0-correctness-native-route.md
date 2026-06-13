# Native Category Route Fixture: Correctness / Bugs

Input shape:
An audit finds a wrong result in a brownfield parser after reading the live owner/source and a failing smoke.

Native route:
- Category: correctness / bugs
- tdqyq-audit-object: ledger row with owner/source, failing behavior, acceptance criteria, Smoke A/B, and final status
- ydqyq-audit-action: classify, patch owner/source, verify, and close the defect row
- Owner/source: parser module plus direct caller and focused regression check
- Route: DMAIC brownfield repair
- Smoke A/B: Smoke A captures the wrong result; Smoke B proves the corrected result and no regression
- Andon: trigger on absent reproduction, ambiguous owner/source, or any new failing previously-passing check
- Final audit: confirms the defect row is terminal and remaining risk is stated
- Plan Closure: changed when patched, blocked/deferred/unverified if evidence or owner/source is missing

Finding row:
- Finding title: Parser returns the wrong result for quoted empty values
- Category: correctness / bugs
- Evidence: failing fixture, live source readback, and focused command output
- Impact: users receive incorrect parsed data
- Effort: small bounded patch plus regression fixture
- Risk: parser edge cases may affect callers
- Confidence: high when repro and owner/source are direct
- Fix sketch / implementation route: DMAIC defect closure at parser owner/source with caller smoke
- Owner/source: parser module and focused test fixture
- Acceptance criteria: quoted empty values parse correctly and existing cases still pass
- Verification: focused parser test plus relevant package smoke
- Rollback / Plan Closure: revert parser patch and fixture if Smoke B regresses
- Rejected/deferred rationale: not applicable unless live evidence disproves the finding
- Remaining risk: untested formats outside the scoped parser surface
- Route: DMAIC / default runtime pressure

Negative control:
- False parity to reject: a generic "bug risk" note without a wrong result, source citation, owner/source, or verification route
- Forbidden behavior: classify as PASS from intuition, skip Smoke A/B, or mutate unrelated callers without owner/source evidence
