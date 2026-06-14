# Supergoal Comparator Matrix

Source: attached `supergoal-main(3).zip`, SHA-256
`6E03BEF4CF02C33C0C93961D4EF5779E3E31C39CC966D362D0CBF0BB161537CC`.

Canonical status vocabulary: SURPASSED, COVERED, REJECTED_WITH_REASON,
DEFERRED, OWNER_DECISION, UNVERIFIED, FAIL.

Detail status vocabulary: ADOPTED, ALREADY_MET, STRENGTHENED, SUPERSEDED,
REJECTED_INVALID, DEFERRED_OWNER_DECISION, OBSERVATION_ONLY.

| ID | Comparator claim | Verified source/evidence | IMPLEMENTAUDIT verdict | Canonical status | Detail status | Closure evidence |
|---|---|---|---|---|---|---|
| SG-01 | namespaced run roots avoid planning-artifact clobbering. | `claim-run.sh`, README, AGENTS. | Already adapted in IMPLEMENTAUDIT run roots. | COVERED | ALREADY_MET | `skills/implementaudit/scripts/claim-run.sh`, `tests/claim-run.test.sh`. |
| SG-02 | complete working tree vs baseline is the canonical comparison. | `references/repo-state-comparison.md`. | Already adapted, with run-root self-evidence exclusion. | SURPASSED | STRENGTHENED | `skills/implementaudit/scripts/repo-state.sh`, `tests/repo-state.test.sh`. |
| SG-03 | Stage 6 self-critique catches plan weakness. | `SKILL.md` Stage 6a. | Already native and now plan-quality checker-backed. | SURPASSED | STRENGTHENED | `scripts/check-plan-quality-contract.sh`. |
| SG-04 | Stage 6.5 pre-flight avoids baseline thrash. | README and SKILL Stage 6.5. | Already native. | COVERED | ALREADY_MET | `skills/implementaudit/SKILL.md`, `scripts/check-planner-stages.sh`. |
| SG-05 | single ready-to-paste /goal handoff. | Goal reference and README. | Native goal handoff exists, with audit-governed identity. | COVERED | ALREADY_MET | `skills/implementaudit/references/goal-format.md`. |
| SG-06 | final audit before completion. | PROTOCOL final audit. | Already native; completion marker ordering is stricter. | COVERED | ALREADY_MET | `tests/marker-order.test.sh`. |
| SG-07 | AUDIT_COMPLETE before IMPLEMENTAUDIT_RUN_COMPLETE. | Supergoal uses analogous order. | Already native. | COVERED | ALREADY_MET | `fixtures/simple-audit/EXPECTED-TRANSCRIPT-SKELETON.md`. |
| SG-08 | claim-run comparator test passes. | `tests/claim-run.test.sh` raw zip: 23/23. | Comparator evidence accepted; native test already present. | COVERED | ALREADY_MET | Local comparator smoke plus native `tests/claim-run.test.sh`. |
| SG-09 | repo-state comparator test passes when git exists. | Raw zip 46/47; initialized git copy 47/47. | Comparator caveat classified; native repo-state test passes pre-patch. | SURPASSED | STRENGTHENED | Audit ledger records environmental rerun. |
| SG-10 | memory writeback privacy boundary. | SKILL memory rules. | Already native via bounded continuity and no-secret rules. | COVERED | ALREADY_MET | `skills/implementaudit/templates/PROTOCOL.md`, continuity fixtures. |
| SG-11 | Stage 0 detects active runs. | SKILL Stage 0. | Native Stage 0 detects prior run state and optional tooling. | COVERED | ALREADY_MET | `skills/implementaudit/SKILL.md`. |
| SG-12 | Planning coexistence warning distinguishes planning from execution. | AGENTS gotcha. | Adopted as run-root and worktree safety wording. | COVERED | ADOPTED | `skills/implementaudit/references/planning-depth.md`. |
| SG-13 | Greenfield intake walks material categories. | SKILL Stage 1. | Already native through routing and planning-depth. | COVERED | ALREADY_MET | `skills/implementaudit/references/routing.md`. |
| SG-14 | Brownfield asks only true gaps. | SKILL Stage 1. | Already native. | COVERED | ALREADY_MET | `fixtures/routing/brownfield-zero-question-recon/EXPECTED.md`. |
| SG-15 | Phase count is adaptive, no fixed cap. | Phase-design reference. | Already native and checker-protected against terminal caps. | SURPASSED | STRENGTHENED | `scripts/check-no-terminal-cap.sh`. |
| SG-16 | Last phase is Polish & Harden. | Phase-design reference. | Adopted as optional terminal rule with explicit rationale if skipped. | COVERED | ADOPTED | `fixtures/phase-design/polish-harden.md`. |
| SG-17 | Phase specs include transcript markers. | `templates/phase-goal.txt`. | Native marker vocabulary is richer. | SURPASSED | STRENGTHENED | `skills/implementaudit/templates/phase-goal.txt`. |
| SG-18 | validate-phase is grep-light. | Comparator script readback. | Superseded by IMPLEMENTAUDIT non-placeholder validator, which is stronger. | SURPASSED | SUPERSEDED | `skills/implementaudit/scripts/validate-phase.sh`. |
| SG-19 | Fixed three-strike handoff exists. | Supergoal failure protocol. | Rejected as terminal cap; native Andon is blocking-condition based. | REJECTED_WITH_REASON | REJECTED_INVALID | `skills/implementaudit/references/transcript-contract.md`. |
| SG-20 | Capped three audit rounds exist. | Supergoal final audit. | Rejected as terminal cap; native audit loops to closure or audited handoff. | REJECTED_WITH_REASON | REJECTED_INVALID | `scripts/check-no-terminal-cap.sh`. |
| SG-21 | Cleanliness greps inspect added lines. | Phase-design and PROTOCOL. | Already native, with added-line checker and run-root exclusion note. | SURPASSED | STRENGTHENED | `scripts/check-added-lines-clean.sh`, repo-state test. |
| SG-22 | Deliverable check parses ROADMAP. | PROTOCOL final audit. | Already native through audit object and repo-state deliverable checks. | COVERED | ALREADY_MET | `skills/implementaudit/templates/PROTOCOL.md`. |
| SG-23 | `PROTOCOL.md` and helper copied into run root. | Stage 7. | Already native and package self-contained. | COVERED | ALREADY_MET | `skills/implementaudit/templates/PROTOCOL.md`, package tests. |
| SG-24 | Run root placeholders must be substituted. | Stage 7 and CLAUDE gotcha. | Native templates preserve concrete `{{RUN_ROOT}}` substitution requirement. | COVERED | ALREADY_MET | `skills/implementaudit/templates/phase-goal.txt`. |
| SG-25 | Slash commands fire only from user input. | README and goal-format. | Already native. | COVERED | ALREADY_MET | `skills/implementaudit/references/goal-format.md`. |
| SG-26 | Installed package has README/LICENSE/CHANGELOG outside payload. | Zip inventory. | Rejected as a capability row because it is an observation only; no runtime claim is made, and IMPLEMENTAUDIT deliberately excludes repo docs from payload. | REJECTED_WITH_REASON | OBSERVATION_ONLY | Package builder allows only runtime payload. |
| SG-27 | LICENSE exists in comparator. | Zip inventory. | Owner decision because this repo does not add a license without owner selection. | OWNER_DECISION | DEFERRED_OWNER_DECISION | AGENTS/README license boundary. |
| SG-28 | Public install docs are strong. | Comparator README. | Partly already met; local source milestone does not claim new publication. | COVERED | ALREADY_MET | README install sections. |
| SG-29 | Codex manual install is a one-way copy. | Comparator README/CLAUDE. | Already native; no auto-update claim. | COVERED | ALREADY_MET | README and changelog upgrade notes. |
| SG-30 | Pre-flight may be bypassed only by user. | Stage 6.5 menu. | Native pre-flight boundary preserved. | COVERED | ALREADY_MET | `skills/implementaudit/SKILL.md`. |
| SG-31 | Audit coverage line warns on trust-prior-heavy runs. | Goal-format reference. | Native trust-prior counts already exist; coverage remains evidence-bound. | COVERED | ALREADY_MET | transcript contract and fixtures. |
| SG-32 | Active runs in same tree are unsafe for parallel execution. | Stage 0 coexistence notice. | Native owner/source and worktree boundaries cover this. | COVERED | ALREADY_MET | `skills/implementaudit/references/planning-depth.md`. |
| SG-33 | Stale run-root evidence can overclaim closure. | User correction plus comparator repo-state lesson. | New stale-proof checker labels run-root evidence historical non-current unless validated. | COVERED | ADOPTED | `scripts/check-proof-run-currentness.sh`. |
