# Expected Transcript Skeleton

This fixture is intentionally skeletal. It checks marker order, not the exact
wording of a run.

```text
IMPLEMENTAUDIT_PHASE_START
Input basis:
- fixtures/simple-audit/AUDIT.md

IMPLEMENTAUDIT_PHASE_VERIFY
Criteria:
- owner/source inspected
- Smoke A recorded
- Smoke B recorded

AGENTS_UPDATE_DECISION
Decision:
- Not warranted; no durable repo-local rule was learned.

IMPLEMENTAUDIT_PHASE_DONE
Status:
- changed

AUDIT_START
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

IMPLEMENTAUDIT_RUN_COMPLETE
```
