# Native Category Route Fixture: Performance / Scale

Input shape:
An audit sees an N+1 query pattern, avoidable O(n squared) loop, oversized payload, or slow CI-feedback path.

Native route:
- Category: performance / scale
- tdqyq-audit-object: performance row with owner/source, measurement-or-static-evidence label, acceptance target, rollback, and final status
- ydqyq-audit-action: classify evidence strength, patch owner/source when authorized, and verify the delta
- Owner/source: hot path, query builder, payload serializer, or CI helper that owns the cost
- Route: DMAIC brownfield performance repair
- Smoke A/B: Smoke A records timing/count/static complexity; Smoke B compares the same signal after repair
- Andon: trigger on benchmark substitution, hidden dependency install, or unverifiable performance claim
- Final audit: states whether evidence is live measurement, local benchmark, CI-feedback, or static inference
- Plan Closure: changed when measured/static delta is verified, unverified when evidence is too weak

Finding row:
- Finding title: N+1 fetch in list rendering path
- Category: performance / scale
- Evidence: loop plus per-item query readback, static complexity, or reproducible query count
- Impact: latency and load grow with item count
- Effort: medium owner/source patch and regression/perf guard
- Risk: batching can alter ordering or error behavior
- Confidence: medium/high depending on measurement availability
- Fix sketch / implementation route: DMAIC performance repair with measurement-or-static-evidence boundary
- Owner/source: data loader or serializer that controls the repeated work
- Acceptance criteria: query count, complexity, payload, or CI-feedback improves without correctness regression
- Verification: focused measurement or explicitly labeled static evidence plus existing tests
- Rollback / Plan Closure: revert batching/cache change if Smoke B regresses behavior
- Rejected/deferred rationale: defer if no safe benchmark or owner/source is available
- Remaining risk: local measurement may not represent production scale
- Route: DMAIC / default runtime pressure

Negative control:
- False parity to reject: performance advice without measurement, static evidence label, owner/source, or rollback
- Forbidden behavior: install benchmarking tools, alter dependencies, or claim production speedup without authorization and evidence
