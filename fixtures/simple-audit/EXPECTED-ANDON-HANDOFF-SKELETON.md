# Expected Andon Handoff Transcript Skeleton

This fixture is intentionally skeletal. It shows the blocked Andon path:
probe, escalation with new evidence, then handoff on a genuine blocking
condition — never on a try count. The run ends in an audited handoff and
must not contain a run-completion marker.

```text
IMPLEMENTAUDIT_PHASE_START
Input basis:
- fixtures/simple-audit/AUDIT.md
Audit object:
- simple-audit ledger and evidence surface
- mnemonic: tdqyq-audit-object

ANDON_PROBE
Abnormality:
- acceptance criterion requires a credential the run does not hold
Class:
- failed-criterion
Owner/source:
- external service configuration named by the audit
Containment decision:
- no mutation against the unverifiable surface
5 Whys (proportional):
- symptom: check cannot run -> cause: credential absent ->
  systemic: authorization was never granted to this run
Hansei:
- gap: criterion assumed access; cause: intake did not verify access;
  countermeasure: attempt documented offline verification path; follow-up:
  rerun against the offline path
Countermeasure selected:
- offline verification path from repo-local evidence
Rerun evidence required:
- offline check produces equivalent evidence
Andon log:
- row #1 appended: class failed-criterion, outcome open (rerun pending)

ANDON_ESCALATE
Prior probe history:
- row #1 countermeasure failed: offline path cannot reproduce the evidence
Same-class citation:
- cites Andon log row #1 (failed-criterion)
New evidence:
- offline path output diverges from the criterion's required live evidence
Changed approach:
- owner-decision route selected; no bounded fix-spec can supply access
Andon log:
- row #2 appended: class failed-criterion, outcome escalated (cites #1)

ANDON_HANDOFF
Blocking condition:
- missing authorization (credential grant is an owner decision)
Probe and escalation history:
- rows #1-#2 with attempts and results
Remaining blocker:
- criterion is unverifiable without granted access
Smallest next owner action:
- grant credential or rescope the criterion to repo-local evidence
Andon log:
- row #3 appended: outcome blocked (handoff condition)
STATE.md:
- Status: BLOCKED

IMPLEMENTAUDIT_PHASE_DONE
Status:
- blocked

AUDIT_START
Skill version:
- 0.2.9
Scope:
- simple audit fixture, blocked Andon path

AUDIT_VERIFY
Checks:
- git diff --check
- Andon log readback: rows terminal (blocked with named handoff condition)

AUDIT_GAPS
Remaining:
- one criterion blocked on missing authorization; owner decision required

AUDIT_HANDOFF
Handoff:
- blocked surface, evidence trail, and smallest next owner action recorded
- no run-completion marker may follow this handoff
```
