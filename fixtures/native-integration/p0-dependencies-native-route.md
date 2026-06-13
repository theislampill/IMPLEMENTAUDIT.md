# Native Category Route Fixture: Dependencies / Migrations

Input shape:
An audit finds deprecated/EOL dependency use, lockfile drift, migration drift, or install-path mismatch.

Native route:
- Category: dependencies / migrations
- tdqyq-audit-object: dependency row with manifest/lockfile readback, blast radius, no hidden install/update, and rollback
- ydqyq-audit-action: classify the current state, plan or patch owner/source, and verify package/install behavior
- Owner/source: manifest, lockfile, migration file, install helper, or package manifest
- Route: DMAIC brownfield dependency/migration repair
- Smoke A/B: Smoke A records current manifest/lockfile/migration state; Smoke B verifies drift is repaired or deferred
- Andon: trigger on unauthorized install/update, missing lockfile evidence, or package payload mismatch
- Final audit: confirms package/install evidence and no unapproved dependency mutation
- Plan Closure: changed when drift is fixed, deferred when update is unsafe or out of scope

Finding row:
- Finding title: Lockfile drift hides deprecated/EOL dependency state
- Category: dependencies / migrations
- Evidence: current manifest/lockfile readback and version mismatch
- Impact: installs may be stale, insecure, or unreproducible
- Effort: small for metadata drift, larger for migration
- Risk: dependency updates can change runtime behavior
- Confidence: high when manifest and lockfile disagree
- Fix sketch / implementation route: DMAIC dependency repair with no hidden install/update
- Owner/source: manifest and lockfile or migration owner
- Acceptance criteria: manifest/lockfile/migration state is consistent or explicitly deferred
- Verification: package/path-integrity checker or install smoke when authorized
- Rollback / Plan Closure: revert manifest/lockfile/migration patch as one unit
- Rejected/deferred rationale: defer updates requiring owner approval or network/install gate
- Remaining risk: upstream vulnerability notices can change after audit
- Route: DMAIC / default runtime pressure

Negative control:
- False parity to reject: dependency advice that does not read current manifest and lockfile
- Forbidden behavior: hidden install, package update, migration execution, release, or provenance claim without separate authorization
