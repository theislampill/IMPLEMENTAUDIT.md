# Native Category Route Fixture: DX / Tooling

Input shape:
An audit finds a missing or broken typecheck, lint, onboarding, AGENTS guidance, helper script, or host-aware runbook path.

Native route:
- Category: DX / tooling
- tdqyq-audit-object: tooling row with host constraints, helper owner/source, expected output, and evidence boundary
- ydqyq-audit-action: repair or document the tool path through native Smoke A/B and owner/source closure
- Owner/source: helper script, test, validation registry, host runbook, or scoped instruction file
- Route: DMAIC brownfield tooling repair
- Smoke A/B: Smoke A captures broken command or missing gate; Smoke B proves the repaired command/checker output
- Andon: trigger on substituted command, shell quoting failure, hidden install, or host mismatch
- Final audit: confirms command output, registry wiring, and remaining host risk
- Plan Closure: changed when tool path is fixed, unverified when host/runtime is unavailable

Finding row:
- Finding title: Typecheck helper is absent from validation registry
- Category: DX / tooling
- Evidence: live script/test registry readback and missing command
- Impact: contributors miss fast feedback and future regressions slip through
- Effort: small checker or registry update
- Risk: host-specific shell behavior can break validation
- Confidence: high when registry grep and direct command prove the gap
- Fix sketch / implementation route: DMAIC tooling repair with host-aware helper/runbook checks
- Owner/source: script, test, registry, and AGENTS guidance when durable
- Acceptance criteria: command exists, emits clear diagnostics, and is wired where required
- Verification: direct command, registry checker, and no hidden install
- Rollback / Plan Closure: remove or revert bad helper and registry entry together
- Rejected/deferred rationale: defer when the host lacks required runtime and no fallback is safe
- Remaining risk: other hosts may need separate smoke evidence
- Route: DMAIC / default runtime pressure

Negative control:
- False parity to reject: saying "DX could improve" without a failing helper, missing registry, or onboarding owner/source
- Forbidden behavior: install tooling, rewrite runbooks broadly, or update AGENTS with transient logs
