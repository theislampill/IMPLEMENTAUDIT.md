# R35-Q01.c changed-oracle review

Baseline `51416b2f156b341c4a5f09029e2c6ceb5b30b1e7`, subject `2450417a3d442e189e20ba261120aff3ed7444c6`.

**Reviewer:** Claude Opus 5.5 (claude-opus-5-5). Claude Opus 5.5; fresh subagent session spawned by the DG16 executor's session with a neutral brief; no access to the author's conversation; did not author the changes under review.

**Summary:** 26 JUSTIFIED, 8 JUSTIFIED_WITH_NOTE, 0 NOT_JUSTIFIED, out of 34 changed oracles.

## Inventory

git diff --name-status 51416b2f 2450417a -- tests fixtures: 31 paths (24 M, 7 A, 0 D). The brief listed 10 files. Of the other modified files, host_session_binding_hardening.py, work-graph-historical-fixture-cases.py, work-graph-planner-copy-cases.py, work-graph-finite-entry-cases.py and repo-state.test.sh also change expected values or assertions and are reviewed here. The rest are additive or helper-signature only (native_preparation_test.py, nonterminal-yield-cases.py, turn-disposition-cases.py, native_input_adapter_test.py, protected_projection_v2_test.py, native-route-projection.py, run-root-validation.test.sh, work-graph-historical-fixture.py, work-graph-prefix-cases.py).

## Oracles

### 1. `fixtures/semantic-preservation/cases.json`: package_evidence.builder_sha256 (scripts/package-contract.py)

* **Before:** 506d52a9e122...68c1f
* **After:** 3b631cf230b5...86564
* **Justifying fact:** Recomputed sha256(git show 2450417a:scripts/package-contract.py) = 3b631cf2... (53,261 B); baseline blob = 506d52a9... A sed substitution of the two old digests by the new ones over the baseline file is byte-identical to the subject file, so nothing else changed. evaluate.py --check passes 21/21 at the subject; the baseline pins at the subject fail ('builder identity mismatch').
* **Coverage preserved:** Yes. All 21 cases, including every 'expected' label (triggered, disposition, reason_code), are byte-identical. Negatives and held-out cases (lean-lost, nonexistent-owner, broken-consumer, invented-consumer, exact-marker-broken-consumer, held-out-runtime, optional-only) remain.
* **Verdict:** **JUSTIFIED**

### 2. `fixtures/semantic-preservation/cases.json`: SKILL.md sha256 pin (13 occurrences across exact_literal_evidence and evidence_profiles)

* **Before:** a6b0e2801147...600ef
* **After:** 49e8342a5c5d...952df
* **Justifying fact:** Recomputed sha256(2450417a:skills/implementaudit/SKILL.md) = 49e8342a... (21,233 B). The anchor counts IMPLEMENTAUDIT_RUN_COMPLETE (3) and references/lean-operating-discipline.md (1) are the same at both commits. 'Package semantic preservation' is absent at both, so the lean-lost negative still has its missing anchor.
* **Coverage preserved:** Yes. The case labels did not change.
* **Verdict:** **JUSTIFIED_WITH_NOTE**. Note: The SKILL.md bytes themselves changed: an L4 interrupt-routing paragraph was added (cd7d9ffb) and the Hansei and background wording was condensed (76db9723 restored the wording that checkers require). The pin follows the actual bytes, but whether that prose is semantically equivalent is outside this oracle. It is covered by the checkers that consume SKILL.md, not by cases.json.

### 3. `tests/c5-selected-source-fixture.py`: CURRENT_LOADER (size, sha256) of scripts/load-work-graph-c5-executor.py

* **Before:** (62545, d80a77c1...d493)
* **After:** (75536, c48e71e1...7020)
* **Justifying fact:** Recomputed at 2450417a: 75,536 B, c48e71e1... The baseline loader (62,545 B, d80a77c1...) is retained byte-exactly at test-support/r5-verifier-scan-history/v12-source/scripts/load-work-graph-c5-executor.py. c5-current-source-receiving::test_all_prior_pin_and_revision_tables_are_unchanged asserts that literal (62545, d80a77c1...) and checks that every uppercase pin table in the retained V12/V13/V14/V15/V16/V17/V18 loaders equals the current loader's.
* **Coverage preserved:** Yes. The old pin is not deleted; it becomes a retained historical pin, and the prior pin tables are checked for equality.
* **Verdict:** **JUSTIFIED**

### 4. `tests/c5-selected-source-fixture.py`: HISTORIES tuple extended plus a RETAINED mapping for the prefix at ff5dbdce; write_plan substitutes the historical builder for selection pin 506d52a9

* **Before:** 8 history tables; builder read from the live path
* **After:** 16 history tables; builder pin 506d52a9 read from the v12-source copy
* **Justifying fact:** The retained copies are byte-identical to the baseline files. v12-source/scripts/qualify-work-graph-prefix.py = ff5dbdce... = 51416b2f:scripts/qualify-work-graph-prefix.py (the live file is now 2718a778...). v12-source/scripts/package-contract.py = 506d52a9... = the baseline builder. read_member still checks the digest against the selection pin.
* **Coverage preserved:** Yes. The historical selections still materialize exact historical bytes. Per the file's own comment, there is no search for a matching hash.
* **Verdict:** **JUSTIFIED**

### 5. `tests/c5-current-source-receiving.py`: CURRENT compiler sha256

* **Before:** ac4cc4180b1d...f772
* **After:** b9c3fde1eab9...5610
* **Justifying fact:** Recomputed sha256(2450417a:skills/implementaudit/scripts/compile-work-graph.py) = b9c3fde1... The baseline value ac4cc418 is the baseline compiler and is kept as V12_COMPILER, asserted at R5_NATIVE_OWNER_PROFILE_SOURCE_REVISION and in test-support/r5-verifier-scan-history/v12-source (recomputed ac4cc418).
* **Coverage preserved:** Yes. Retained compilers V13-V18 are added, and each is asserted against its retained member, with recomputed shas d9fb8b1f, de1832e6, f34de578, f148ccad, a5bcffee and 10a1f3f0.
* **Verdict:** **JUSTIFIED**

### 6. `tests/c5-current-source-receiving.py`: len(current.SOURCES) (two assertions)

* **Before:** 13
* **After:** 15
* **Justifying fact:** _Engine builds SOURCES from LOADER plus the selection pins (load-work-graph-c5-executor.py:615-626). Enumerated at the subject: R5_5S_SUCCESSOR selection = 14 pins, so 15. At baseline R5_NATIVE_OWNER_PROFILE = 12 pins, so 13. The two added members are scripts/qualify-work-graph-finite-leaf.py and scripts/verify-package.sh. Their consumption was required by Root's verifier_absence_scan_assignment and c5_and_windows_compatibility ('derive their consumed pins from actual source').
* **Coverage preserved:** Yes. The count equals an enumerable population.
* **Verdict:** **JUSTIFIED**

### 7. `tests/c5-current-source-receiving.py`: Current base selection: NEW_BASE becomes FINAL_BASE (selection_origins.base_actual_member, builder pin)

* **Before:** budget5-builder base, 8304 B, 5963c877..., builder 506d52a9
* **After:** final-successor base, 8290 B, daed0c51..., builder 3b631cf2
* **Justifying fact:** Recomputed: the final-successor fixture is 8,290 B with sha daed0c51...; its package-contract.py pin is 3b631cf2..., the live builder. SCAN_BASE (8290 B, bdd38d50..., builder af3f496e) also matches. Discussion record DG16-DG17-reader-bindings.md:300 describes it as the scan-repaired selection with only the builder pin moved.
* **Coverage preserved:** Yes. A new assertNotIn(NEW_BASE) is added. NEW_BASE is still asserted for the retained V10 engine.
* **Verdict:** **JUSTIFIED**

### 8. `tests/c5-current-source-receiving.py`: test_historical_base_bytes_at_current_selector_refuse

* **Before:** current() refuses NEW_BASE substitution
* **After:** the NATIVE_OWNER revision refuses NEW_BASE substitution; current() refuses FINAL_BASE substitution
* **Justifying fact:** The current selector no longer reads NEW_BASE, so the refusal moved to the revision that does read it. An equivalent refusal was added for the member that is now current.
* **Coverage preserved:** Yes, extended: two refusals instead of one.
* **Verdict:** **JUSTIFIED**

### 9. `tests/c5-current-source-receiving.py`: Wrong-profile refusal regex

* **Before:** 'fixed R5 hosted profile'
* **After:** 'fixed R5 hosted (source )?profile'
* **Justifying fact:** The loader messages for the new revisions read '... requires the fixed R5 hosted source profile' (load-work-graph-c5-executor.py:364-392). The older revisions keep 'fixed R5 hosted profile' (396/400). The loop was extended from 3 to 10 revisions.
* **Coverage preserved:** Yes. Every revision must still raise ValueError.
* **Verdict:** **JUSTIFIED_WITH_NOTE**. Note: The match text is slightly looser. It is still anchored on 'fixed R5 hosted ... profile'.

### 10. `tests/c5-current-source-receiving.py`: V10 producer-contract state root

* **Before:** live ROOT bytes
* **After:** a materialized R5_CURRENT_BUILDER_V10 source
* **Justifying fact:** The V10 selection pins builder 506d52a9, and the live builder is now 3b631cf2. The materialized source supplies the retained baseline builder, whose bytes were verified identical.
* **Coverage preserved:** Yes. The V10 contract is still checked against its own pinned bytes, not relaxed.
* **Verdict:** **JUSTIFIED**

### 11. `tests/c5-current-source-receiving.py`: Stale V10 and V9 loader tests now write the v12 prefix helper before current()

* **Before:** no prefix override
* **After:** the v12-source prefix (ff5dbdce) is written
* **Justifying fact:** The stale loaders pin the baseline prefix ff5dbdce, retained byte-exactly. The live prefix changed to 2718a778.
* **Coverage preserved:** Yes, but these tests are skip-gated (--baseline-v10-loader / --baseline-loader).
* **Verdict:** **JUSTIFIED_WITH_NOTE**. Note: They do not run by default (2 skips), so this change is not exercised in ordinary runs.

### 12. `tests/composite-source-cases.py`: Native-owner (V12) successor compiler pin

* **Before:** dict(R5_BUDGET5_BUILDER_PINS, compiler=actual live compiler)
* **After:** ...compiler=R5_NATIVE_OWNER_PROFILE_COMPILER_SHA256
* **Justifying fact:** The constant is ac4cc418... (loader:261), the same value the baseline assertion computed from the live compiler at 51416b2f. It is independently pinned as the literal V12_COMPILER in c5-current-source-receiving. The state dict is now hashed from the materialized source rather than live ROOT.
* **Coverage preserved:** Yes. The value is unchanged; only its source moved to the retained pin.
* **Verdict:** **JUSTIFIED**

### 13. `tests/composite-source-cases.py`: Hosted current reader member equality

* **Before:** only the compiler equals the live bytes
* **After:** 7 members equal the live bytes, builder pin = live; plus retained-predecessor and mixed-source refusal (prefix from another revision refuses)
* **Justifying fact:** Root c5_and_windows_compatibility (CONTINUATION.json): 'Check current and historical own-source acceptance and mixed-source refusal through the mandatory composite suite.'
* **Coverage preserved:** Yes, strengthened.
* **Verdict:** **JUSTIFIED**

### 14. `tests/composite-source-cases.py`: Windows profile population tests: historical member map

* **Before:** only validate-run-root.sh, rotate-canonical-state.py and read-canonical-pair.py come from history
* **After:** canonical_hot_projection.py and canonical_rotation_inputs.py also come from retained copies
* **Justifying fact:** Retained windows-shared-hot-projection.py.fixture = 10f852a7... = bb781f62 = 51416b2f canonical_hot_projection.py (live is now 6ff0fe34). Retained pre-OR canonical_rotation_inputs.py = dc95d31e... = baseline. The profile rows (size, digest) did not change. This is Root's c5_and_windows_compatibility assignment ('Bind the two prior Windows profile population tests to their authentic historical hot-projection bytes').
* **Coverage preserved:** Yes. The historical profiles still require their original bytes.
* **Verdict:** **JUSTIFIED**

### 15. `tests/composite-source-cases.py`: Core continuity profile under test

* **Before:** the literal 'composite-20261120-native-owner-profile-v1-core' must equal the live CORE bytes
* **After:** selected_core_continuity_profile(): the unique entry among 8 named profiles whose claim-run.sh and validate-run-root.sh digests equal the live bytes
* **Justifying fact:** The selection is derived from facts (live digests) and requires exactly one match. Elsewhere the test separately asserts the 8 new profiles and the full chain of retained hashes.
* **Coverage preserved:** Mostly. The prior core profile is still asserted Windows-valid and distinct from the new one.
* **Verdict:** **JUSTIFIED_WITH_NOTE**. Note: The test no longer names which profile must be current. Live drift to another of the 8 known profiles would pass this particular check.

### 16. `tests/composite-source-cases.py`: len(transport.SOURCE_PROFILES_V1) plus the retained-population hash chain

* **Before:** 50 (the 48-entry hash 0424405... after removing the native-owner prefix)
* **After:** 58, with intermediate hashes 57...50 and the same 48-entry check
* **Justifying fact:** Recounted: 50 at baseline, 58 at the subject. All 50 baseline entries are byte-identical (0 changed, 0 removed, 8 added). The full baseline hash 389cb640... equals the test's new 50-entry checkpoint literal, and the 48-entry hash 0424405... is unchanged.
* **Coverage preserved:** Yes. Baseline identity is now pinned more strongly.
* **Verdict:** **JUSTIFIED**

### 17. `tests/composite-source-cases.py`: Composite prefix selection

* **Before:** profile 'COMPOSED_COMPOSITE_PREFIX_23_V1' selects the live registry
* **After:** COMPOSITE_PROFILE refuses the live registry and accepts the predecessor registry; SCAN_REPAIRED selects the live registry and refuses the predecessor
* **Justifying fact:** The predecessor registry (v12-source/scripts/verify-package.sh) = 65c7b693... = baseline bytes. f894aa80 is the only registry change since the baseline. Root verifier_absence_scan_assignment (CONTINUATION.json) assigns the scan repair and its own prefix selection.
* **Coverage preserved:** Yes, extended: cross-registry refusals in both directions.
* **Verdict:** **JUSTIFIED**

### 18. `tests/composite-source-cases.py`: validate-run-root.sh expected sha in the INERT_NO_EXECUTION policy test

* **Before:** 7787569b...28ad
* **After:** 9ff4ffb1...13b8
* **Justifying fact:** Recomputed: baseline validate-run-root.sh = 7787569b, subject = 9ff4ffb1. The value equals the actual bytes.
* **Coverage preserved:** Yes. Same assertion shape.
* **Verdict:** **JUSTIFIED**

### 19. `tests/host_session_terminal.py`: test_windows_init_refuses_before_write replaced by test_windows_init_refuses_inherited_store_permissions

* **Before:** Windows init returns UNAVAILABLE and creates no store
* **After:** with a pre-existing inherited-ACL store, init returns UNAVAILABLE, the error names 'protected owner-only DACL', and the store stays empty
* **Justifying fact:** This is a documented, Root-assigned behavioural change. CONTINUATION.json:1365 assigns Sol-DG17 the Windows typed first-activation writer and read-only lookup. host-session-binding.md at the subject reads 'Windows NTFS supports init, first bind and lookup under ... a protected owner-only DACL'. The commit is 5900a598. Run natively on Windows: the new test passes. test_windows_initial_binding_lookups_preserve_the_store also passes.
* **Coverage preserved:** Partly. Unsafe Windows init is still refused with no write. The unconditional refusal is gone by design.
* **Verdict:** **JUSTIFIED_WITH_NOTE**. Note: No separate Root/reviewer post for this exact test rename was found in discussions/*.md, only the CONTINUATION assignment. Windows-only; executed natively here.

### 20. `tests/host_session_terminal.py`: SelectedStopDiagnostics expected binding plus the owner mock

* **Before:** partial bound dict; load_pinned_owner -> object()
* **After:** full canonical v1 binding record; real validate_record and ATTEMPT_SCHEMA; v3 policies; binding refusal path
* **Justifying fact:** Root expected_binding_decision (CONTINUATION.json, 30aadfcd on 16917d2f): 'Require the exact canonical expected binding shape and equality to the complete active lookup'. The commit is defa480b.
* **Coverage preserved:** Yes, strengthened. It now uses the real validator. The suite passes in WSL (32 OK, 1 Windows skip).
* **Verdict:** **JUSTIFIED**

### 21. `tests/host_session_binding_hardening.py`: Admitted failed-activation attempt marker

* **Before:** {schema, owner_id, host_id, host_session_id}; after a successful bind the marker bytes are unchanged
* **After:** the marker also carries outcome: REFUSED; after a successful bind 'outcome' is absent
* **Justifying fact:** This is a documented contract. host-session-binding.md at the subject reads 'A validation refusal before either pair write records outcome: REFUSED ... Owner retry resets REFUSED before validation.' The commit is d10264be. CONTINUATION.json requires preserving 'the proven failed-first-activation fallback'. The suite passes in WSL (30 OK).
* **Coverage preserved:** Mostly. Two new tests cover the proven-refusal versus interrupted-attempt distinction and custody drift.
* **Verdict:** **JUSTIFIED_WITH_NOTE**. Note: The post-bind assertion went from full byte equality to 'outcome' absent only. The other marker fields are no longer checked after the bind. No Root/reviewer record naming this exact assertion change was found.

### 22. `tests/package-contract.test.sh`: reduced-reserve mutation value

* **Before:** canonical reserve 1239
* **After:** canonical reserve 1999
* **Justifying fact:** One below the active reserve. Revision 4 has reserve 2000 for both roles (package-contract.py:131/141 and package/implementaudit-package.json at the subject).
* **Coverage preserved:** Yes. Same boundary-minus-one negative.
* **Verdict:** **JUSTIFIED**

### 23. `tests/package-contract.test.sh`: History mutations

* **Before:** changed-fourth-history (history['4'] reserve)
* **After:** unexpected-current-as-history and historical-v5; 10 mutations become 11
* **Justifying fact:** budget_history at the subject has keys 1-3 (revision 4 is active), so history['4'] no longer exists. Injecting the current budget as history '4' and switching to revision 5 / reserve 1240 are both rejected.
* **Coverage preserved:** Yes. One more negative.
* **Verdict:** **JUSTIFIED**

### 24. `tests/package-contract.test.sh`: Per-role budget limit

* **Before:** canonical 588584, standalone 587824
* **After:** 587824 for both
* **Justifying fact:** Revision 4: 589,824 minus 2,000 = 587,824 for each role. This matches the Root m5_original_budget (CONTINUATION.json) and the original M5 receiver c073689e:qualification/dg16-installed-runtime05/installed_runtime.py:142-171.
* **Coverage preserved:** Yes. Tightened.
* **Verdict:** **JUSTIFIED**

### 25. `tests/package-contract.test.sh`: Historical-revision refusal check

* **Before:** budget_history['4'] enforced at 587824/587825
* **After:** a constructed revision-5 budget (V4 plus canonical 1240) enforced at 588584/587824 plus 1; revision-4 and revision-5 approval file shas pinned
* **Justifying fact:** Recomputed the approval shas: pr255-v4 = e4af32dc..., pr255-v5 = 9cce88d8... Both files are present at both commits.
* **Coverage preserved:** Yes. The historical v5 refusal is retained.
* **Verdict:** **JUSTIFIED_WITH_NOTE**. Note: The v5 budget is rebuilt inside the test from PR255_V4_BUDGETS, not read from a retained contract record. budget_history no longer lists revision 4 or 5 as data.

### 26. `tests/plugin-release-asset.test.sh`: budget_revision.revision and the (cap, reserve) check

* **Before:** revision 5; (589824, 1240 canonical / 2000 standalone)
* **After:** revision 4; (589824, 2000) for both
* **Justifying fact:** Root M5 review (CONTINUATION.json m5_original_review_345b0be7): 'Mandatory package acceptance scripts at this candidate require v5. Historical results cannot cover the changed contract ... DG17 owns the package revision and matching acceptance-test correction.' Root m5_original_budget: cap 589824, reserve 2000, usable 587824. The original M5 receiver c073689e (lines 142-171) requires revision 4, approval e4af32dc, cap 589824 and reserve 2000. At the subject, package/implementaudit-package.json has revision 4 and both reserves at 2000. The commit is 6dec63a3. Opus's discussion record (DG18 file, 2026-11-23) states 'v5 does not satisfy the original M5 predicate'.
* **Coverage preserved:** Yes. The reserve went up (stricter) and the cap is unchanged.
* **Verdict:** **JUSTIFIED**

### 27. `tests/release-asset.test.sh`: budget_revision.revision (standalone)

* **Before:** 5
* **After:** 4
* **Justifying fact:** Same Root M5 decision and original-receiver predicate as plugin-release-asset. The standalone (589824, 2000) assertion is unchanged, and so is the history['3'] check.
* **Coverage preserved:** Yes.
* **Verdict:** **JUSTIFIED**

### 28. `tests/work-graph-custody-append-cases.py`: len(helper._CONTRACTS)

* **Before:** 37
* **After:** 39
* **Justifying fact:** Recounted by importing qualify-work-graph-finite-leaf.py: 37 at baseline, 39 at the subject. The first 37 keys are in the same order, and each contract_for() digest is identical (0 changed). Two were added: CUSTODY_APPEND_SCAN_REPAIRED_20261123_V1 and SHARED_SUCCESSOR_20261123_V1.
* **Coverage preserved:** Yes. The count equals an enumerable population.
* **Verdict:** **JUSTIFIED**

### 29. `tests/work-graph-custody-append-cases.py`: Current composite input profile

* **Before:** CURRENT_CUSTODY_APPEND_PROFILE selects the live verify-package.sh
* **After:** SCAN_REPAIRED profile for the live registry; CURRENT profile accepts the predecessor registry and refuses the live one; SCAN_REPAIRED refuses the predecessor
* **Justifying fact:** Predecessor = v12-source verify-package.sh = 65c7b693... = baseline bytes. The live registry changed (f894aa80). DG16-DG17-reader-bindings.md:239/265 records this plan.
* **Coverage preserved:** Yes, extended: cross refusals added.
* **Verdict:** **JUSTIFIED**

### 30. `tests/work-graph-historical-fixture-cases.py; tests/work-graph-planner-copy-cases.py`: Profile exclusion set for historical iteration (3 loops) and engine selection

* **Before:** != CURRENT_CUSTODY_APPEND_PROFILE
* **After:** not in COMPOSITE_CUSTODY_APPEND_PROFILES
* **Justifying fact:** COMPOSITE_CUSTODY_APPEND_PROFILES = (CURRENT, SCAN_REPAIRED, SHARED_SUCCESSOR). The two new members are exactly the 2 added contracts, so the same 36 historical profiles are still iterated.
* **Coverage preserved:** Yes.
* **Verdict:** **JUSTIFIED**

### 31. `tests/work-graph-finite-entry-cases.py`: Prefix drift / unreviewed successor refusal

* **Before:** one mode (custody-append-current, live prefix path)
* **After:** 3 modes, each with its own selected prefix (v12 copy, v16 copy, live)
* **Justifying fact:** Each mode binds its own retained prefix. The same two refusals ('loaded prefix helper differs', 'unsupported captured prefix helper') and dispatch_count == 0 are asserted for each.
* **Coverage preserved:** Yes, extended. Passes in WSL (10 OK).
* **Verdict:** **JUSTIFIED**

### 32. `tests/work-graph-verifier-cases.py`: DIST consumer scan argv reconstruction

* **Before:** parse 'if grep -R -n -I ...' up to '  . >'; assert argv[0]=='grep' and 5 '-e'
* **After:** parse 'require_absent_matches "msg" ...' up to '  .'; assert -R -n -I --exclude-dir=.git, 5 '-e', ends with '.'
* **Justifying fact:** Independently extracted both: the grep argv at 51416b2f and at 2450417a is element-for-element identical (17 tokens, same 5 patterns, same excludes), and the refusal message is unchanged. Root CONTINUATION.json ordinary_verifier_de4b0d20: the DIST fixture searched for an obsolete scan expression, 'DG17 integrates the corrected DIST consumer test once'. verifier_absence_scan_assignment covers the fail-closed scan. The actual failing predecessors are retained as terminal (de4b0d20, 2ec0ad91; exit 1, 96/1/22).
* **Coverage preserved:** Yes, strengthened.
* **Verdict:** **JUSTIFIED**

### 33. `tests/work-graph-verifier-cases.py`: Read-population drift oracle (added within the range, 71b6315c, then changed by e2c0183c = cherry-pick of d60798ea, and 2450417a = ea827457)

* **Before:** drift simulated by zeroing the after digest; expected DRIFT_DURING_OCCURRENCE
* **After:** drift is a consistent after-bookend (one entry sha changed, digest recomputed with owner._digest); inconsistent bookends give INCONSISTENT_BOOKEND
* **Justifying fact:** A reviewed behavioural correction. The reviewer found a stale inner digest accepted (DG16-DG17-reader-bindings.md:2420). The Opus deltas are at 2485-2515 and 2611-2638. The Root decision on e2c0183c is at 2603-2607 (Epicurus found a TypeError for array/object status). The Root freeze of 2450417a is at 2657-2659 (Epicurus independently received the controls). Labels are computed from the evidence by owner._digest, not typed in.
* **Coverage preserved:** Yes. Relative to the baseline the block is purely additive. The stale-digest class is covered by 8 edits on each side, giving INCONSISTENT_BOOKEND and not COMPLETE.
* **Verdict:** **JUSTIFIED_WITH_NOTE**. Note: There is no control for a digest-only corruption (entries unchanged, digest altered). The case is covered by class (digest is not equal to the rederived value), not by an explicit case.

### 34. `tests/repo-state.test.sh`: added-lines and changed-files census oracles

* **Before:** tracked.txt += 'modified'; grep -F DEBUG_SENTINEL somewhere in the output
* **After:** tracked.txt += 'modified\n++count;\ncount += 1;'; exact -Fx lines for 7 sentinels; header-leak, colour and Git-failure negatives; masked committed/staged paths
* **Justifying fact:** Fixture inputs were extended to exercise the masked-layer and '++' line cases (commits 2e72a912, 6f422597, 0cf89c2b, 858906e7, e31e5b60, cd7d9ffb). Every expected line is a literal the fixture itself writes.
* **Coverage preserved:** Yes, strengthened. The DEBUG_SENTINEL check is retained under stricter -Fx matching.
* **Verdict:** **JUSTIFIED**

## R53-DAG-* identifiers

Baseline: 0 files. Subject: 0 files. The 20 IDs (A01-A03, B01-B03, H01-H04, N01-N08, P01-P02 (20)) are defined only at 585012cb (recovery/contracts/original/*: DEFINITIONS_48_20_117_12.json, ORIGINAL20_CASES.json, ORIGINAL48_CURRENT_MAP_NOV06.json, R0035_209_CRITERIA_INDEX.md, issue-209.md); 585012cb is not an ancestor of 2450417a.

No R53-DAG-* identifier, and none of the sampled suffixes, appears in any file at either commit. This diff therefore neither removed nor added R53-DAG coverage by identifier. Whether the original R53-DAG positive/negative/boundary/adjacent/held-out coverage is retained at all cannot be shown by identifier at either commit. That belongs to the P limb of Q01, not to this oracle review.

## Execution and limits

* Passed in a fresh WSL clone at 2450417a: tests/package-contract.test.sh (ok); fixtures/semantic-preservation/test-cases.sh (21/21); tests/host_session_terminal.py (32 OK, 1 skip); tests/host_session_binding_hardening.py (30 OK, 1 skip; baseline 27 OK); tests/work-graph-finite-entry-cases.py (10 OK).
* Passed on native Windows: test_windows_init_refuses_inherited_store_permissions; test_windows_initial_binding_lookups_preserve_the_store; test_selected_stop_receives_proven_refusal_but_not_interrupted_attempt; evaluate.py --check 21/21; baseline pins at the subject refuse.
* Environment-limited (not evidence): c5-current-source-receiving, custody-append-cases, historical-fixture-cases and planner-copy-cases failed under WSL because the clone sits on a /mnt/c drvfs mount. The refusals are mode, link-count and byte-bound checks ('bounded ordinary single-link file', 'unsupported finite-leaf source mode'). They are not oracle failures, and the run was stopped before composite-source-cases. Those oracles were instead verified by independent recomputation and enumeration, as listed. Native-Windows host_session_binding_hardening fails on POSIX-only cases at both commits (baseline 20 failures, subject 7), which is out of scope.
* Side effect, reverted: The WSL run script added git config --global safe.directory '*' in the WSL user profile. It was removed afterwards (0 entries remain). Nothing was written to the shared clone.
