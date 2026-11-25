# DG16 M6 ordinary-comparison packets

These packets are read-only. I ran no tests or workflows and made no commit or push. The only git commands used were show, log, diff, rev-parse, ls-tree, ls-remote, fetch, cat-file, merge-base and patch-id.

* **Subject:** `2450417a3d442e189e20ba261120aff3ed7444c6`, tree `b14577983c5e0ab05225250491efe7363945742c`. I verified this with `git rev-parse 2450417a^{tree}`.
* **Baseline:** `51416b2f`, tree `9c3913ce`.
* **A4 subject:** `71b6315c`, tree `6491fd78`.
* **Source clone:** `adv3/full/src`.
* **Ledger:** disc `HEAD:handoff/astra-dg16-dg18/m6-ledger/DG16_M6_LEDGER_V2.json`.
* **DG17 record:** `2450417a:handoff/sol-dg17-20261122/CONTINUATION.md`, cited below as "DG17 CONT".
* **Discussion:** disc `HEAD:handoff/astra-dg16-dg18/discussions/DG16-DG17-reader-bindings.md`, cited below as "RB".

Every commit in `51416b2f..2450417a` is linear (303 commits, 0 merges). The committer is always `theislampill`. Authorship can therefore distinguish only Opus-authored commits. It cannot separate DG17 from DG18 work.

---

## R35-Q03.a: shared owners unmodified, or delivered as exact integration patches

**Commands**

```
git ls-remote origin                      # 33 engineering/opus-dg16-* heads (opus_heads.txt)
git log --author=Claude 51416b2f..2450417a
git log --grep='Co-Authored-By: Claude' 51416b2f..2450417a
git show --name-status <c>                # each DG16 delta
git show <c> | git patch-id --stable      # slice commit vs DG16 branch commit
git merge-base --is-ancestor <c> a5ed001f # sol-dg17 tip
git diff --name-status 51416b2f 2450417a  # 242 paths (189 A, 53 M)
git log 51416b2f..2450417a -- <shared path>
```

**DG16 deltas inside the 2450417a slice: 14 commits.** Twelve are Opus-authored. The other two, `e2c0183c` and `2450417a`, are Opus patches recommitted by DG17.

* Each commit is patch-id-identical to its DG16 branch original.
* All 14 are ancestors of the `engineering/sol-dg17-20261122` tip `a5ed001f`.

In the table, "DG17 CONT" plus a line number means a line in the DG17 record that receives the delta.

| Slice commit | DG16 original | Files changed | Class | DG17 composition record |
|---|---|---|---|---|
| f2221468 | 7c1c45f2 | scripts/qualify-work-graph-finite-leaf.py; tests/work-graph-{custody-append,finite-entry,planner-copy}-cases.py, tests/work-graph-historical-fixture.py | a | cherry-pick; used as the DG17 n07 subject (DG17 CONT L324) |
| ba5df5ce | b3cefdd4 | scripts/operational-evidence.py, scripts/work-graph-continuity-transport.py, tests/composite-source-cases.py | a* | DG17 CONT L386 |
| 688da6db | 7a310842 | scripts/{load-work-graph-c5-executor,qualify-work-graph-c5-setup,qualify-work-graph-verifier-properties}.py; 3 test-support history files; tests/c5-{current-source-receiving,selected-source-fixture}.py, tests/composite-source-cases.py | a / c | DG17 CONT L390 ("joined once"; befb8023/a0fc7788) |
| 8d2a2918 | 3fa8e70e | operational-evidence.py, work-graph-continuity-transport.py, composite-source-cases.py | a* | DG17 CONT L434 |
| fd516dee | 01ed5098 | same three files, plus test-support/dg18-or-history/... | a* | DG17 CONT L545 (befb8023) |
| 0c986ca5 | 3f2f6336 | qualify-work-graph-{finite-leaf,prefix,verifier}.py; test-support prefix history; 4 tests | a | DG17 CONT L583 (b3055743) |
| 4fcb3386 | dfdce921 | 2 fixtures/work-graph-c5-inputs/*final-successor*.json; C5 loader, setup and properties; 4 test-support files; 3 tests | a / c | DG17 CONT L632 (9d8a09ad) |
| 878e25e2 | d3c54e78 | test-support/work-graph-registry/shared-successor-retained/.../repo-state.sh; 3 tests | a | DG17 CONT L632 |
| fe569146 | d47fe2c3 | operational-evidence.py, work-graph-continuity-transport.py, composite-source-cases.py | a* | DG17 CONT L858 (0087a545) |
| **daaa0819** | **ed892098** | **skills/implementaudit/scripts/compile-work-graph.py, source-peers/route-graph/SOURCE_MANIFEST.json, source-peers/route-graph/skills/implementaudit/scripts/{compile-work-graph,route-transaction}.py** | **b** | **DG17 CONT L858 (0087a545)** |
| b30ef328 | 3547cc13 | C5 loader, setup and properties; 2 test-support files; 3 tests | a / c | DG17 CONT L858 (0087a545) |
| 71b6315c | c7c59245 (cherry-pick) | C5 loader and setup; qualify-work-graph-verifier{,-properties}.py; scripts/work-graph-verifier-task.py; 2 test-support files; tests/c5-selected-source-fixture.py, tests/work-graph-verifier-cases.py | a / c | DG17 CONT L1907 (195158b2); L1822 |
| e2c0183c | d60798ea (cherry-pick) | work-graph-verifier-task.py, work-graph-verifier-cases.py | a | DG17 CONT L2007 (f7a5330e) |
| 2450417a | ea827457 (cherry-pick) | work-graph-verifier-task.py, work-graph-verifier-cases.py | a | sol-dg17 CONTINUATION L2032 at a5ed001f (d688ec25); RB L2651 |

The class key is:

* **a:** DG16 graph source, fixture or test.
* **a\*:** a repo-only DG16 reader-binding adapter. Its name says "continuity" or "evidence", but it is not a skills/ continuity owner. Root should confirm it is not a shared owner.
* **b:** a shared owner.
* **c:** qualification or history. The C5 loader is listed as a / c. Whether it counts as a "helper load map" is a reading for Root to make.

**Shared-owner touches in the slice: one, `daaa0819`.** It changes the route, the route-graph manifest and both compilers.

* It was published as "PROPOSAL for DG17", commit `ed892098` on `engineering/opus-dg16-t14-compiler-proposal-20261124`. The commit message says it is "for DG17 ... to adopt or reject".
* DG17 composed it patch-identically. Commit `0087a545` records the composition in DG17 CONT section "Frozen joined V18 adoption and package measurement". That section says "DG17 applied `d47fe2c3`, `ed892098` and `3547cc13` once in order".
* The Git author stays Opus. The DG17 adoption is what makes it an integration patch.

**No DG16 commit in the slice touches any other shared owner.** These include:

* `scripts/verify-package.sh` and `.github/workflows/*`
* `package/`, `scripts/package-contract.py` and the native-runtime manifest
* `skills/implementaudit/{SKILL.md,templates/PROTOCOL.md}`
* the skills/ governor, host and continuity owners: claim-run.sh, validate-run-root.sh, claim-run-rotation.py, host-session-binding.py, host-stop-interlock.py, rotate-canonical-state.py, repo-state.sh and the canonical_*.py files
* the portal and index

Every change to those paths in 51416..2450417a was authored by DG17 or Root. `.github/workflows/dg17-structural.yml` was added by DG17 in 13 commits. `scripts/verify-package.sh` was changed only by `f894aa80`.

**Branch-only DG16 shared-owner touches, outside the 2450417a slice:**

* **V03 run and review packets.** These are 05569621, d2303ee9, 5ee0c867, dd8fde10, 8f1b6db3, f067fd2d, 5ff384dd and 9006904b. They add `.github/workflows/dg16-r5-full-g2.yml` and `qualification/.../SOURCE_MANIFEST.json` on top of `2e72a912`. That workflow is absent from 2450417a. They were Root-adopted for one V03 episode and are not DG17-composed.
* **`5e4274d6`.** It touched the route-graph manifest and route-transaction.py. It was superseded and never composed. DG17 consumed `b3cefdd4` instead.
* **G132 lineage.** e6576c69, b37ca20b and 022a10f6 do not descend from 51416. They add or modify `.github/workflows/opus-dg16-g132-host-measure.yml` and `dg16-r5-g1-hosted-episode.yml`. Their operation subject is separate (G132, `b393a905`).

**First unresolved predicate after:**

* Root has not named the base. 51416b2f is used here, per `integration_base`.
* Root has not ruled on whether a\* (continuity-transport and operational-evidence adapters) and the C5 loader are outside the shared-owner list.

---

## R35-V01.c: registry obligation population at 2450417a

**Commands**

```
git diff 379581a8 2450417a -- scripts/verify-package.sh   # 0 bytes
git rev-parse {51416b2f,379581a8,71b6315c,2450417a}:scripts/verify-package.sh
git log 51416b2f..2450417a -- scripts/verify-package.sh    # f894aa80 only
git diff --name-status 379581a8 2450417a -- scripts tests  # 12 M, 0 A/D
```

**Result: the registry did not change from 379581a8 to 2450417a.**

| Subject | `scripts/verify-package.sh` blob |
|---|---|
| 51416b2f | e6a33828ee58d3aa36e8fbffefcb1186d1d948c5 |
| 379581a8 | cc4d076f4874e93f478db97675555cc373929540 |
| 71b6315c | cc4d076f4874e93f478db97675555cc373929540 |
| 2450417a | cc4d076f4874e93f478db97675555cc373929540 |

* The only registry change since 51416 is `f894aa80`, which composes the fail-closed scans and C5 selection: +26 / −15. It lies before 379581a8, where V01 was already reconfirmed.
* Twelve scripts and tests changed between 379581a8 and 2450417a. All are modified files; none was added or deleted.
* A crude grep found no glob or `find`-based test discovery in the registry. The registry names its consumers statically, for example L728 `bash tests/repo-state.test.sh`.
* Population-affecting change: none at the registry text level.
* Ledger claim confirmed: A4 covered 119 nodes on `71b6315c` with the same registry blob.

**First unresolved predicate after:** Root has not bound V01 to 2450417a. The packet is ready to hand over.

---

## R35-V02.b: applicability from 71b6315c to 2450417a

**Commands**

```
git diff --name-status 71b6315c 2450417a                 # 8 paths
git log 71b6315c..2450417a -- scripts/work-graph-verifier-task.py tests/work-graph-verifier-cases.py
git diff 71b6315c 2450417a -- scripts/work-graph-verifier-task.py   # 1 hunk
git diff 71b6315c 2450417a -- tests/work-graph-verifier-cases.py    # 1 hunk
```

**Paths changed between 71b6315c and 2450417a.** Eight paths changed, two of them handoff files. The six product and test paths are:

* `.github/workflows/dg17-structural.yml` (DG17 repin)
* `scripts/validate-audit-andon-return.py` and `tests/audit-andon-return-cases.py` (DG17 Andon)
* the deleted `test-support/.../v19-source/scripts/load-work-graph-c5-executor.py` (DG17 T10 retirement)
* the two verifier-task files

**Commits.** Only `e2c0183c` (= d60798ea) and `2450417a` (= ea827457) touch the verifier files. The blob for `work-graph-verifier-task.py` moves bccb3288 → 893d3ecd → c5dab437.

**Task hunk** at `@@ -571,12 +571,56 @@`, +44 / −0. It is **bookend validation only**:

* It adds `POPULATION_STOPS`, `POPULATION_LIMITS` and `_bookend_consistent`.
* In `summarize_read_populations` it adds a type guard, the `INCONSISTENT_BOOKEND` and `UNRECOGNIZED_SCOPE` branches, and a limits check.
* It leaves `all_obligation_rows`, the row and property emission, `property_completeness` and `read_population_evidence` untouched.

**Test hunk** at `@@ -450,12 +450,100 @@` inside `all_obligation_acceptance`, +91 / −3. It adds bookend controls. One existing oracle changes:

* The old drift control altered only the after-bookend `digest` and expected `DRIFT_DURING_OCCURRENCE`.
* It now edits one entry's sha256 and rederives the digest, so the drift is self-consistent, and still expects DRIFT.
* A digest-only edit is now `INCONSISTENT_BOOKEND`. RB L2503 gives this as the justification.

**Do valid inputs change mapping? No.**

* `read_population_evidence` emits `limits == POPULATION_LIMITS`.
* `observe_read_population` emits bookends that `_bookend_consistent` accepts: BOUNDED with rederivable entries, count, bytes and digest, or a known stop with empty or null fields.
* Valid emitter output therefore reaches the unchanged status chain. The new test line `summarize_read_populations(clean) == established["summary"]["scopes"]` asserts this.
* DG17 CONT L2007 and L2032 report that the retained A4 sidecar still derives the same 22 ESTABLISHED scopes.
* No hunk touches the property or obligation mapping for any input.

**First unresolved predicate after:** Root has not received this classification.

---

## R35-Q01.b: changed oracles and test expectations since 51416

**Command**

```
git diff --name-status/--numstat 51416b2f 2450417a -- tests fixtures
```

**31 files: 7 added, 24 modified, 0 deleted.** In addition, 27 test-support history files were added; they are not listed. In the table, `*O` marks a DG16 commit.

| St | File | +/− | Expected answers or pins changed? | Commits (DG16 = *O) |
|---|---|---|---|---|
| A | fixtures/work-graph-c5-inputs/execution-r5-hosted-ubuntu24-final-successor-python312.json | +180 | new C5 input pin | 4fcb3386*O |
| A | fixtures/work-graph-c5-inputs/genuine-r5-hosted-ubuntu24-final-successor-execution-profile.json | +222 | new C5 profile pin | 4fcb3386*O |
| A | fixtures/work-graph-c5-inputs/execution-r5-hosted-ubuntu24-scan-repaired-python312.json | +180 | new C5 input pin | f894aa80 |
| A | fixtures/work-graph-c5-inputs/genuine-r5-hosted-ubuntu24-scan-repaired-execution-profile.json | +222 | new C5 profile pin | f894aa80 |
| A | tests/audit-andon-return-cases.py | +138 | new oracle | 9b308ac6 772e1c12 9ddd73f6 d10264be |
| A | tests/jidoka-andon-cases.py | +83 | new oracle | d10264be |
| A | tests/work-graph-verifier-properties-cases.py | +225 | new oracle (pins) | f894aa80 b6f34aef |
| M | fixtures/canonical-state-rotation/native_input_adapter_test.py | +13 −0 | additive | 11538085 |
| M | fixtures/canonical-state-rotation/native_preparation_test.py | +186 −2 | additive, plus a helper signature change | 11538085 19587dbe |
| M | fixtures/canonical-state-rotation/protected_projection_v2_test.py | +18 −0 | additive | 53a80108 |
| M | fixtures/operational-evidence/native-route-projection.py | +17 −0 | additive | 314597a4 |
| M | fixtures/semantic-preservation/cases.json | +15 −15 | **YES: SKILL.md sha256 pins and builder_sha256 re-pinned** | 486204e9 b4335c33 11538085 19587dbe 6dec63a3 |
| M | tests/c5-current-source-receiving.py | +155 −18 | **YES: `CURRENT` pin and SOURCES count** | 379581a8 b30ef328*O 4fcb3386*O 688da6db*O 41337a6d 2ec0ad91 647a8a26 de4b0d20 |
| M | tests/c5-selected-source-fixture.py | +12 −2 | **YES: `CURRENT_LOADER` (62545/d80a77c1 → 75536/c48e71e1); history set** | 71b6315c*O 379581a8 b30ef328*O 4fcb3386*O 688da6db*O 41337a6d 2ec0ad91 647a8a26 f894aa80 |
| M | tests/composite-source-cases.py | +261 −22 | **YES: compiler and reader profile pins and selection** | 27 commits (DG16: b30ef328 fe569146 4fcb3386 0c986ca5 fd516dee 8d2a2918 688da6db ba5df5ce) |
| M | tests/host_session_binding_hardening.py | +86 −3 | changed fault control (activation-custody-drift) | 5900a598 8a3dd9d1 76d47406 d10264be |
| M | tests/host_session_terminal.py | +126 −14 | **YES: Windows init refusal test replaced** | defa480b 5900a598 8caa0922 d10264be |
| M | tests/nonterminal-yield-cases.py | +14 −2 | refactor (tempdir) | c4e5a583 |
| M | tests/package-contract.test.sh | +28 −12 | **YES: budget reserve and history mutations** | 6dec63a3 |
| M | tests/plugin-release-asset.test.sh | +3 −3 | **YES: budget revision 5 → 4; reserve 1240/2000 → 2000** | 6dec63a3 |
| M | tests/release-asset.test.sh | +2 −2 | **YES: budget revision 5 → 4** | 19587dbe 6dec63a3 |
| M | tests/repo-state.test.sh | +151 −3 | adjusted fixture steps, plus new masked or empty cases | 2e72a912 6f422597 0cf89c2b 858906e7 e31e5b60 cd7d9ffb |
| M | tests/run-root-validation.test.sh | +149 −0 | additive | 9af0cbaa fd8942f6 a0fc7788 be670382 f60f8817 9ee33444 |
| M | tests/turn-disposition-cases.py | +82 −1 | helper signature, plus additive | d80c1e3a 482fcecd |
| M | tests/work-graph-custody-append-cases.py | +17 −6 | **YES: `_CONTRACTS` count 37 → 39; profile constant** | 0c986ca5*O f2221468*O f894aa80 |
| M | tests/work-graph-finite-entry-cases.py | +29 −18 | profile-selection refactor | 0c986ca5*O f2221468*O |
| M | tests/work-graph-historical-fixture-cases.py | +5 −3 | profile-set filter | 878e25e2*O f894aa80 |
| M | tests/work-graph-historical-fixture.py | +7 −0 | additive | 878e25e2*O 0c986ca5*O f2221468*O |
| M | tests/work-graph-planner-copy-cases.py | +3 −2 | profile-selection | f2221468*O |
| M | tests/work-graph-prefix-cases.py | +2 −0 | additive | 878e25e2*O |
| M | tests/work-graph-verifier-cases.py | +643 −4 | **YES: scan argv (grep `-e` count) changed in f894aa80; drift oracle changed in d60798ea, see V02.b** | 2450417a e2c0183c 71b6315c*O 39e6a7a7 f894aa80 2059984e 345b0be7 b6f34aef |

I classified the rows by inspecting removed and added lines. Each changed oracle still needs its independent property justification; that is Q01.c, a REVIEW limb.

**First unresolved predicate after:** Q01.c has no reviewer for the files marked YES.

---

## R35-P01.b: lineage and concurrent-writer census

**Commands**

```
git log --oneline 51416b2f..2450417a | wc -l     # 303
git log --merges 51416b2f..2450417a              # 0
git log --format='%an|%cn' 51416b2f..2450417a | sort | uniq -c
git ls-remote origin                              # 622 refs
```

**Commit grouping (303 in total)**

* **DG16 (Opus): 14.**
  * 12 are Opus-authored: f2221468 ba5df5ce 688da6db 8d2a2918 fd516dee 0c986ca5 4fcb3386 878e25e2 fe569146 daaa0819 b30ef328 71b6315c.
  * 2 are Opus patches recommitted by DG17: e2c0183c and 2450417a.
* **DG17 (Sol): 289.** Their author and committer are both `theislampill`, on the sol-dg17 line.
* **DG18: 0 authored.** DG18 source enters only through DG17 composition commits, for example 11538085, 19587dbe, 53a80108, b6f34aef and efdee66d. Fifteen messages mention DG18 or OR.
* **Root: 0 commits in the range.** Root decisions live on the disc branch. Five DG17 commits record Root decisions: 1035138f, 2e17f137, fc688064, 49d92011 and 141174a9.
* **Other: 0.**

**Branch-head census from `git ls-remote origin`.** There are 83 `engineering/*` heads and 288 `pro/*` heads. The full list is in `scratchpad/p01_branch_census.tsv`.

The heads recorded in `CONTINUATION.json branch_heads_at_receiving` (disc d8c22d3) have since advanced:

| Branch | At receiving | Now |
|---|---|---|
| engineering/sol-dg17-20261122 | 9f3e44e6 | a5ed001f (9f3e44e6 is an ancestor) |
| engineering/sol-dg16-20261122 | 9bdf5f96 | 3063f2cc |
| engineering/sol-dg18-20261122 | 43d15ad1 | 33b20880 (merge-base with 2450417a is 51416b2f) |
| engineering/pro-executor-original-completion-20261115 | f7e6c5a2 | d19abe0f |
| integration/active-rlgwo-composite-20261025 | 51416b2f | 51416b2f (unchanged) |
| main | — | 8fd1d1ca |

**Writers.**

* There are 33 `engineering/opus-dg16-*` heads, including `opus-dg16-v04-bookend2-20261125` = ea827457 and `opus-dg16-v02-v04-c5v20-20261124` = c7c59245.
* There are 14 `engineering/pro-dg18-*` and `pro-executor-dg18-*` heads. The `pro/dg18-*` heads include the a1–a13 51416 runs.
* The concurrent writers are therefore DG16 (Opus), DG17 (sol-dg17), DG18 (sol-dg18 and pro-dg18 heads) and the coordination branch.

**First unresolved predicate after:** Root has not received this census bound to 2450417a.

---

## R35-P02.a/b: per-delta owner, gap, change, discriminator and rollback

**Commands**

```
git show --stat <c>
git log -1 --format=%B <c>
patch-id comparisons
grep <sha> RB
```

| Delta | Semantic owner files | Actual gap (source) | Smallest change (diffstat) | Discriminator test | Failing preimage demonstrated | Rollback |
|---|---|---|---|---|---|---|
| 5c7634b9 (branch only; parent 2e72a912) | scripts/work-graph-verifier-task.py, tests/work-graph-verifier-cases.py | No v4 all-obligation record. v3 covered 399 rows, so the registry obligations were not each mapped (RB L1547–1606; association 3bc597a3). | 2 files, +393 / −9 | `work-graph-verifier-cases.py --canonical-task-only` → `all_obligation_acceptance` | None: the gap was an absence of rows, not a runtime RED (ledger P02.b) | Superseded and never in the slice. Its content was squashed into c7c59245/71b6315c. |
| 01c67ee1 (branch only; parent 5c7634b9) | same | Root review of 5c7634b9 (RB L1638). The positive fixture left 374 rows UNVERIFIED while the summary said PASS. | 2 files, +257 / −78 | `all_obligation_acceptance` (property_completeness verdicts) | RB L1638: Root observed this on 5c7634b9 | Superseded and squashed into c7c59245. RB L1840 is Root's decision (b), leading to read populations. |
| c7c59245 → slice 71b6315c (cherry-pick; patch-id 63f2c5d3 identical) | verifier-task.py, qualify-work-graph-verifier.py, qualify-work-graph-verifier-properties.py, C5 loader and setup, 2 tests; V19 history under test-support | V02: 27 recursive scopes unbound, COMPLETE unreachable (RB L1827, L1840). V04: W2 late writer changed the sealed stdout digest (RB L1694–1705). | 9 files, +6380 / −18. Most of that is the retained V19 history, 5232 lines. | `--canonical-task-only` (all_obligation_acceptance, canonical_task_late_writer_case); `--consumer-only` (RB L2176–2186) | RB L2191: late-writer regression "fails on the original `2e72` qualifier". W2 defect retained (RB L1702). | `git revert 71b6315c`. It needs 2450417a and e2c0183c reverted first, plus the DG17 C5 pins, because later commits edit the same functions. Not attempted (read-only). |
| d60798ea → slice e2c0183c (cherry-pick; patch-id ea13767d identical) | verifier-task.py, verifier-cases.py | Root, at bd5e065 (RB L2420): a stale inner digest was accepted as ESTABLISHED on 71b6315c (RB L2489). | 2 files, +92 / −3 | the bookend block in `all_obligation_acceptance` (stale entry, count, bytes, dropped, malformed, limits, consistent drift) | RB L2506: on 71b6315c the check fails at `before / stale_entry` with ESTABLISHED, entry_count 186 | `git revert e2c0183c`, after reverting 2450417a. Blob 893d3ecd → bccb3288. |
| ea827457 → slice 2450417a (cherry-pick; patch-id 5fb2315e identical) | verifier-task.py, verifier-cases.py | Root decision on e2c0183c (RB L2603–2607): a JSON array or object status raised TypeError. | 2 files, +45 / −2 | malformed-status, item, descriptor and top-level controls in `all_obligation_acceptance` | RB L2635: on e2c0183c, `TypeError: unhashable type: 'list'` | `git revert 2450417a`. Blob c5dab437 → 893d3ecd. |

**Byte-identity checks.** The task-file blobs on the slice equal the DG16 originals:

* 71b6315c = c7c59245 = bccb3288
* e2c0183c = d60798ea = 893d3ecd
* 2450417a = ea827457 = c5dab437
* the test file at 2450417a = ea827457 = 01130a29

None of the five DG16 deltas touches a shared owner.

**What remains for P02.b.** These packets cite the preimage RB lines. The retained failing output bytes have not been reproduced, and the ledger's proposed check, running the controls on disposable checkouts, was not run because this task is read-only.

**First unresolved predicate after:**

* **P02.a:** none left on the table itself; it is ready for Root.
* **P02.b:** the failing output bytes have not been re-retained on disposable 71b6315c and e2c0183c checkouts.
