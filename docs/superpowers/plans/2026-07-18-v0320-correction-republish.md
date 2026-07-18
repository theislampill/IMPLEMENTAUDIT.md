# v0.3.2.0 correction and republication implementation plan

> **Executor note:** This plan is governed by `/implementaudit`. Execute phases
> in order. Do not republish while any B3 or reproducibility gate is red.

**Goal:** Transparently correct and republish `v0.3.2.0`, then freeze it and
open the separate `v0.3.3.0 — 28/28 behavioral qualification` program.

**Owner/source:** 2026-07-18 owner correction directive.
**Planned-at baseline:** `e7102711c0c514dc8478c807039c098335bb00cf`, clean,
tracking identical `origin/main`.
**Correction branch:** `fix/v0.3.2.0-b3-evidence-correction-sol`.
**Worktree:** `C:\workspace\ai\improveimplementaudit\IMPLEMENTAUDIT-correction-v0320-sol`.
**Run root:** `.IMPLEMENTAUDIT/runs/v0-3-2-0-corrected-republication-sol-5FIN9Y`.
**Provenance:** Sol.

## Scope and fixed boundaries

In scope: A1-A11 and the Program B start deliverables in the owner directive.
The private raw campaigns are read-only. The original B3 fixture is immutable.
The old public release may be deleted, issues/milestone reopened, and the tag
replaced only in the authorized order. Commit, push, PR, merge, release,
publication, public-asset install, issue creation/edit/closure, milestone
creation/edit/closure, and the one-time tag replacement are explicitly owner
authorized for this task.

Out of scope: publishing a `v0.3.3.0` release; metered API spend; model
substitution; silent retries; rewriting private raw evidence; claiming general
model superiority; unrelated repo cleanup.

## Phase 1 — Preserve and withdraw

**Files:**

- `docs/audits/archive/v0.3.2.0-correction-and-republish-report.md`
- `docs/superpowers/specs/2026-07-18-v0320-correction-republish-design.md`
- this plan and the ignored run root

**Steps:**

1. Record release ID/URL/title/body/times/Latest state, tag object/target,
   downloaded assets and `CHECKSUMS.txt`, issue/milestone state, and clean
   `main`/tag/worktree facts.
2. Hash both original seeded B3 campaign intents, ledgers, completion records,
   raw event streams, verdicts, and canonical bundle hashes.
3. Re-score all 12 event streams with the byte-identical tagged scorer and
   record the per-property matrix showing 0/12 all-true.
4. Commit and push the evidence/design/plan; open the correction PR so the
   historical record is remotely durable.
5. Delete the GitHub release (not the tag), verify it is no longer Latest,
   reopen #9/#10/#35, and reopen milestone 1.

**Verification:** remote branch/PR contains the A1 record; public release tag
endpoint returns absent while git ref remains; three issues OPEN; milestone
OPEN.
**STOP:** any A1 hash cannot be reproduced, the public release differs from the
snapshot, or remote durability is not confirmed.

## Phase 2 — B3-v1 RED and layered verdict GREEN

**Files/symbols:**

- `eval/runner.py::score_bundle`
- `eval/lib/verdict.py::build_verdict`
- `eval/lib/scoring.py::score_events` only if evidence proves a scorer defect
- `eval/test_*.py`, `tests/eval-harness.test.sh`, and new focused regression
  tests

**Steps:**

1. Add a failing regression test using a minimal authentic B3-style bundle:
   host unauthorized mutation plus scoreable events must retain all product
   property results.
2. Add negative RED cases for manufacture, erasure, incomplete-ceiling,
   unreconstructible report claim, and replay mismatch.
3. Refactor bundle evaluation so product measurements and host-safety findings
   are composed separately; add an explicit adjudication object.
4. Re-run the old B3-v1 reproducer and focused eval suites.

**Verification:** old implementation fails the new tests; corrected
implementation passes; original stored events independently reproduce the
recorded derived matrix.
**STOP:** a foundational custody gate would need weakening, a property result
could be inferred without evidence, or backward compatibility would silently
reinterpret old verdicts.

## Phase 3 — Freeze B3-v2 and prove the builder

**Files:**

- new `eval/fixtures/B3-v2/**` (never modify `eval/fixtures/B3/**`)
- `eval/README.md`, self/adversarial/host tests
- `scripts/build-release-asset.sh`
- new release reproducibility checker/test plus both validation registries

**Steps:**

1. Add B3-v2 with the six owner-required properties and decision/handoff
   semantics observable before canonical mutation.
2. Add deterministic PASS/FAIL/host-fail/incomplete negative controls.
3. Canonicalize ZIP entries, timestamps, modes, creator/platform fields,
   compression, paths, timezone, and locale effects.
4. Add a two-independent-checkout reproducibility test comparing archive hash
   and per-entry metadata/content/manifest.
5. Freeze and hash B3-v2 fixture, scorer, candidate/control products, configs,
   seed, repetitions, rules, and authorization boundary in a private campaign
   intent before any live mission.

**Verification:** all focused tests and two-checkout proof green; `git diff
--exit-code -- eval/fixtures/B3` proves B3-v1 unchanged.
**STOP:** fixture/scorer choice changes after live output is observed, or two
clean builds differ.

## Phase 4 — Corrected 12-mission B3 comparison

**Inputs:** immutable control `v0.3.1.0`; exact correction candidate; existing
owner-approved subscription configs L and O; three repetitions; interleaved
arms; no automatic retries.

**Steps:**

1. Attest exact candidate/control/model/host identities and launch the frozen
   12-mission plan.
2. Preserve every attempt and terminal record; stop on quota/auth/substitution
   and classify infrastructure origin without contaminating results.
3. Require 12/12 terminal, property results in every verdict, zero unexplained
   ERROR, zero unaccounted INVALID, and zero substitution.
4. Independently replay the raw events and compare the complete property
   matrix byte-for-byte with recorded verdicts.
5. Apply the preregistered improvement/no-regression rule. If it fails, keep
   the release unpublished and return to a bounded causal repair.

**Verification:** campaign ledger, intent hash, run hashes, property matrix,
identity attestations, and independent re-derivation recorded in the correction
report.
**STOP:** any rule ambiguity, missing property result, identity mismatch,
unauthorized canonical write, or failed preregistered release criterion.

## Phase 5 — Records, review, qualification, and merge

**Files:** README, CHANGELOG, portal sources, audit index, four v0.3.2.0 release
ledgers, correction report, release-body source, package evidence/checksums.

**Steps:**

1. Correct the historical false claim without deleting the historical record;
   replace stale mandatory-Fable-gate wording with optional future review.
2. Correct `#1-#7 + #11-#15` to twelve core contracts plus #35 separately.
3. Add the owner-specified public “What’s New” and keep structural tests,
   independent review, and live model behavior visibly distinct.
4. Run a bounded fresh-context cold review of the complete diff and evidence;
   record PASS/GAP-REVISE/BLOCKED/OWNER-DECISION and resolve every gap.
5. Run all deterministic/eval/adversarial/host/adapter/package/portal gates,
   two-checkout reproducibility, exact-head CI, and clean-scope checks.
6. Commit/push review fixes, make the PR ready, wait for exact-head CI, and
   merge only when all release-critical evidence is green.

**Verification:** correction PR merged; exact merge commit and CI checks green;
main clean/synced; no unrelated changes.
**STOP:** any release-critical test, review disposition, or exact-head check is
not green.

## Phase 6 — Corrected tag/release transaction

**Steps:**

1. Archive the old tag object/target already captured in Phase 1, delete the
   old tag ref, and create a corrected annotated `v0.3.2.0` tag at the final
   CI-green release commit with the authorized-republication disclosure.
2. Build twice from independent clean checkouts; require identical bytes and
   SHA-256; generate matching `CHECKSUMS.txt`.
3. Publish non-draft/non-prerelease/Latest with a visible correction note and
   complete old/new tag and asset hashes.
4. Download public assets to a clean location, verify hashes and metadata,
   install from the downloaded public asset, compare installed-file parity,
   and run post-install smoke.
5. Verify tag dereference, CI, release body, asset API metadata, Latest state,
   and public readback; only then close #9/#10/#35 and milestone 1.

**Verification:** every A11 readback passes. Only then print
`V0.3.2.0_CORRECTED_REPUBLISH_COMPLETE`.
**Rollback:** if publication/readback fails, withdraw the corrected release,
keep issues/milestone open, preserve the tag state/evidence, and repair before
republication; do not invent success.

## Phase 7 — Start, do not publish, the 28/28 successor

**Steps:**

1. Freeze corrected `v0.3.2.0`; make no further tag changes.
2. Create milestone `v0.3.3.0 — 28/28 behavioral qualification` unless live
   roadmap evidence assigns another version; create umbrella tracker.
3. Commit campaign intent, untouched holdout policy, 28-cell historical
   baseline, 17-cell causal ledger, cluster map, and first tranche artifact.
4. Open the first causal tranche issue/branch/PR as appropriate, but do not
   publish a successor release without a later owner decision.

**Verification:** milestone/tracker/artifacts exist and first tranche is
actively opened. Only then print `CAMPAIGN_28_OF_28_STARTED`.

## Final done condition

The corrected public release is verifiably installed and frozen, release
issues/milestone are closed after readback, the separate 28/28 program is
actively opened with frozen evidence and a first tranche, and the consolidated
owner report identifies every hash, commit, PR, matrix, provenance boundary,
and remaining risk. `AUDIT_COMPLETE` is forbidden before those conditions.
