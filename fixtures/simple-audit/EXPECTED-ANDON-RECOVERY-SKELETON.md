# Expected Andon Recovery Transcript Skeleton

This fixture is intentionally skeletal. It shows the recovered Andon path:
an abnormality stops the line, the probe drives a countermeasure, rerun
evidence confirms correction, and the run still reaches terminal closure.
It checks marker order and required Andon fields, not exact run wording.

```text
IMPLEMENTAUDIT_PHASE_START
Input basis:
- fixtures/simple-audit/AUDIT.md
Audit object:
- simple-audit ledger and evidence surface
- mnemonic: tdqyq-audit-object

ANDON_PROBE
Abnormality:
- mandatory check exited non-zero on first run
Class:
- failed-criterion
Failing criterion / command / artifact:
- "checker passes" / bash scripts/example-check.sh / exit 1
Owner/source:
- scripts/example-check.sh
Containment decision:
- no further mutation until the probe completes
5 Whys (proportional):
- symptom: checker fails -> cause: stale expected value in checker ->
  systemic: generated value changed without checker update
Hansei:
- gap: checker not updated with source; cause: no paired-update rule;
  countermeasure: update checker from owner/source; follow-up: rerun checker
Countermeasure selected:
- update the stale expected value at the owner/source
Rerun evidence required:
- bash scripts/example-check.sh exits 0
Andon log:
- row #1 appended: class failed-criterion, outcome open (rerun pending)

Rerun evidence:
- bash scripts/example-check.sh -> exit 0
- Andon log row #1 outcome: resolved
- phase resumes; no new marker needed

IMPLEMENTAUDIT_PHASE_VERIFY
Criteria:
- owner/source inspected
- Smoke A recorded
- countermeasure followed from the probe, not the symptom
- rerun evidence recorded before resume
- Smoke B recorded

AGENTS_UPDATE_DECISION
Decision:
- Not warranted; countermeasure was run-local, not a durable repo rule.

IMPLEMENTAUDIT_PHASE_DONE
Status:
- changed

AUDIT_START
Skill version:
- 0.2.9
Scope:
- simple audit fixture, including the recovered Andon path

AUDIT_VERIFY
Checks:
- git diff --check
- bash scripts/verify-package.sh
- Andon log readback: all rows terminal (resolved)

AUDIT_GAPS
Remaining:
- none

AUDIT_COMPLETE
Coverage:
- all in-scope fixture items terminally closed
- recovered abnormality closed with rerun evidence, no try cap involved

IMPLEMENTAUDIT_RUN_COMPLETE
```
