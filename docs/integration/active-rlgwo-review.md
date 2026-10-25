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
