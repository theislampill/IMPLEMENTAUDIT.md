# v0.4.1 Thread-5 auto-DAG execution plan

Status: planning-only review anchor. No source implementation is admitted until this plan receives an independent cold-review PASS and the exact baseline preflight is green.

Baseline: commit `62507de00e16cc2ada0e7546273988c387a20390`, tree `6b24f9500ac00838c9e66389f3f4dfcbf2528be3`.

Live census at derivation: 93 issues, 270 issue-only comments, 58 canonical RXX through R003A, 14 open RXX (`#157,#158,#161,#163,#196,#197,#198,#200,#207,#209,#211,#214,#215,#216`), zero open PRs.

Derived population: 68 total cells, comprising 10 control/planning cells and 58 execution cells. Exactly 38 execution cells are admitted implementation/action cells. The frozen Thread-4 population is not reused; two explicit cells were added by the first cold review for pre-freeze version source ownership and post-package host activation evidence, and the post-dispatch `CAM-ID1` countermeasure was added to synchronize the R0004-owned durable-identity carriers with the already-allocated live R0038-R003A population before any other cell merge.

## Acceptance boundary

Deliver one exact reviewed v0.4.1 candidate, merge it to main, publish a tag/release/assets/checksums from that main identity, independently read back hosted workflows, Pages/package portal, marketplace, isolated fresh install and public dogfood, and terminalize every live work order truthfully. Historical R0033 steer remains ancestry only; the post-publication steer is nonnormative; live GitHub/source/package state wins.

Two missed automatic compactions after generation G007D are distinct dogfood witnesses attached to the existing R0011 currentness and R0033 route owners. No intermediate receipt is fabricated and no new RXX is created for either witness. The later G0080 mechanical recovery passed, but its initially omitted R0033 decision became a third, separately preserved route-conformance witness; it was satisfied by an actual installed `audit-state` load, return to governor and G0080 re-require, again with no new RXX.

## Gate sequence

1. Cold-review this plan and the machine graph from a fresh context with distinct base/head commits and `authoring_context_reuse=no`.
2. Re-anchor live GitHub, controller/continuity, baseline worktree and process state.
3. Run focused baselines plus one patient terminal Git-for-Windows `scripts/verify-package.sh`. The earlier contained run is partial evidence only.
4. Create `thread5/v041-integration` from the exact cold-review-PASS planning head. Execute each implementation cell TDD-first in a task-owned worktree/branch, independently review it, push a draft PR whose base is the exact campaign branch or dependency stack, and merge only when dependencies/shared writers are current. `CAM-ID1` is the merge-first campaign-base repair; no other cell merge is admitted until it is reviewed, hosted-green and merged. Reject any cell PR based on `main`; `CAM-M1` is the sole main writer.
5. Compose one exact source/package join, run installed behavioral cells, exact-tree review, main integration, release/public readback and tracker closure.

`R39-F1` and `R30-B0` are RED-bootstrap checkpoints, not mergeable GREEN
cells. Their exact RED diagnostics and immutable commits terminate those cells,
but `NON_GREEN_BY_DESIGN` is not CI PASS. Only the composed `R39-F7` and
`R30-J0` aggregate PRs register their new tests exactly once, turn the intended
owners GREEN and merge into the campaign branch. Public main remains unchanged.

## Admitted implementation/action cells (38)

### Host/currentness/route/DAG/control (10)

- `HC-H0` R003A binding core: add `host-session-binding.md`, `host-session-binding.py`, contract tests/fixtures and narrow continuity/governor routes. Prove two-session/worktree isolation, CAS, stale/foreign refusal and retention-safe GC.
- `HC-H1` R0011 compact interlock: add Codex `SessionStart(source=compact)` adapter, exact hook packaging and tests. It only resolves a current R003A binding and invokes canonical continuity invalidation; no child route or closure. This cell proves source/package behavior, not an actually fired host event.
- `HC-H2A` R0033 route decision/obligation: add canonical `PENDING|NOT_REQUIRED|REQUIRED` state, scoped expiry and CAS machinery plus tests.
- `HC-H2B` R0033 transaction instrumentation: prove full child bytes+packet delivery, same live return, post-return reread/currentness and one governor decision. Paths, hashes, prose, files and simulated reasoning never satisfy it.
- `HC-H3` audit-implement evidential-support v2: add exact non-release proposition states with v1 compatibility and neutral held-outs, without fifth child or authority.
- `HC-H4` R0035 native graph compiler: derive complete node/edge/writer/resource/authority/evidence population, route blockers, selective invalidation and all-settled JOIN while retaining the serial cheap path and legacy fallback.
- `HC-H6` R0036 SubagentStart/Stop sensor: bind exact host/session/agent/task to parent-owned lanes and nodes; observations never establish result, PASS or JOIN. This cell proves source/package behavior, not an actually fired host event.
- `HC-H7A` R0037 turn-disposition core: distinguish valid terminal closure, audited handoff, nonterminal yield and no object; unsatisfied route obligations block.
- `HC-H7B` R0037 Stop adapter: thin host translator into H7A with supported/disabled/untrusted fallbacks and no agent prison. This cell proves source/package behavior, not an actually fired host event.
- `HC-H8` terminal-cap repair: reject finite retry-count stop/handoff wording while preserving ordinary retry prose, strike/strikes/CrowdStrike and explicit no-cap denials.

`HC-H5` PreToolUse is deferred unless every supported-host, binding, route, graph/node, writer/resource/effect and executor predicate is exact. It is not in the 38 implementation count.

### R0038 operational evidence (10)

- `C01` strict canonical snapshot schema/loader.
- `C02` repository/package/registry and bounded Python-AST positive collectors.
- `C03` read-only binding/route/graph native-owner projection.
- `C04` evidence/failure/Andon/residual/recovery projection.
- `C05` separate Git/package/release/public layers and bounded read-only refresh.
- `C06` deterministic compile and atomic old-complete-or-none publication.
- `C07` six deterministic status/query/why families.
- `C08` deterministic diff/export without a permanent index.
- `C11` real helper route/test/registry/package registration after R001E final population logic.
- `C12` hostile path/content, trust, crash, portability, offline and resource bank.

Primary files: `operational-evidence.md`, `operational-evidence-schema.json`, `operational-evidence.py`, `fixtures/operational-evidence/**`, `tests/operational-evidence-contract.test.sh`, plus narrow governor/reference/helper/registry routes. C00 intake, C13 dogfood and C14 public review are evidence cells. UI/SSE, annotation, foreign-repo proof, index, R0038 host adapters and Madge/Knip adapters are deferred.

### R0039/R0030 (10)

- `R39-F1` freeze semantic RED/algebra/test/fixture matrix.
- `R39-F2` deterministic undiscoverable draft/archive.
- `R39-F3` reader-first legacy/pointer/marker/receipt migration matrix.
- `R39-F4` expected-old CAS, winner/loser quarantine and crash recovery.
- `R39-F5` exact rotation provenance/invalidation/successor epoch.
- `R39-F6` immutable generation + pointer CAS without cyclic future receipt.
- `R39-F7` v3 receipt, permanent first-migration marker and pointer+v3 currentness JOIN.
- `R30-B0` shared immutable RED harness for D48-C02 and D48-C04.
- `R30-P34` bounded retry/recovery admission requiring semantic eligibility, deadline/queue policy, downstream capacity and recovery headroom.
- `R30-P37` pointer-aware generation plus immutable target fence at the cooperating mutation sink.

R0039 F0 is re-anchor evidence, F9 is exact-tree review and R30-J0 is the focused join. P53 remains owner-decision deferred with no implementation/release burden.

### Base/package-budget/security/version cells (8)

- `CAM-ID1` R0004 live durable-identity allocation sync: update the package-owned Rockstar high-water through R003A while preserving the historical decimal-alias ceiling through ordinal 55, repair maintained canonical spellings and merge first before every other cell.
- `B-P3` R001F pre-allocation admission and complete current Rockstar collision/genealogy test.
- `B-P4A` R0022 affected-evidence verifier selection from semantic owners and consumers, not filenames/diff size.
- `B-P2` conditional MKH-001 retirement of only `scripts/check-workflow-structure.py`, after immediate exact-current no-caller/no-owner/no-consumer/replacement proof; otherwise no deletion.
- `B-P1` R001E exact executable package-member to route/classification set equality for canonical and standalone, with unknown type, N-1/N+1 and count-substitution controls.
- `B-P4B` R0021 real governor reserve under the unchanged 22,000-byte ceiling after all governor edits, with moved-trigger semantic preservation.
- `B-P5` R002E native conditional security profile: bounded adversary/exclusions, trust/identity, authority/privilege, provenance, assurance limits, containment/revocation/recovery/trust restoration and cheap path.
- `PKG-VERSION` one generator-first source writer for runtime `0.4.1` and release family `v0.4.1.0` across all five skill metadata files, Codex/Claude manifests, package contract, installers, checkers, tests and maintained docs. It lands before candidate freeze and before B-P4B's final governor-byte/budget receipt.

R002D `B-P6` is decision/evidence only. Source mutation is `NO_CHANGE` unless an exact current architecture-caused RED survives all live exclusions; admitting such a delta recompiles the graph.

## Key dependency path

```text
HC-E0(done) -> H0 -> H2A -> H2B -> H4
H0 -> H1,H6
H2A -> H7A -> H7B

R38-C00 -> C01 -> C02,C04,C05
C01 + H0 + H2B + H4 -> C03
C02+C03+C04+C05 -> C06 -> C07 -> C08

R39-F0 -> F1 -> F2 -> F3 -> F4 -> F5 -> F6 -> F7
R30-B0 -> P34
R30-B0 + R39-F7 -> P37
P34 + P37 -> R30-J0

CAM-ID1 -> all other cell merges
B-P3 + all executable-adding cells -> B-P1
B-P1 + R38-C08 -> R38-C11
B-P1 + R30-J0 + R39-F7 + R38-C11 + all version-bearing feature owners -> PKG-VERSION -> B-P4B
B-P4A -> B-P5
B-P3 + B-P4A -> B-P6
```

All admitted source/qualification cells then join at `J-PKG`. `HC-E1_HOST_ACTIVATION` follows the frozen package and separates documented support, packaged membership, isolated installation, enabled state, trusted exact hook-definition hash and actually fired SessionStart/SubagentStart/SubagentStop/Stop events. A truthful disabled/untrusted/unsupported/standalone/Claude result yields `HOST_CLAIM_WITHHELD`; source tests never substitute for host evidence. R39-F9 and installed behavioral cells B-F1/B-F2/B-F3 precede final candidate qualification.

The exact terminal projection is:

```text
J-PKG -> HC-E1_HOST_ACTIVATION -> CAM-Q1 -> CAM-M1 -> CAM-R1
      -> CAM-P1 -> R38-C14 -> CAM-I1 -> CAM-T1
```

P05 is candidate qualification only. P06 is main integration then
publication-only release. P07 is independent public readback, R0038 public
review, tracker evidence/closure and terminal census. A phase-projection check
rejects tracker closure before main/release/public readback or any dependency
contradiction with this chain.

## Shared writers

- Governor/child/route: host H0-H7, R0039 reader/currentness work and B-P4B serialize.
- Continuity/ref namespaces: H0/H1/H2A/H7, R0039 F3-F7 and P37 serialize.
- Planning/action-selection: B-P4A, B-P5, R30-P34 and H4 serialize by exact hunk.
- Helper reachability: B-P1 is final population owner; R38-C11 consumes it.
- Validation registry and package/release surfaces: RED checkpoints are unmergeable; R39-F7/R30-J0 own exact-once GREEN registration; PKG-VERSION is the one version source writer; J-PKG freezes the candidate.
- GitHub main/issues/tag/release/public surfaces: one exact external writer with post-state readback.

## Initial post-preflight dispatch

Logical READY cells are H0, H3, H8, C00, F0, R30-B0, B-P3, B-P4A and B-P2. H0 and H3 collide on the governor, so dispatch H0 first and keep H3 resource-blocked. The first collision-free set is H0, H8, C00, F0, R30-B0, B-P3, B-P4A and B-P2.

## Exact package/release tail

The composed join must run focused owner gates, R30-J0, validation registry, terminal package verifier, reproducible plugin/standalone builds, source/member/inventory parity, R001E final set equality, unchanged R0021 caps/reserve, rebuilt 658-row retained evidence, and isolated install/update/rollback/readback. Freeze commit/tree/artifact/checksum/install identities before behavioral review. Any tracked source change after freeze invalidates qualification and requires a successor candidate.

Final candidate review separately verdicts R0039, R002C, R002D, R002E, R0038 and every other owner. Merge only that exact tree to main. `CAM-R1` performs no tracked source mutation: publish `v0.4.1.0` only from unchanged verified main. Require reviewed candidate commit/tree = public main commit/tree = peeled tag commit/tree and bind archive/package versions to it. Independently read all release/asset/workflow/Pages/marketplace/install/public legs, then post/read back issue evidence and close only terminal live RXX. Host issue closures require HC-E1 PASS; otherwise preserve `HOST_CLAIM_WITHHELD`. Preserve P53 and any truthful blocked/non-evidence row.

Canaries fail on a tracked source byte after freeze, a pre-CAM-M1 PR based on
`main`, a RED checkpoint treated as CI PASS, duplicate/missing registry entries,
or a governor version-byte mutation after B-P4B. The repaired sequence must
rerun B-P4B and bind its receipt to the final governor bytes.

## Rollback and STOP

Every branch is reversible before external publication. R0039's permanent migration marker is never deleted; after pointer migration, compensation uses only the proved pointer/v3 path. Failed behavioral evidence is preserved and evaluators are not weakened. Immutable public mistakes require a truthful successor, not rewrite. Stop and rederive affected cells on any source/tree/dirty drift, live RXX change, controller/currentness/route/pointer drift, hook trust/schema change, writer/registry change, package/member/budget/install/public drift, ActiveGraph identity change, new MKH owner/caller, P53 decision or deferred-surface admission.

## Cold-review challenges

1. Determine whether every one of the 38 action cells is independently schedulable by owner, test and rollback rather than a ceremony-only split.
2. Verify that folding HC-J, R39-F8 and B-J1 into one `J-PKG` does not erase separate issue-owner acceptance verdicts.
3. Verify that `R38-C08 -> B-P1 -> R38-C11 -> PKG-VERSION -> B-P4B -> R38-C12` removes the helper/package-budget/version cycle while leaving B-P1 as final executable-set owner and B-P4B as final governor-byte writer.
