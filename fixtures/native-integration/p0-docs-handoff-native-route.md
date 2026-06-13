# Native Category Route Fixture: Docs / Handoff

Input shape:
An audit finds docs or handoff text that contradicts runtime behavior or overstates proof.

Native route:
- Category: docs / handoff
- tdqyq-audit-object: truth row with source-owned claim, runtime evidence, generated-artifact policy, and final overclaim audit
- ydqyq-audit-action: classify the claim, patch source-owned text when in scope, and verify generated output when applicable
- Owner/source: source doc, handoff, generated-doc source, checker, or run-root artifact
- Route: DMAIC brownfield docs/handoff truth repair
- Smoke A/B: Smoke A records contradiction or stale claim; Smoke B proves source and generated outputs match runtime behavior
- Andon: trigger on public-claim overreach, generated-artifact mismatch, or unauthorized publication
- Final audit: confirms no claim exceeds evidence and unresolved doc risks are terminally classified
- Plan Closure: changed when source-owned claim is repaired, deferred when docs are out of current owner scope

Finding row:
- Finding title: Docs claim behavior that the runtime does not implement
- Category: docs / handoff
- Evidence: source-owned claim plus runtime source/checker contradiction
- Impact: users and future agents follow an unsafe or stale path
- Effort: small source-doc or generated-source update
- Risk: docs repair can imply release/publication if boundary is unclear
- Confidence: high when claim and runtime contradiction are direct
- Fix sketch / implementation route: DMAIC public-claim truth repair with generated-doc refresh when applicable
- Owner/source: doc source, generator, checker, or handoff artifact
- Acceptance criteria: claim matches runtime behavior and evidence boundary is explicit
- Verification: source readback, generated-doc checker when applicable, final overclaim audit
- Rollback / Plan Closure: revert doc source and regenerated output as one unit
- Rejected/deferred rationale: defer external or public docs when current instruction excludes docs scanning
- Remaining risk: external docs may drift outside this runtime audit
- Route: DMAIC / default runtime pressure

Negative control:
- False parity to reject: treating docs as true because they are docs rather than comparing them to runtime source
- Forbidden behavior: publish, release, issue-create, or claim external docs are current without explicit gate and evidence
