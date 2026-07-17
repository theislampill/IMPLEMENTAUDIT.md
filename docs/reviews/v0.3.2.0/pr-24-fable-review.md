# Fable review of PR #24 — Long-running/background command lifecycle and diagnostic retention

## Provenance statement

This review was produced end to end by **Claude Fable 5** (model id
`claude-fable-5`) on 2026-07-17 (session 04/16). The harness reported Fable 5
at session start and no substitution was observed before or during any
mutation on this branch. The original PR #24 is treated as mixed-provenance
work; every conclusion below was re-derived from live GitHub state, exact Git
objects, current source, and executed fixtures against the contract’s
disposition rule.

## Identity proof (exact objects)

| Object | SHA |
|---|---|
| PR #24 head (`feat/i2-background-contract`) | `4f8736772a4a280a3df18d98123f4449a949c4f6` |
| Merge commit on `main` | `6edf6b9b812b3863718b9eeadf3e15333f1aed95` |
| Merge base (parent 1) | `da0ace0978d1b38a74c7100656efe5bc71387b72` |
| `origin/main` at review time | `82297b0683e6b1379bfeee7568c965c143a358d4` |

- `git diff --exit-code 4f87367 6edf6b9^2` — empty; merged tree
  byte-identical to reviewed head; `git diff --check` clean. Single commit;
  6 files, +147/−0 (PROTOCOL section, SKILL pointer, new test, CI/package
  registration, CHANGELOG).

## Issue #2 and closure review

- Issue #2 (milestone v0.3.2.0), zero comments, closed 2026-07-17T13:44:00Z
  by merge linkage. `updatedAt == closedAt`, so the full current body —
  including **both** amendment blocks (2026-07-16) — predates the merge.
- CI at merge executed the new test (registered in `validate.yml` and both
  verify-package registries).
- Acceptance adjudication against the amended criteria (“contract section
  present AND all six transition fixtures pass” + Amendment 2’s retention
  fixture):
  - Contract section, seven-token state model, missing-marker rule, abort
    containment, and the Amendment-1 suspicion-not-proof rule: **present
    and verified by execution**.
  - Six state-transition fixtures: **present, executed, all pass**.
  - **Amendment 2 (diagnostic-retention-before-cleanup): entirely absent
    from the merged bytes** — zero occurrences of any retention/purge/
    scan-then-retain language in the merged PROTOCOL, SKILL.md, or the
    test, and no retention fixture exists (Finding 1). The PR body says
    “the owner amendment” (singular) — it implemented Amendment 1 only,
    while claiming `Closes #2`.
- Supersession: no later commit touched the test; no later PR added
  retention language anywhere in PROTOCOL.md (verified by grep on current
  `main`). The gap persisted until this review. SKILL.md budget claim at
  merge (393 lines / 18,180 bytes) verified byte-exact.

## Invariant adjudication (packet checks 1–6)

1. **Six required states distinguishable** — the product model carries
   seven tokens (`running`, `succeeded`, `failed`, `aborted`,
   `terminal-state-unverified`, `contaminated`, `infrastructure-failed`);
   each is produced by a distinct executed fixture. CONFIRMED.
2. **Missing completion evidence never defaults to FAIL or PASS** —
   CONFIRMED and sharpened: a chain with `exit=0` recorded but no
   `chain.done` classifies `terminal-state-unverified` (the disposition
   rule checks the marker before the exit), now pinned by a new fixture.
3. **Infra signatures = suspicion, not proof** — normative text present
   (“grounds to SUSPECT infrastructure, not proof”, producer
   countermeasures “PROHIBITED until the run’s origin is classified”);
   asserted by the test; an ambiguous-origin fast-fail fixture stays
   `terminal-state-unverified`. CONFIRMED.
4. **Abort records exactly which owned work may be contaminated** —
   containment rule kills only the owned tree; the contamination fixture
   names the affected sibling (`siblings=lane-B`). CONFIRMED.
5. **Secret-scanned diagnostics retained before destructive cleanup** —
   **NOT IMPLEMENTED in the original PR** (Amendment 2). Fixed on this
   branch (Finding 1).
6. **No automatic rerun or hidden replacement call** — the contract is
   prose + markers only; no rerun/replacement language or machinery is
   introduced anywhere in the diff. CONFIRMED.

## What was executed (evidence)

- `bash tests/background-chain-contract.test.sh` — green at current `main`
  (section + vocabulary + 6 transition fixtures).
- Packet robustness cases against the contract’s disposition rule
  (`classify()` extracted verbatim and driven with disposable chain dirs):
  - Start marker without terminal marker → `terminal-state-unverified`.
  - Host exits (`exit=0` recorded) but marker absent (child may continue)
    → `terminal-state-unverified`, never `succeeded`.
  - Ambiguous simultaneous fast failure, no classification recorded →
    stays `terminal-state-unverified`, never producer-failed.
  - Interrupted run later produces terminal host evidence → truthful
    reclassification `terminal-state-unverified` → `failed` on re-read.
  - Abort with subset contamination → `contaminated`, sibling named.
  - Cleanup-removes-only-diagnostic → **not preventable by the merged
    contract** (no retention rule existed); covered by the fix.
- Post-fix: extended test RED against the unfixed PROTOCOL
  (“retention-ordering rule missing”), GREEN after; all 53 repo suites
  green; `verify-package.sh` ok; `git diff --check` clean.

## Findings by severity

**Finding 1 — MEDIUM (unimplemented owner amendment; closure overclaim;
fixed).** Amendment 2 (2026-07-16) added a normative
diagnostic-retention-before-cleanup invariant with a required fixture
(failing pre-admission host, planted secret in stderr → secret absent from
retained bytes, diagnostics present, terminal state recorded). The merged
bytes contain none of it — no contract text, no fixture — yet the PR
closed the issue. In the project’s own (session-02-reviewed) taxonomy this
is a `false-closure` instance: the closure claim collapsed an unresolved
amendment into “resolved”. The real incident motivating the amendment
(diagnostics lost to cleanup ordering, cohort left unfanned) is exactly
the class the contract exists to prevent.

**Finding 2 — LOW (regression hardening).** The
missing-completion-evidence invariant held under execution but had no
fixture for its sharpest form (exit recorded, marker absent — the
host-exits-child-continues shape). Pinned by a new fixture so
marker-before-exit precedence cannot silently flip.

**Finding 3 — INFO.** Everything else in the PR body reproduced exactly:
state model, fixtures, suspicion-not-proof amendment, budget
(393/18,180), dual registration, CI execution at merge.

## Corrections made (this branch)

Product payload bytes changed: **yes** (PROTOCOL template), plus its test:

1. `skills/implementaudit/templates/PROTOCOL.md` — point 6 added to the
   background-commands section: diagnostics are secret-scanned and
   RETAINED before any destructive cleanup, at every failure stage
   including pre-admission; purging is satisfied by
   scan-then-retain-then-purge ordering, never by deleting the only
   failure evidence.
2. `tests/background-chain-contract.test.sh` — Amendment 2 fixture
   (planted `sk-ant-…` secret in a pre-admission stderr tail; asserts
   secret absent from retained bytes, diagnostics survive purge, terminal
   state recorded), the exit-without-marker fixture, and two prose
   assertions for the new contract text. RED against unfixed PROTOCOL,
   GREEN after.

## Residual risks and nonclaims

- The contract is prose + fixture-encoded disposition; no runtime
  enforces it mechanically (issue non-goals: no watchdog, no runner). The
  eval harness’s own retention behavior (raw-stream preservation,
  quarantine-not-delete) was separately verified in session 01.
- Whether the contract reduces real recovery time/misclassification is
  unmeasured until the #9 evaluation — the issue’s own evidence limit.
- The retention fixture demonstrates the ordering rule on synthetic
  bytes; it does not execute a real host failure.

## Verdict

**CONFIRMED_WITH_FIXES.**

The background-command contract as merged is real, coherent, and its
disposition rule survived all executable robustness cases — but the PR
closed issue #2 with Amendment 2 (retention-before-cleanup) entirely
unimplemented. The missing invariant and its required fixture are added
minimally on this branch; the state model, missing-marker rule,
containment, and suspicion-not-proof semantics are confirmed as merged.

Integrator notes: touches `skills/implementaudit/templates/PROTOCOL.md`
(payload — release-asset hash changes at integration),
`tests/background-chain-contract.test.sh`, and this report. No overlap
with sessions 01–03 branches except distinct reports under
`docs/reviews/v0.3.2.0/`. If a later review session also edits the
PROTOCOL background section, merge this branch first (purely additive
point 6).
