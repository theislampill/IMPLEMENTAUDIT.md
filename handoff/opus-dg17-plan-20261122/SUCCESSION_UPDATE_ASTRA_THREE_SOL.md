# Succession update: Astra with three parallel Sol agents (owner-directed, 2026-11-22)

This is an **additive** update to Pro's verified handoff, commit `2f920bd7c3b70c78c8c105b486a71c8bc4b5426a` on `engineering/pro-final-20261122`. Read that handoff's `CHECKPOINT.json`, `CUSTODY_AND_GAPS.md`, `ASTRA_LAUNCH.md` and `SOL_LAUNCH.md` first.

This file changes only the **work split**: one Sol becomes three. Every authority limit, protected-operation rule, no-replay boundary and acceptance requirement in those files stays in force. Prepared by Claude Opus 5.5 (adviser). It grants no award and no authority; the owner appoints.

## Structure

| Agent | Owns | Branch prefix | Never does |
|---|---|---|---|
| **Astra** | Sole Root adjudicator, cross-cell integrator, sole writer of the results branch and PR #255, independent adjudication of Sol evidence | `engineering/astra-*` | Self-approve protected operations; certify a Sol's work without independent review |
| **Sol-DG16** | Ordinary DG16 engineering, G132 source restoration, host-route trial, readiness evidence | `engineering/sol-dg16-*` | Launch a protected G132 operation; write results or PR #255 |
| **Sol-DG17** | DG17 coverage: structural suite, model and native preparation, native Stop qualification evidence | `engineering/sol-dg17-*` | Run Codex native/model episodes without the owner's exact grant; award cases |
| **Sol-DG18** | DG18 A4/A5, OR, occurrence and retry, cold receiving, C02, N1 evidence | `engineering/sol-dg18-*` | Waive N1/R01–R09; manufacture C02 entitlement; write results |

Delegate the three Sols as subagent threads under Astra where the host supports it (for example, Codex subagents, subject to model access and concurrency). Otherwise use separate sessions that report through GitHub commits.

The three Sol agents are executors of this programme. They are **not** the plugin's four model-facing child skills.

## Rules shared by every Sol

- **GitHub-first:** push every candidate to the Sol's own branch before asking for review. Cite commit and path, never local paths.
- **Self-contained:** each Sol works from GitHub alone; no shared workspace. A durable coordination note lives on the Sol's branch: `COORDINATION.md` (current task, last commit, open escalations).
- **Escalate to Astra only at these gates:**
  1. a shared-source conflict (touching a file another cell owns, or packaged bytes);
  2. an original-contract blocker that engineering cannot settle;
  3. any protected, native or model operation (Astra prepares the owner request);
  4. a proposed original acceptance decision.
- **No self-certification:** a Sol's result is evidence. Astra adjudicates only after independent review by an agent other than the author.
- **Package budget:** about 20 bytes of headroom at `51416b2f`. Any change to shipped bytes goes through Astra.

## First executable task and stop condition, per agent

**Astra**
1. Verify every identity in Pro's `CHECKPOINT.json` against live GitHub.
2. Launch the three Sols with the addenda below.
3. Own PR #255 conflict resolution and the shared-file map.

Stop and escalate to the owner only with a plain-English, ready-to-sign request.

**Sol-DG16**
1. Decide, with evidence, whether the four missing historical source files can be recovered or must be rebuilt as labelled new engineering (Pro's `CUSTODY_AND_GAPS.md`).
2. Run one ordinary (non-protected) host-route trial: the existing G132 observer inside a digest-pinned container image on the hosted runner. Record every host check in one run, and fix the stop rule in advance. If the sandbox namespace cannot start in the container, stop and report.

Also note: run `45049052400` was refused at `REPORT_BOUND` (full report 2,589,544 bytes against 1,823,337 allowed). Fix the report size within the unchanged rules before rerunning any observer.

**Sol-DG17**
1. Read `handoff/opus-dg17-plan-20261122/DG17_LEDGER_AND_PLAN.md` on `engineering/opus-dg17-plan-20261122`. Verify it against the source; do not rebuild it.
2. Bring Astra decision proposals for the two real source gaps: the Jidoka owner (section 6) and the `audit-andon` return validator (section 8b).
3. Run `tests/run-root-validation.test.sh` on the hosted runner. It failed locally for environment reasons (section 8f).
4. Build the structural suite (Op S) on the candidate map.

Stop on any native/model need; Astra prepares the grant request.

**Sol-DG18**
1. Determine the provenance of R01–R09 from records. Its earliest trace is Pro's own "Requested frozen A4 contract" (Nov 22 transcript). Report whether it was an independent requirement or a subordinate receiving checklist.
2. One hosted Windows A4 run, one fresh process per method, with an equivalence proof:
   - same 28 methods, same order;
   - same results for the 25 that never hit the memory guard;
   - each method under 64 MiB;
   - the whole Job under 192 MiB with descendant accounting;
   - confirmation that the product runs the rotation helper as a fresh process per operation.
3. A field-by-field census of what the real project state records about N1.
4. Inspect the C02 configured issuer (scope `CONTROLLED_NONPROTECTED_FAULT_INJECTION`) and propose a disposable non-protected trial.

Stop before any protected, native or model operation, or any requirement change.

## Unchanged from Pro's handoff

- `44888568054` is SPENT_NO_RETRY.
- `301aeecd` and A4-07 are UNKNOWN_NO_REPLAY.
- Queued `43098152901` stays untouched.
- No new protected G132, native or model operation without the owner's explicit exact grant.
- No merge, release or issue closure.
- Whole-DG acceptance is 0/3.
