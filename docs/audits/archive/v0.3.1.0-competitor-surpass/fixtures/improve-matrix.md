# Improve Comparator Matrix

Source: attached `improve-main(1).zip`, SHA-256
`8FBCE8DE9AF124B675B14C5DC7BE000AC4EC86F3772AA98688F41A461A7C9B30`.

Canonical status vocabulary: SURPASSED, COVERED, REJECTED_WITH_REASON,
DEFERRED, OWNER_DECISION, UNVERIFIED, FAIL.

Detail status vocabulary: ADOPTED, ALREADY_MET, STRENGTHENED, SUPERSEDED,
REJECTED_INVALID, DEFERRED_OWNER_DECISION, OBSERVATION_ONLY.

| ID | Comparator claim | Verified source/evidence | IMPLEMENTAUDIT verdict | Canonical status | Detail status | Closure evidence |
|---|---|---|---|---|---|---|
| IMP-01 | Advisor is read-only by default. | `skills/improve/SKILL.md` Hard Rules. | IMPLEMENTAUDIT is not read-only by identity, but read-only audit-object closure is explicit and implementation requires authorization. | COVERED | ALREADY_MET | `skills/implementaudit/SKILL.md`, routing refs, read-only audit fixtures. |
| IMP-02 | Plans are the product. | README and plan template. | IMPLEMENTAUDIT keeps the run-root audit object as product plus implementation closure when authorized, which is the stronger native product surface. | SURPASSED | SUPERSEDED | `skills/implementaudit/templates/ROADMAP.md`, `skills/implementaudit/templates/phase-goal.txt`. |
| IMP-03 | self-contained plans for weaker executors. | `references/plan-template.md`. | Adopted as phase/handoff self-containment gates and made checker-backed. | SURPASSED | STRENGTHENED | `scripts/check-plan-quality-contract.sh`. |
| IMP-04 | drift check before execution. | Plan template drift check. | Already covered by baseline refs and repo-state comparison, now checker-backed for plan examples. | SURPASSED | STRENGTHENED | `fixtures/competitor-surpass/plan-quality/valid-handoff-plan.md`. |
| IMP-05 | STOP conditions prevent improvisation. | Plan template STOP section. | Adopted as phase rollback/defer and Andon handoff semantics. | COVERED | ALREADY_MET | `skills/implementaudit/scripts/validate-phase.sh`, phase fixture. |
| IMP-06 | machine-checkable done criteria. | Plan template done criteria. | Adopted into phase acceptance and mandatory-command expected-output checks. | SURPASSED | STRENGTHENED | `scripts/check-plan-quality-contract.sh`. |
| IMP-07 | Commands include expected output. | Plan template command table. | Already stronger: phase validator rejects commands without expected success shape. | COVERED | ALREADY_MET | `tests/phase-validation.test.sh`. |
| IMP-08 | Current state excerpts are inlined. | Plan template current state section. | Already stronger: filled phase specs require current-state excerpts. | COVERED | ALREADY_MET | `skills/implementaudit/scripts/validate-phase.sh`. |
| IMP-09 | repo-content-as-data prompt-injection boundary. | Improve Hard Rule 6. | Already native and shipped; now matrix keeps it visible. | COVERED | ALREADY_MET | `skills/implementaudit/templates/phase-goal.txt`, `skills/implementaudit/templates/PROTOCOL.md`. |
| IMP-10 | never reproduce secret values. | Improve Hard Rule 4. | Already covered by security and child-agent prompt contracts. | COVERED | ALREADY_MET | `skills/implementaudit/references/audit-playbook.md`, child-agent fixtures. |
| IMP-11 | issue publication deferred behind flag. | `--issues` flow. | Stronger boundary: no issue creation without explicit publication gate. | COVERED | ALREADY_MET | `skills/implementaudit/references/plan-lifecycle.md`. |
| IMP-12 | executor isolation through worktrees. | `execute <plan>` closing loop. | Adopted as execute isolation route plus unsafe fallback block. | SURPASSED | STRENGTHENED | `fixtures/audit-object-routing/execute-dispatch-isolation.md`. |
| IMP-13 | review result before merge. | Closing loop review section. | Adopted as child/subagent review evidence only and no hidden merge. | COVERED | ALREADY_MET | `skills/implementaudit/references/child-agents.md`. |
| IMP-14 | Reconcile DONE/BLOCKED/TODO plans. | Closing loop reconcile section. | Adopted into run-root plan lifecycle statuses. | COVERED | ALREADY_MET | `skills/implementaudit/references/plan-lifecycle.md`. |
| IMP-15 | Reject false positives. | Vet phase. | Native finding row includes rejected/deferred rationale. | COVERED | ALREADY_MET | `fixtures/audit-object-routing/finding-format-contract.md`. |
| IMP-16 | direction suggestions grounded in repo evidence. | Direction playbook. | Adapted as DMADV direction/design routing, separate from defect closure. | COVERED | ADOPTED | `skills/implementaudit/references/routing.md`. |
| IMP-17 | Quick audit pressure is scoped. | README usage and effort table. | Adopted without copying command identity. | COVERED | ADOPTED | `skills/implementaudit/references/audit-category-matrix.md`. |
| IMP-18 | Deep audit discloses coverage. | Effort table. | Adopted as deep pressure and omitted-surface disclosure. | COVERED | ADOPTED | `fixtures/audit-object-routing/deep-pressure-disclosure.md`. |
| IMP-19 | Category fanout across nine domains. | Audit playbook. | Adopted into native category matrix with DMAIC/DMADV routes. | COVERED | ADOPTED | `skills/implementaudit/references/audit-category-matrix.md`. |
| IMP-20 | Subagents receive playbook and hard rules. | Audit phase instructions. | Adopted as child-agent review template and report contract. | SURPASSED | STRENGTHENED | `skills/implementaudit/templates/child-agent-report.md`. |
| IMP-21 | Plans have dependency ordering. | Plan index template. | Adopted by ROADMAP/STATE phase dependency fields. | COVERED | ALREADY_MET | `skills/implementaudit/templates/ROADMAP.md`. |
| IMP-22 | No source mutation by advisor. | Hard Rule 1. | Rejected as default identity because IMPLEMENTAUDIT implements under authorization. | REJECTED_WITH_REASON | REJECTED_INVALID | Audit-governed implementation is the project identity. |
| IMP-23 | Source writes only under root `plans/`. | Plan output rules. | Rejected as canonical surface; run roots avoid clobbering and carry full substrate. | REJECTED_WITH_REASON | REJECTED_INVALID | `.IMPLEMENTAUDIT/runs/<id>/` remains canonical. |
| IMP-24 | Issue publication with `gh issue create`. | `--issues` section. | Deferred because publication is a separate public gate and the user explicitly did not authorize implementing `--issues`. | DEFERRED | DEFERRED_OWNER_DECISION | Plan lifecycle keeps issue publication deferred. |
| IMP-25 | Branch audit separates introduced/pre-existing. | Branch variant. | Adopted as branch/diff behavioral contract. | COVERED | ADOPTED | `fixtures/audit-object-routing/branch-diff-classification.md`. |
| IMP-26 | Review-plan critiques existing plans. | Invocation variant. | Adopted as audit-object review route, not a command identity. | COVERED | ADOPTED | `skills/implementaudit/references/plan-lifecycle.md`. |
| IMP-27 | Executor report has COMPLETE or STOPPED. | Closing loop report format. | Adopted as review evidence shape. | COVERED | ADOPTED | `fixtures/audit-object-routing/transcripts/execute-preflight-contract-transcript.md`. |
| IMP-28 | Plans include maintenance notes. | Plan template. | Already enforced in phase validator and new plan-quality checker. | SURPASSED | STRENGTHENED | `tests/plan-quality-contract.test.sh`. |
| IMP-29 | Security findings avoid runnable misuse details. | Security playbook. | Already covered by defensive security wording and secret redaction rules. | COVERED | ALREADY_MET | `skills/implementaudit/references/audit-playbook.md`. |
| IMP-30 | Improve ships no test harness. | Zip file inventory. | Rejected as a capability row because it is an observation only, not a runtime requirement; no runtime claim is made from the absence. | REJECTED_WITH_REASON | OBSERVATION_ONLY | No scripts/tests in comparator zip; source proof only. |
