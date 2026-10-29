# Independent cold review of composite source wave 1

Disposition: **GAP-REVISE for the frozen publication packet**, limited to the concrete checker portability repair and two public-record corrections below. After those narrow corrections and affected validation, the reviewed source is suitable for the commissioned **draft source PR**. It is **not merge-ready**, package-qualified, native-qualified, or original-issue acceptance. This is ordinary independent engineering review, authority NONE; no native audit-assess admission is claimed.

## Exact subject and scope

- Packet: `review-subject/REVIEW_PACKET.json`, SHA256 `1135f0efc167664e4f47bcb6a24f52ef80c2b81bc38db9a70dc34ad7f5273e5f`.
- Engineering HEAD: `55b46ac762aa351e36ccd80da8eadd13f5b86e3e`; tree: `106979b17fe1a33e9128d1ea958c7e9d5c16b3f6`.
- Accepted main: `e78f7cb21af4197d490f10bc95917a4c75f748aa`.
- All three document snapshots match their packet hashes. At entry and the last pre-correction source readback, the index/tracked worktree were unchanged; the only status entry was the pre-existing untracked `docs/integration/` directory. The final report check observed the root's pending modification to `scripts/check-helper-reachability.sh`; HEAD/tree remain frozen as above. That new delta is outside this review, and the reviewer changed no tracked source.
- Read the applicable repository AGENTS.md, corrected commission, execution plan, report/adoption/dependency snapshots, material merge resolutions, repair commit, and focused evidence. Reviewed combined seams and public claims; did not purport to independently requalify all inherited donor behavior across 231 paths.

## Findings and minimal fixes

### F1 — P2: make the new shell-launcher fingerprint independent of the Python AST schema

`scripts/check-helper-reachability.sh:403` hashes `ast.dump()` and compares it with one fixed digest. The admitted subject's launcher contains FunctionDef nodes. The local interpreter is CPython 3.11.9, whose FunctionDef fields have no `type_params`; Python 3.12's empty `type_params` field changes the serialized dump for unchanged source. `.github/workflows/validate.yml:11` uses ubuntu-latest and does not pin 3.11. Consequently an otherwise unchanged selected launcher can fail reachability on a different supported interpreter.

The root independently identified and admitted this correction during review. I confirmed the exact fingerprint implementation, local AST fields, and unpinned workflow; I did not execute CPython 3.12 here. Minimal repair: use a version-stable representation of the reviewed launcher, retain exact companion size/hash binding, and retain refusals for removed digest checking, altered compiled buffer, and changed selected owner. The root's proposed lexical-token representation is pending outside this frozen review. Do not describe it as reviewed or passing at 55b46ac7.

### F2 — P2 public-record omission: name the retained original-registry source gates explicitly

The report's R0035 residual at `docs/integration/active-rlgwo-composite-20261025.md:51` and continuation at line 90 identify Windows `fcntl` and POSIX qualification, but do not explicitly identify the independently reproduced earlier source gate for retained finite/prefix profiles. The selected current registry hashes to `65c7b6939c7bf9396f83cdad58c735cabbc7e28232ceff816e7a8909bf625878` and contains 119 nodes / 91 tests. `scripts/qualify-work-graph-finite-leaf.py:920` and `scripts/qualify-work-graph-prefix.py:257` retain registry `77f26397b276fa1b6e494558d1796cb4c43d14b1e1a6755e68f542cdc4c37698`; cheap direct selector calls refuse the current registry before execution. Evidence: `review-controls/historical-profile-probes.json`.

These are correct retained exact-source guards, not missing native authority and not permission to replace 117 with 119 globally. The original live registry harness also retains its 89-test expectations at `tests/work-graph-registry-cases.py:404`, line 437 and line 469, behind those guards. Minimal publication correction: state that these historical profiles remain usable only on their selected source and that current combined finite-profile qualification needs an explicitly reviewed new mapping/profile or an exact historical subject. Preserve original117/89 obligations and avoid presenting a POSIX rerun alone as sufficient. No automatic gate broadening or full replay is requested.

### F3 — P3: correct the projection-custody test population

`docs/integration/active-rlgwo-composite-20261025.md:46` says ten tests, nine executed and one skipped. The retained `projection-custody.log` says **11 tests, 10 executed and one skipped**. The root independently noticed the same mismatch. Correct the row without changing any qualification claim.

## Independently checked evidence

- Rebuilt Git tree maps: all 231 affected-path adoption rows, main/donor/selected blobs and modes match; the 1,314-path unchanged-main complement matches. Classifications are 205 unchanged donor, 16 combined reconciliation, and 10 integration repair/addition.
- Recomputed every native-runtime and route-graph manifest file/core-dependency size and SHA256: no mismatch. Native overlay validator, hot projection and rotator exactly match selected core. Peer/core shells have different surrounding responsibilities but contain the same guarded companion-launcher code.
- Derived the canonical verifier graph from current source: 119 nodes = one prelude, 25 checks, 91 tests, one final diff check and one terminal node. It matches CANONICAL_REGISTRY.json; it does not replace original117 acceptance.
- Read actual repaired archive bytes: plugin 552439 / SHA256 `2de0db665b619be3b7d1654f31911c4f536f1113a80ced95cd38252655df9679`; standalone 547836 / SHA256 `4dfed3257f91663132e6afca9db3e42c4241b5684284d3e5c837131f581a4156`. Both exceed the unchanged 456752 usable limit. No rebuild was run. The isolated-install attempt separately refused source worktree-state binding; it is not successful install evidence or an isolated proof of the capacity guard.
- Independently materialized only the eight-member native-peer overlay under review-controls and exercised its shell custody suite on the explicitly resolved Python/Git PATH: nine tests, seven executed successfully, two POSIX-only skips. The negative same-size/wrong-size/missing/hardlinked source, physical module identity, stdin/argv, caller-directory shadowing, and capture-to-compile drift controls passed. `review-controls/peer-shell-qualified.log` SHA256 `244aa6c63c584ed5c52c8dae0dc538d8a8ec823312b9b609596ac5cb7d925c7f`.
- Preserved the initial independent peer attempt separately as `review-controls/peer-shell.log`: inherited WindowsApps python3 produced download-manager stdout and three test failures, with two skips. This was an interpreter-selection failure, not qualified companion evidence. No source was changed to make it pass.
- Read the focused pending, semantic, registry, helper and rotation witnesses. Duplicate-key and exact counter controls retain pending obligations and R0039 extensions. The original pending durability harness refuses its newly combined four-source profile before controls; no crash/native JOIN qualification follows.
- Read the original14 receipt parser and native18 discriminator, the graph-owned eight-member transport, source closure checks, companion same-buffer execution and physical-path cache key. No demonstrated merge-resolution defect was found in those reviewed seams beyond F1. Historical profiles remain; no second owner or fifth child was introduced by the repair.
- `git diff --check e78f7cb2..55b46ac7` produced no whitespace error. No tracked source, index, HEAD, donor or protected state was modified by this review.

## Behaviors deliberately not judged

- Full 119-node package/verifier success, full original117 correspondence, and current historical59 coverage: not executed; old eight failures remain. Both packages are already over budget.
- Original14 Windows transport's full live owner/receipt route, authentic C5, OR, C02, physical child H0/O/U/RETURN/acceptance/DISPOSE, native JOIN and restored-current cold receiving: no admitted producers/grants or authority in this review. Imports, exact source selection and synthetic controls are not substitutes.
- POSIX locking, no-follow descriptor and symlink cases: unavailable on the selected Windows interpreter; existing skips and failures remain non-evidence for those properties.
- Successful installation or public/hosted CI: not independently executed/read here. Root publication receipts and later actual CI must carry their own identities. Archive identity alone grants no install/release credit.
- All donor research/member judgments and R0041 closure readiness: population/claimed-scope separation and the conditional recommendation were reviewed, but no independent 77/73/234-member receiving replay or entitled closure decision was made. R0041 remains only a bounded next assessment recommendation.
- General package-size impossibility: no exhaustive compression or semantic refactor proof exists. The report correctly states a limited deduplication investigation and retains a concrete future package-owner decision.

## Next operation and stop

Root alone applies F1 and the F2/F3 documentation corrections, validates only the affected fingerprint controls, freezes the successor head/doc identities, and publishes the one authorized non-closing draft PR. Report this review as bound to 55b46ac7 with a separately identified correction delta. Keep the capacity, finite-profile, pending-profile, native/authority and host blockers explicit. No main merge, issue closure, native acceptance or protected mutation is approved. Reviewer stops after this report.

## Root disposition after independent return

F1: corrected in4b681652f4106f57b6e02bcf8b9b0e771370ea04; actual checker and five targeted token-scanner controls succeeded. This correction delta is root-validated, not retrospectively included in the independent55b46ac7 review. F2: exact original117/89-test finite/prefix source guards are now explicit in the report and continuation; no guard changed. F3: report corrected to11 tests,10 executed successfully,one skipped. Root accepts the bounded review findings as resolved for the already authorized draft publication only.

All deliberately unjudged behaviors remain unqualified; no scope is silently dropped. Capacity and unknown/native effects remain explicit. No deferred minor finding remains. The next operation is the guarded integration-branch push and non-closing draft PR with exact post-publication readback.


# Finite wave 2 independent review

# Wave 2 independent review: authorization consumer correction

**Disposition: suitable for the authorized draft update. No actionable findings in this three-file increment.** This ordinary source review has authority NONE. It does not establish merge readiness, grant authenticity, native enforcement, package/install qualification, or original-work-order acceptance. The first review and the composite's existing residuals remain separate and unchanged.

## Exact reviewed subject

- Previous published integration subject: `ede32d13bd5cbde17ebaf682505656e18441b9d6`.
- New local merge: `aa9fd9fc40f3eceacc439d637e57a13d739edae5`; tree `041a6e66da93907c9b126611d28eedfccec6d971`.
- Selected PR251 increment: `326d091e06b7bbef1647b1d97f3bc84c0dae90ee`; tree `7aae6dde798ffa365a62348917d16691bba693fb`, over previously frozen `45853f9403f5ffaad100df1686fe5320f72e19b7`.
- Scope is exactly `docs/maintenance/four-rockstar-integration.md`, `skills/implementaudit/scripts/check-authorization-binding.sh`, and `tests/authorization-binding-contract.test.sh`. All three merged blobs exactly match the selected donor. Entry worktree/index were clean and HEAD/tree matched the commission.

## Behavior and tests

The change at checker lines 349–351 rejects noncanonical case variants of the `param.` prefix. Previously the case-insensitive supplied-parameter check recognized those lines while the value-validation loop skipped them. The change at lines 361–365 treats an absent or empty declared constraint as authority drift. It does not convert missing data to an unrestricted grant. Canonical literal and numeric-range behavior is preserved, including inclusive endpoints.

The three added registered regressions independently cover absent constraint, empty constraint and mixed-case prefix. Existing match/drift, intake, duplicate-key, missing-parameter and unterminated-line controls remain. Their new assertions test nonzero refusal rather than only message wording. Existing positive coverage, plus the independent exact-message checks below, prevents interpreting a universally failing helper as a successful repair.

I independently executed eight inert input cases on both exact old and merged helper buffers: missing constraint, empty constraint, `Param.object`, literal match, numeric lower endpoint, numeric upper endpoint, out-of-range numeric value, and `pArAm.object`. All **16 expected exit codes matched**. The old helper accepted all four new malformed/underbound negative examples; the merged helper returned the expected authority-drift or malformed-prefix refusal. Literal/range positives retained exit 0 with empty stderr; the out-of-range negative remained refused. No consequential command, native route, grant issuer, or `--phase` rehearsal branch was invoked.

Evidence: `review-controls/wave2/authorization-review-controls.json`, including exact stdout/stderr. The root's retained `authorization-wave2-red.log` reports the expected premerge missing-constraint failure; `authorization-wave2-green.log` reports the extended registered suite succeeded. These are separate from my eight-case differential.

Source identities independently match the new documentation:

| Helper | Bytes | SHA256 |
|---|---:|---|
| Premerge | 17469 | e2ff72034bac8317b881dcbf1180a47f6d7b64119398af2b664c47e10cdba728 |
| Merged | 17640 | 9a501a59d004068f80035cb1ea6041bb3fee655e5094b2f3eeb63d78ab108660 |

## Claim boundary and remaining limits

The appended maintenance record correctly calls this portable authorization-consumer evidence. It explicitly withholds authentication of the supplied grant, consequential execution, native enforcement, private held-out qualification, original P06/P17 or all-sixty acceptance, and whole-work-order closure. Its historical derivative/raw-packet identities were not independently requalified in this narrow review; the current helper identities and differential behavior were verified directly.

No introduced false positive was demonstrated in the selected grammar. Refusing an empty constraint and a differently cased prefix is the explicit new behavior, not a grant expansion. This review does not assert that the entire older text grammar or every authorization pathway is complete or secure. The unchanged rehearsal branch and other donor banks were not replayed.

The helper is a shipped source member, so old package sizes/hashes/install claims cannot be relabeled as current after this merge. Root must bind any later package observation to its actual new source, and preserve the existing capacity/native/owner gates. No build or heavy qualification was requested or performed here.

## Next action and stop

Root may document this exact finite wave, retain the red/green and independent control identities, and update the single authorized draft PR through its guarded ordinary publication path. This review supplies no main-merge, release, native-effect or closure authority. Reviewer stops after writing this report; no tracked repository, index, HEAD, donor, or protected-state mutation was performed.

Root received this exact three-file review and independently verified all three selected blobs and the complete authorization suite. Accepted for the owner-authorized ordinary update to draft PR255 only. All package/native/issue boundaries remain.
