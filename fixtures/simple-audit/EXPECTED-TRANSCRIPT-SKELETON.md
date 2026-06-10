# Expected Transcript Skeleton

This fixture is intentionally skeletal. It checks marker order, not the exact
wording of a run.

```text
IMPLEMENTAUDIT_PHASE_START
Input basis:
- fixtures/simple-audit/AUDIT.md
Audit object:
- simple-audit ledger and evidence surface
- mnemonic: tdqyq-audit-object
Auditing actions:
- inspect owner/source, classify checks, patch, verify, and close
- mnemonic: ydqyq-audit-action
Double-audit sequence:
- AUDIT_START normalized the audit object before mutation
- implementation acted against that object
- AUDIT_VERIFY checked the object against evidence before completion

IMPLEMENTAUDIT_PHASE_VERIFY
Criteria:
- owner/source inspected
- Smoke A recorded
- Smoke B recorded
- audit object updated with terminal status evidence

AGENTS_UPDATE_DECISION
Decision:
- Not warranted; no durable repo-local rule was learned.

IMPLEMENTAUDIT_PHASE_DONE
Status:
- changed

AUDIT_START
Skill version:
- 0.2.9
Scope:
- simple audit fixture

AUDIT_VERIFY
Checks:
- git diff --check
- bash scripts/verify-package.sh

AUDIT_GAPS
Remaining:
- none

AUDIT_COMPLETE
Coverage:
- all in-scope fixture items terminally closed
- audit object reached terminal verified closure before run completion

IMPLEMENTAUDIT_RUN_COMPLETE
```
