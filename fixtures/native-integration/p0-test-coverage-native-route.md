# Native Category Route Fixture: Tests / Validation

Input shape:
An audit finds a dangerous untested path that can regress silently.

Native route:
- Category: tests / validation
- tdqyq-audit-object: validation row with missing verification as the finding, owner/source, acceptance criteria, and registry wiring
- ydqyq-audit-action: add or require characterization-test-first evidence before risky mutation
- Owner/source: test/checker/fixture closest to the runtime behavior
- Route: DMAIC brownfield validation repair
- Smoke A/B: Smoke A records the missing or failing guard; Smoke B proves the new guard fails/passes for the right reason
- Andon: trigger on false-green tests, missing registry wiring, flaky evidence, or hidden skipped check
- Final audit: confirms validation is wired into relevant local/package/CI gates
- Plan Closure: changed when guard and registry wiring pass, deferred when owner/source rejects the guard

Finding row:
- Finding title: Dangerous path lacks characterization-test-first coverage
- Category: tests / validation
- Evidence: runtime branch exists with no focused test/checker/fixture
- Impact: future changes can break behavior without signal
- Effort: small to medium fixture/checker addition
- Risk: weak tests can create false confidence
- Confidence: high when live file and registry readback show no guard
- Fix sketch / implementation route: DMAIC validation repair with characterization-test-first route
- Owner/source: focused test, fixture, checker, and validation registry
- Acceptance criteria: guard fails on negative control and passes on live behavior
- Verification: direct test plus registry checker
- Rollback / Plan Closure: remove only the invalid guard if it proves false-positive
- Rejected/deferred rationale: defer with reason when behavior is untestable in current host
- Remaining risk: static fixture may not cover every future repo shape
- Route: DMAIC / default runtime pressure

Negative control:
- False parity to reject: "tests look adequate" without proving a guard exists and is wired
- Forbidden behavior: count documentation-only examples or passing unrelated tests as coverage for the dangerous path
