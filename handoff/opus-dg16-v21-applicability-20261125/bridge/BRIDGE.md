# V21 native-source applicability bridge (per changed member)

Authority NONE. Ruling: Root at 24c4684 handoff/astra-dg16-dg18/discussions/DG16-DG17-reader-bindings.md. Product 338c4c36d2ac95ca24345bc92fe8c53d66eaa15d / tree 53498df783ed441744ae5080982c2d5e59c34bbc; retained native-qualified source 3e0f4b6d05eb086017ce721d40459fdbd68714dd; historical adopted source e76a07b2bae7c945e5a9d529ed8cf9069f4c9064. Input rows sha256 `9a073972b3f0599b1ddc9ce98a9643ef27414fa6b168fa7aa1b0b7bd24326033`.

Linux native path = qualification/dg16-r5-g1-hosted-episode/native_probe.py@b393a905 running the unchanged tests/work-graph-original14-receiving-cases.py::{test_native_intake_uses_current_original14_not_retired_root,test_native_intake_later_boundary_prevents_return}; these import only tests/native-work-graph-cases.py (compiler) and fixtures/canonical-state-rotation/canonical_reader_test.py, which copies skills/implementaudit/scripts and templates into a constructed repo, runs author_checkpoint.py --activate, claim-run.sh/claim-run-rotation.py/rotate-canonical-state.py rotation, read-canonical-pair.py --native-guards, and compiler native intake (operational-evidence.py static owner + continuity transport closure over the 8-file helper tuple), and execs protected_projection_v2_test.py only for render_pair/build_owner_map.

Classes: a = non-semantic; b = semantic, off the Linux native-intake path or Windows-only; c = semantic on the native-relevant path.
COVERED = a/b with a passing registered control at V21. PARTIAL = c whose Linux-reachable delta is pin-coherence only or mechanically equivalent (no native observation at V21). OPEN = c with Linux-reachable behaviour change; the native predicate stays open.

Counts: COVERED 11, PARTIAL 5, OPEN 4. The native predicates at V21 (fixed_receiver_identity, wrong_receiver_refusal, current_native_intake, later_invalidation_refusal, host/currentness custody) remain OPEN.

| # | Member | Commits (3e0f4b6d..V21) | Class | Status | Covering controls / evidence | Residual semantic difference |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 1 | `fixtures/canonical-state-rotation/native_input_adapter_test.py` | 11538085 | b | COVERED | tests/canonical-state-rotation.test.sh:25 runs this file<br>canonical-state-rotation: rc=0 stderr_sha256=3eddf690cba5a109045bafdfb9c873593cfe9ccd6b7c22a3e0617d0faf132c5f | None for the native predicates. |
| 2 | `fixtures/canonical-state-rotation/native_preparation_test.py` | 11538085, 19587dbe | b | COVERED | tests/canonical-state-rotation.test.sh:29 runs this file<br>canonical-state-rotation: rc=0 stderr_sha256=3eddf690cba5a109045bafdfb9c873593cfe9ccd6b7c22a3e0617d0faf132c5f | None for the native predicates; the OR behaviour these tests control is DG18 scope. |
| 3 | `fixtures/canonical-state-rotation/owned_stdio_source_boundaries_test.py` | e61ead42 | b | COVERED | NATIVE_SOURCE_APPLICABILITY.json@b393a905 fixture_repair (retained e166953f..., selected 528f1e69...)<br>native_prerequisite.py@b393a905:181-184 NATIVE_FIXTURE_REPAIR_SCOPE<br>tests/canonical-state-rotation.test.sh:30<br>git show 338c4c36:<path> / sha256sum = 528f1e693d0745b90a8ea2ededd570962f929e8f2c76b115c6e011386a03e0f7 (identical to e76a07b2)<br>canonical-state-rotation: rc=0 stderr_sha256=3eddf690cba5a109045bafdfb9c873593cfe9ccd6b7c22a3e0617d0faf132c5f | Unchanged from the historical admission, including its declared limits: native_qualification=false, full_pair_consumption=REQUIRED_NOT_EXECUTED. |
| 4 | `fixtures/canonical-state-rotation/protected_projection_v2_test.py` | 53a80108 | b | COVERED | tests/canonical-state-rotation.test.sh:13 runs this file<br>ast_delta.py 3e0f4b6d..338c4c36: only ClassDef:ProjectionV2Qualification differs<br>canonical-state-rotation: rc=0 stderr_sha256=3eddf690cba5a109045bafdfb9c873593cfe9ccd6b7c22a3e0617d0faf132c5f | None for the native predicates. |
| 5 | `fixtures/canonical-state-rotation/windows_qualification_test.py` | 11c0dbd0 | b | COVERED | tests/canonical-state-rotation.test.sh:17 runs this file<br>canonical-state-rotation: rc=0 stderr_sha256=3eddf690cba5a109045bafdfb9c873593cfe9ccd6b7c22a3e0617d0faf132c5f | Windows native behaviour stays DG18_SEPARATE, as the historical record says (windows_qualification). |
| 6 | `fixtures/controller-initialization/author_checkpoint.py` | 14adb7c4 | c | PARTIAL | tests/canonical-state-rotation.test.sh:19 (canonical_reader_test setUp in every case)<br>tests/continuity-contract.test.sh<br>canonical-state-rotation: rc=0 stderr_sha256=3eddf690cba5a109045bafdfb9c873593cfe9ccd6b7c22a3e0617d0faf132c5f<br>continuity-contract: rc=0 stderr_sha256=9445bec30e46f37454928c755f735769c4edba0e7c9cf95924d03ac72abf836f<br>Sol-DG18 7f954af1 same record: CanonicalReaderTests.test_actual_native_owner_pair_reads_are_ordered_and_token_bound rc 0 stderr 543b42af93a2d2f1cdd6c6382342698da999b790cc4acfef843897ac9ecca612 | Equivalence claim for independent review: on Linux, shutil.which(PATH) and execvp(PATH) resolve the same bash, so only argv[0] changes (bash ignores it for $0 when running a script). The missing-bash refusal changes the error, not the success path. |
| 7 | `scripts/operational-evidence.py` | b41051e2, 529f2a53, 6729f156, fe569146, fd516dee, 8d2a2918, ba5df5ce, 11762d9f, 39e6a7a7, 53a80108, 51416b2f, 1b6b8911, 14adb7c4, 8ee4ae44<br>since e76: b41051e2, 529f2a53, 6729f156, fe569146, fd516dee, 8d2a2918, ba5df5ce, 11762d9f, 39e6a7a7, 53a80108, 51416b2f, 1b6b8911, 14adb7c4 | c | OPEN | tests/operational-evidence-contract.test.sh<br>tests/work-graph-continuity-cases.py, tests/work-graph-source-observation-cases.py (registered by tests/native-work-graph.test.sh)<br>tests/composite-source-cases.py (tests/composite-source.test.sh)<br>ast_delta.py e76a07b2..338c4c36: +15 AugAssign source-profile rows, +15 transport-profile Assigns, FunctionDef _native_check_continuity_closure_v1 differs only in its nt tuple<br>pin coherence verified: every changed byte/sha256 pin in this member equals the V21 sibling body (git show 338c4c36) (compiler _NATIVE_STATIC_OWNER 441955/28d1b5d0 matches this file)<br>operational-evidence-contract: rc=0 stderr_sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855<br>wg-continuity-cases: rc=0 stderr_sha256=7c3a9b301de18146337fba454d938d99a91de6dd17bf92acf157a4658dd74c14<br>wg-source-observation-cases: rc=0 stderr_sha256=f8198396cd4a1c7c75d45a25bdfd686b75836051780e9d658e624ea6e1f69bb6<br>Sol-DG17 2485bf5270c87026c275c33143a48aee99d4fa40 handoff/sol-dg17-20261122/CONTINUATION.md "Exact V21 joined source and artifact qualification": clean WSL composite-source wrapper rc 0 (85 composite cases, 20 C5 source receiving, 6 original14 history cases), stderr 24235e75815885fd0ec5eb1d8bf8cf8502fb14d01c1de0d60d5e1b0d452e1f73 | Native predicates fixed_receiver_identity, wrong_receiver_refusal and current_native_intake have not been observed at receiver 441955/28d1b5d0 with the V21 helper tuple. Historical native_prerequisite pins RECEIVER_SHA 5950164a/422801 and receiver_non_windows_ast_sha256 699eb268 (no producer). No native observation exists at V21 bytes. Historical native receiving bound e76a07b2 (DG16_8EE4_LINUX_CHANGED_NATIVE_BINDING_V1) and retained 3e0f4b6d; neither transfers. |
| 8 | `scripts/work-graph-continuity-transport.py` | b41051e2, 529f2a53, 6729f156, fe569146, fd516dee, 8d2a2918, ba5df5ce, 11762d9f, 39e6a7a7, 53a80108, 51416b2f, 1b6b8911, 14adb7c4 | c | OPEN | tests/work-graph-continuity-cases.py, tests/work-graph-source-observation-cases.py<br>tests/composite-source-cases.py<br>ast_delta.py e76a07b2..338c4c36: only Assign rows plus the nt-only _windows_core_profile_v1<br>pin coherence verified: every changed byte/sha256 pin in this member equals the V21 sibling body (git show 338c4c36)<br>wg-continuity-cases: rc=0 stderr_sha256=7c3a9b301de18146337fba454d938d99a91de6dd17bf92acf157a4658dd74c14<br>wg-source-observation-cases: rc=0 stderr_sha256=f8198396cd4a1c7c75d45a25bdfd686b75836051780e9d658e624ea6e1f69bb6<br>Sol-DG17 2485bf5270c87026c275c33143a48aee99d4fa40 handoff/sol-dg17-20261122/CONTINUATION.md "Exact V21 joined source and artifact qualification": clean WSL composite-source wrapper rc 0 (85 composite cases, 20 C5 source receiving, 6 original14 history cases), stderr 24235e75815885fd0ec5eb1d8bf8cf8502fb14d01c1de0d60d5e1b0d452e1f73 | Linux native continuity at V21 goes through a profile row with no native observation. This member was previously unchanged, so it is a new member of the native-relevant delta. No native observation exists at V21 bytes. Historical native receiving bound e76a07b2 (DG16_8EE4_LINUX_CHANGED_NATIVE_BINDING_V1) and retained 3e0f4b6d; neither transfers. |
| 9 | `skills/implementaudit/scripts/canonical_hot_projection.py` | 53a80108 | c | OPEN | fixtures/canonical-state-rotation/protected_projection_v2_test.py new subtests (tests/canonical-state-rotation.test.sh:13)<br>canonical_reader_test (canonical-state-rotation.test.sh:19)<br>Sol-DG18 7f954af15fd8958f0fe40a19ce0afd1b086deaaa handoff/astra-dg16-dg18/discussions/DG18-authentic-OR-and-cold-receiving.md "Sol-DG18 ordinary consumer receiving of V21" (Windows Py3.11): RealHelperIntegration.test_real_helper_migrates_real_main_receipt_and_separate_readers rc 0 stderr 0432353ae2901de77b68763b44d6fc52a5c1f56e544d83c22669265254a3e264<br>canonical-state-rotation: rc=0 stderr_sha256=3eddf690cba5a109045bafdfb9c873593cfe9ccd6b7c22a3e0617d0faf132c5f<br>Sol-DG18 7f954af15fd8958f0fe40a19ce0afd1b086deaaa handoff/astra-dg16-dg18/discussions/DG18-authentic-OR-and-cold-receiving.md "Sol-DG18 ordinary consumer receiving of V21" (Windows Py3.11): RealHelperIntegration.test_real_helper_migrates_real_main_receipt_and_separate_readers rc 0 stderr 0432353ae2901de77b68763b44d6fc52a5c1f56e544d83c22669265254a3e264<br>Sol-DG18 7f954af1 same record: CanonicalReaderTests.test_actual_native_owner_pair_reads_are_ordered_and_token_bound rc 0 stderr 543b42af93a2d2f1cdd6c6382342698da999b790cc4acfef843897ac9ecca612 | This is a strict tightening. Conforming inputs (the unchanged v2/source.json fixture) are accepted in ordinary controls at V21, but the parser running inside the native intake at V21 is unobserved. Independent review is needed on whether the new owner-EVIDENCE binding can refuse a real native pending row that 3e0f4b6d accepted. |
| 10 | `skills/implementaudit/scripts/canonical_rotation_inputs.py` | 11538085 | b | COVERED | native_input_adapter_test.test_null_wire_metadata_preserves_exact_usage_without_admitting_bad_metadata (canonical-state-rotation.test.sh:25)<br>canonical-state-rotation: rc=0 stderr_sha256=3eddf690cba5a109045bafdfb9c873593cfe9ccd6b7c22a3e0617d0faf132c5f | The bytes are still a member of the 8-file continuity tuple admitted by operational-evidence.py (OPEN). The behaviour change belongs to DG18 OR scope. |
| 11 | `skills/implementaudit/scripts/claim-run-rotation.py` | d5670374, 860c282c, d298e64c, 09cef7dd, ae6a48c9, 11538085, ca06d866, 9a71560f, c36c8833, fb8177fd, 53a80108, 11c0dbd0, 1b6b8911, 14adb7c4 | c | PARTIAL | tests/claim-run.test.sh<br>tests/canonical-state-rotation.test.sh (native_preparation_test, native_or_rotation_test, canonical_reader_test)<br>Sol-DG18 7f954af15fd8958f0fe40a19ce0afd1b086deaaa handoff/astra-dg16-dg18/discussions/DG18-authentic-OR-and-cold-receiving.md "Sol-DG18 ordinary consumer receiving of V21" (Windows Py3.11): RealHelperIntegration.test_real_helper_migrates_real_main_receipt_and_separate_readers rc 0 stderr 0432353ae2901de77b68763b44d6fc52a5c1f56e544d83c22669265254a3e264<br>pin coherence verified: every changed byte/sha256 pin in this member equals the V21 sibling body (git show 338c4c36)<br>claim-run: rc=0 stderr_sha256=056be428f93d5c221fb5111f4d266e542ea3d7ce13f6fa95f050091739b87b53<br>canonical-state-rotation: rc=0 stderr_sha256=3eddf690cba5a109045bafdfb9c873593cfe9ccd6b7c22a3e0617d0faf132c5f<br>Sol-DG18 7f954af15fd8958f0fe40a19ce0afd1b086deaaa handoff/astra-dg16-dg18/discussions/DG18-authentic-OR-and-cold-receiving.md "Sol-DG18 ordinary consumer receiving of V21" (Windows Py3.11): RealHelperIntegration.test_real_helper_migrates_real_main_receipt_and_separate_readers rc 0 stderr 0432353ae2901de77b68763b44d6fc52a5c1f56e544d83c22669265254a3e264 | For review (DG18 OR scope, off the native-intake path): an H0 mechanical template without exactly one literal OWNED_STDIO_SELECTION_PIN now raises "private native selector is not one declared literal" instead of returning None. The pinned siblings carry their own residuals. |
| 12 | `skills/implementaudit/scripts/claim-run.sh` | d5670374, a84b5b6c, d298e64c, 09cef7dd, ae6a48c9, 11538085, ca06d866, 9a71560f, c36c8833, fb8177fd, 53a80108, 11c0dbd0, 1b6b8911, 14adb7c4 | c | PARTIAL | tests/claim-run.test.sh<br>tests/canonical-state-rotation.test.sh<br>pin coherence verified: every changed byte/sha256 pin in this member equals the V21 sibling body (git show 338c4c36)<br>claim-run: rc=0 stderr_sha256=056be428f93d5c221fb5111f4d266e542ea3d7ce13f6fa95f050091739b87b53<br>canonical-state-rotation: rc=0 stderr_sha256=3eddf690cba5a109045bafdfb9c873593cfe9ccd6b7c22a3e0617d0faf132c5f<br>Sol-DG18 7f954af15fd8958f0fe40a19ce0afd1b086deaaa handoff/astra-dg16-dg18/discussions/DG18-authentic-OR-and-cold-receiving.md "Sol-DG18 ordinary consumer receiving of V21" (Windows Py3.11): RealHelperIntegration.test_real_helper_migrates_real_main_receipt_and_separate_readers rc 0 stderr 0432353ae2901de77b68763b44d6fc52a5c1f56e544d83c22669265254a3e264 | The pin is coherence-only. The semantic residual lives in claim-run-rotation.py. |
| 13 | `skills/implementaudit/scripts/compile-work-graph.py` | b41051e2, 300aa000, 768bd734, ed8843c5, 6bfcaf90, 02852b65, 6729f156, 5a285255, daaa0819, 9a0bda46, 15a411ca, 8e4d4baf, fc3534f0, bf8b986e, 53a80108, 51416b2f, 1b6b8911, 14adb7c4, 8ee4ae44<br>since e76: b41051e2, 300aa000, 768bd734, ed8843c5, 6bfcaf90, 02852b65, 6729f156, 5a285255, daaa0819, 9a0bda46, 15a411ca, 8e4d4baf, fc3534f0, bf8b986e, 53a80108, 51416b2f, 1b6b8911, 14adb7c4 | c | PARTIAL | tests/work-graph-compiler.test.sh<br>tests/native-work-graph.test.sh case files other than the two maintained native bodies<br>Sol-DG17 2485bf5270c87026c275c33143a48aee99d4fa40 handoff/sol-dg17-20261122/CONTINUATION.md "Exact V21 joined source and artifact qualification": clean WSL composite-source wrapper rc 0 (85 composite cases, 20 C5 source receiving, 6 original14 history cases), stderr 24235e75815885fd0ec5eb1d8bf8cf8502fb14d01c1de0d60d5e1b0d452e1f73<br>ast_delta.py e76a07b2..338c4c36: only the 5 Assign targets listed differ<br>pin coherence verified: every changed byte/sha256 pin in this member equals the V21 sibling body (git show 338c4c36)<br>work-graph-compiler: rc=0 stderr_sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855<br>wg-continuity-cases: rc=0 stderr_sha256=7c3a9b301de18146337fba454d938d99a91de6dd17bf92acf157a4658dd74c14<br>wg-source-observation-cases: rc=0 stderr_sha256=f8198396cd4a1c7c75d45a25bdfd686b75836051780e9d658e624ea6e1f69bb6<br>Sol-DG17 2485bf5270c87026c275c33143a48aee99d4fa40 handoff/sol-dg17-20261122/CONTINUATION.md "Exact V21 joined source and artifact qualification": clean WSL composite-source wrapper rc 0 (85 composite cases, 20 C5 source receiving, 6 original14 history cases), stderr 24235e75815885fd0ec5eb1d8bf8cf8502fb14d01c1de0d60d5e1b0d452e1f73 | The compiler logic is unchanged since the reviewed e76 delta. Its pins select the OPEN receiver and transport. native_prerequisite.py@b393a905 pins COMPILER_SHA 0aa4572a/262144; V21 is e65f13db/261264. compiler_normalized_ast_sha256 d655e326 has no qualified producer, so no V21 value exists. |
| 14 | `skills/implementaudit/scripts/host-session-binding.py` | 5900a598, 76d47406, d10264be | b | COVERED | tests/host-session-binding.test.sh<br>tests/host-session-binding-hardening.test.sh<br>tests/host-session-terminal.test.sh<br>host-session-binding: rc=0 stderr_sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855<br>host-session-binding-hardening: rc=0 stderr_sha256=2f7e12b09f59bcbe4cff020a537884a4c30a3ac2b6e0c52719f3b928b8b12eaa<br>host-session-terminal: rc=0 stderr_sha256=e3cc70f7ea2f67e90d9efdfababe5e452584137afdb4f72f7e1f1309a23053d3 | Windows host Stop/binding native behaviour is DG17/DG18 scope, outside this Linux applicability. |
| 15 | `skills/implementaudit/scripts/host-stop-interlock.py` | defa480b, 5900a598, 8caa0922, 76d47406, d10264be, 1b6b8911, 4a50065d, 14adb7c4 | b | COVERED | tests/host-session-binding.test.sh<br>tests/host-session-binding-hardening.test.sh<br>tests/host-session-terminal.test.sh<br>tests/nonterminal-yield-cases.py via tests/run-root-validation.test.sh<br>host-session-binding: rc=0 stderr_sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855<br>host-session-binding-hardening: rc=0 stderr_sha256=2f7e12b09f59bcbe4cff020a537884a4c30a3ac2b6e0c52719f3b928b8b12eaa<br>host-session-terminal: rc=0 stderr_sha256=e3cc70f7ea2f67e90d9efdfababe5e452584137afdb4f72f7e1f1309a23053d3<br>run-root-validation: rc=0 stderr_sha256=f03cb17d9dad7a8afbc03075f86225b93f6ff3d8d89ac4fd2919fd065128eba7 | Windows Stop qualification is DG17 scope. |
| 16 | `skills/implementaudit/scripts/read-canonical-pair.py` | 14ed4c71, 11c0dbd0 | b | COVERED | windows_qualification_test.WindowsRuntimeGitLayoutControls (canonical-state-rotation.test.sh:17)<br>canonical_reader_test (canonical-state-rotation.test.sh:19)<br>ast_delta.py 3e0f4b6d..338c4c36: only FunctionDef:call differs<br>canonical-state-rotation: rc=0 stderr_sha256=3eddf690cba5a109045bafdfb9c873593cfe9ccd6b7c22a3e0617d0faf132c5f<br>Sol-DG18 7f954af1 same record: CanonicalReaderTests.test_actual_native_owner_pair_reads_are_ordered_and_token_bound rc 0 stderr 543b42af93a2d2f1cdd6c6382342698da999b790cc4acfef843897ac9ecca612 | The bytes are still a member of the 8-file continuity tuple admitted by operational-evidence.py (OPEN). |
| 17 | `skills/implementaudit/scripts/repo-state.sh` | 2e72a912, 6f422597, 0cf89c2b, 858906e7, 3027f796, e31e5b60, cd7d9ffb | b | COVERED | tests/repo-state.test.sh<br>repo-state: rc=0 stderr_sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | None for the native predicates. |
| 18 | `skills/implementaudit/scripts/rotate-canonical-state.py` | 11538085, 53a80108, 11c0dbd0 | c | PARTIAL | native_input_adapter_test.test_archive_schema_is_bound_to_exact_window_calibration<br>tests/canonical-state-rotation.test.sh<br>Sol-DG18 7f954af15fd8958f0fe40a19ce0afd1b086deaaa handoff/astra-dg16-dg18/discussions/DG18-authentic-OR-and-cold-receiving.md "Sol-DG18 ordinary consumer receiving of V21" (Windows Py3.11): RealHelperIntegration.test_real_helper_migrates_real_main_receipt_and_separate_readers rc 0 stderr 0432353ae2901de77b68763b44d6fc52a5c1f56e544d83c22669265254a3e264<br>Sol-DG18 7f954af1 same record: ArchiveQualification.test_actual_archive_gc_retention_typed_retrieval_and_no_current_authority rc 0 stderr b5916752ba42b16e60848dc22eaf45f0acca2cd1d9174ccbe56b5bba200b21b5<br>pin coherence verified: every changed byte/sha256 pin in this member equals the V21 sibling body (git show 338c4c36)<br>calib_equiv.sh (WSL Py3.12.3) imports both revisions: full_or_equal_except_module_pin=True; token_contract_equal=True; old_historical (5 rows) is a subset of new (7 rows); the 2 added rows are R0039-F1-CAL-v2 and R4-FRESH-NATIVE-OR-CANARY-v1 at 33c9ae52<br>canonical-state-rotation: rc=0 stderr_sha256=3eddf690cba5a109045bafdfb9c873593cfe9ccd6b7c22a3e0617d0faf132c5f<br>Sol-DG18 7f954af15fd8958f0fe40a19ce0afd1b086deaaa handoff/astra-dg16-dg18/discussions/DG18-authentic-OR-and-cold-receiving.md "Sol-DG18 ordinary consumer receiving of V21" (Windows Py3.11): RealHelperIntegration.test_real_helper_migrates_real_main_receipt_and_separate_readers rc 0 stderr 0432353ae2901de77b68763b44d6fc52a5c1f56e544d83c22669265254a3e264<br>Sol-DG18 7f954af1 same record: ArchiveQualification.test_actual_archive_gc_retention_typed_retrieval_and_no_current_authority rc 0 stderr b5916752ba42b16e60848dc22eaf45f0acca2cd1d9174ccbe56b5bba200b21b5 | For review: the historical calibration set is a strict superset (+2 live rows at the new module pin), and dc95 v2-schema archive mapping is retained. The value equivalence of the full-OR literal is mechanically shown. There is no native observation of rotation at V21. |
| 19 | `skills/implementaudit/scripts/validate-run-root.sh` | d80c1e3a, f598bd6f, fd8942f6, a0fc7788, 658d4995, be670382, f60f8817, 9ee33444, 1b6b8911, 14adb7c4 | c | OPEN | tests/run-root-validation.test.sh (incl. nonterminal-yield-cases.py, turn-disposition-cases.py)<br>tests/claim-run.test.sh<br>tests/continuity-contract.test.sh<br>tests/evidence-anchoring.test.sh<br>tests/andon-class-contract.test.sh<br>tests/composite-source-cases.py OWNER_TIMEOUT cases<br>run-root-validation: rc=0 stderr_sha256=f03cb17d9dad7a8afbc03075f86225b93f6ff3d8d89ac4fd2919fd065128eba7<br>claim-run: rc=0 stderr_sha256=056be428f93d5c221fb5111f4d266e542ea3d7ce13f6fa95f050091739b87b53<br>continuity-contract: rc=0 stderr_sha256=9445bec30e46f37454928c755f735769c4edba0e7c9cf95924d03ac72abf836f<br>evidence-anchoring-shim: rc=0 stderr_sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855<br>andon-class-contract: rc=0 stderr_sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855<br>Sol-DG17 2485bf5270c87026c275c33143a48aee99d4fa40 handoff/sol-dg17-20261122/CONTINUATION.md "Exact V21 joined source and artifact qualification": clean WSL composite-source wrapper rc 0 (85 composite cases, 20 C5 source receiving, 6 original14 history cases), stderr 24235e75815885fd0ec5eb1d8bf8cf8502fb14d01c1de0d60d5e1b0d452e1f73 | The changed validator semantics have not been observed inside the native continuity at V21. Independent review should check whether owner TMPDIR isolation, sibling-run parallel capture and current_andon_rows parsing are inert for the constructed original14 run root. |
| 20 | `skills/implementaudit/templates/PROTOCOL.md` | 7e2f9407, 329ff297, be74fe66, b4335c33, a0fc7788, 14adb7c4 | b | COVERED | tests/run-root-validation.test.sh<br>tests/continuity-contract.test.sh<br>tests/evidence-anchoring.test.sh<br>tests/andon-class-contract.test.sh<br>canonical_reader_test initialization (canonical-state-rotation.test.sh:19)<br>run-root-validation: rc=0 stderr_sha256=f03cb17d9dad7a8afbc03075f86225b93f6ff3d8d89ac4fd2919fd065128eba7<br>continuity-contract: rc=0 stderr_sha256=9445bec30e46f37454928c755f735769c4edba0e7c9cf95924d03ac72abf836f<br>evidence-anchoring-shim: rc=0 stderr_sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855<br>andon-class-contract: rc=0 stderr_sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855<br>canonical-state-rotation: rc=0 stderr_sha256=3eddf690cba5a109045bafdfb9c873593cfe9ccd6b7c22a3e0617d0faf132c5f | Agent-facing procedure change. Its enforcement lives in validate-run-root.sh (OPEN). |

## Change and reach notes

**1. `fixtures/canonical-state-rotation/native_input_adapter_test.py`** (36766 B `2ec280c74c75` -> 37627 B `4e3033424e63`)

- Change: Test-only: adds test_null_wire_metadata_preserves_exact_usage_without_admitting_bad_metadata and, in test_archive_schema_is_bound_to_exact_window_calibration, admits rotation.NATIVE_INPUT_MODULE_SHA256 among v2 producers plus a live-to-historical calibration retention assertion.
- Native reach: Not executed by native_probe (not imported by the two maintained case bodies or canonical_reader_test).

**2. `fixtures/canonical-state-rotation/native_preparation_test.py`** (46702 B `f3bdf2738770` -> 58021 B `0382e64e8868`)

- Change: Test-only: adds OR_SOURCE_TEMPLATE and seven PreparationControls cases (prospective rotation source, selected template live-host gate, C02 capture grant/driver/owned transport, armed owned transport, unselected source refusal); PortableFactoryLoaderControls retargeted.
- Native reach: Not executed by native_probe.

**3. `fixtures/canonical-state-rotation/owned_stdio_source_boundaries_test.py`** (33063 B `e166953fae13` -> 33227 B `528f1e693d07`)

- Change: Fixture copies compaction-prior-protocol.py and compaction-prior-mcp.py into the constructed fixture (e61ead42). V21 bytes equal e76a07b2 and equal the historically admitted repair pin 33227 B / 528f1e693d0745b90a8ea2ededd570962f929e8f2c76b115c6e011386a03e0f7.
- Native reach: Not executed by native_probe; this is the single historically admitted fixture repair.

**4. `fixtures/canonical-state-rotation/protected_projection_v2_test.py`** (39677 B `926d68a0588e` -> 40925 B `8a34e4f6c5d7`)

- Change: Adds subtests in test_accepted_witness_covers_only_exact_observation_and_occurrence_scope and test_physical_source_selected_occurrence_prior_retry_and_refusal_are_protected (53a80108). Top-level AST delta is limited to ClassDef ProjectionV2Qualification; module-level render_pair/build_owner_map are unchanged.
- Native reach: canonical_reader_test.make_real_generation execs this module as a factory on the native path, but uses only render_pair and build_owner_map, which are AST-identical; the test methods are not executed by native_probe.

**5. `fixtures/canonical-state-rotation/windows_qualification_test.py`** (39255 B `18ccebe67568` -> 44681 B `ef3f0aba8b7b`)

- Change: Test-only: adds WindowsRuntimeGitLayoutControls (ucrt64/mingw64 Git selection) (11c0dbd0).
- Native reach: Not executed by native_probe; it controls os.name=="nt" branches only.

**6. `fixtures/controller-initialization/author_checkpoint.py`** (9420 B `8ca871eaf6a1` -> 9582 B `fa875136c9b8`)

- Change: --activate/--activate-only now resolve bash once through shutil.which and pass the absolute path as argv[0], refusing when bash is absent; previously the literal "bash" (14adb7c4).
- Native reach: Executed on the native path: CanonicalReaderTests.setUp runs author_checkpoint.py --activate.

**7. `scripts/operational-evidence.py`** (422638 B `a3981bfac0c9` -> 441955 B `28d1b5d0a3dc`)

- Change: e76a07b2..V21 (3e0f4b6d..e76 is the historically reviewed 8ee4ae44 delta): purely additive data. There are 15 new _NATIVE_CONTINUITY_SOURCE_PROFILES_V1 rows and 15 new _NATIVE_CONTINUITY_TRANSPORT_PROFILES_V1 entries. _native_check_continuity_closure_v1 changes only by 14 helper pairs inside its os.name=="nt" tuple. There are no deletions.
- Native reach: This is the native static owner and receiver (RECEIVER). On Linux, the V21 8-file helper tuple (claim-run.sh c059ad1b, validate-run-root.sh 9ff4ffb1, claim-run-rotation.py 824194fe, rotate-canonical-state.py 008d63f4, canonical_hot_projection.py 6ff0fe34, canonical_custody.py d52369e5, canonical_rotation_inputs.py 33c9ae52, read-canonical-pair.py 733964e5) is admitted only by the newly added last row ("prospective OR-rotation initializer and validator joined at a84b5b6c+8f59b2c8").

**8. `scripts/work-graph-continuity-transport.py`** (93973 B `a6ecc502ef72` -> 112819 B `4b7c944ce243`)

- Change: Additive: 16 new SOURCE_PROFILES_V1 entries (plus the _N07_PREDECESSOR_PROFILE alias) and 14 Windows core-8 pair constants. _windows_core_profile_v1 gains those pairs and is evaluated only under os.name=="nt". The bytes equal 3e0f4b6d at e76a07b2, so the historical record counted this member unchanged.
- Native reach: Loaded by the compiler native continuity (pin _NATIVE_CONTINUITY_TRANSPORT 112819/4b7c944c). On Linux, the V21 tuple selects the new "composite-20261125-dg18-or-rotation-v1-core" profile. ORIGINAL14_SOURCE_PROFILES_V1 gains two mode-None overlays whose claim-run.sh (104155 B) cannot match the V21 32290-byte helper.

**9. `skills/implementaudit/scripts/canonical_hot_projection.py`** (93893 B `10f852a7b574` -> 94767 B `6ff0fe3414f1`)

- Change: New refusals (53a80108). _v2_pending_rows: a SUPPORTED_RETRY original_occurrence_id must be the selected or a prior occurrence. parse_canonical_pair_v2: an accepted witness and a SUPPORTED_RETRY must bind an EVIDENCE artifact_ref of the pending row owner.
- Native reach: This is the v2 canonical pair parser, used by rotation and pair reads on the native path (rotate-canonical-state pins it as 94767/6ff0fe34).

**10. `skills/implementaudit/scripts/canonical_rotation_inputs.py`** (27916 B `dc95d31e4a1f` -> 27931 B `33c9ae520aa7`)

- Change: parse_exact_usage_v1 accepts params.usageMetadata == None (previously only absent or dict) (11538085). The AST delta is limited to that function.
- Native reach: parse_exact_usage_v1 is reached only through the OR native-input lease/record routes (codex host usage), not the original14 cases. The internal rotate-canonical-state call sites build params without usageMetadata, where the old and new predicates agree.

**11. `skills/implementaudit/scripts/claim-run-rotation.py`** (291624 B `128dfe66ce65` -> 292218 B `824194feede2`)

- Change: Pins move to V21 rotate-canonical-state.py (127141/008d63f4) and V21 validate-run-root.sh (126682/9ff4ffb1). Windows-only ucrt64 Git selection is added (nt branches). A second reviewed OR source-owner template (3d10e2cd) is added: the H0 shortcut is now evaluated after selector parsing, and native_preparation_for_owned_stdio_v1(owned_observation=) is new.
- Native reach: Executed on the native path (claim, initialization, --invalidate-continuity). The OR selection code is unreachable there: _private_native_input_selection_v1 returns None at "if not path.exists()" because skills/implementaudit/scripts/compaction-source-owner-codex-app.py is absent at V21. The Linux-reachable delta is therefore the two pins.

**12. `skills/implementaudit/scripts/claim-run.sh`** (32290 B `9bce5c887cd8` -> 32290 B `c059ad1b409d`)

- Change: Pin-only: embedded expected claim-run-rotation.py identity 291624/128dfe66 -> 292218/824194fe.
- Native reach: Executed on the native path. The only delta is the pin, which selects the V21 claim-run-rotation.py.

**13. `skills/implementaudit/scripts/compile-work-graph.py`** (262144 B `3649a8dc856e` -> 261264 B `e65f13db74a2`)

- Change: e76a07b2..V21 (3e0f..e76 is the historically reviewed 8ee4ae44 delta). The top-level AST differs only in: _NATIVE_STATIC_OWNER_{SHA256,BYTES} (to receiver 28d1b5d0/441955), _NATIVE_CONTINUITY_TRANSPORT_{SHA256,BYTES} (to 4b7c944c/112819), and _NATIVE_ROUTE_PRODUCER_PROFILES_V1, which consolidates 9 assignments into one literal and adds 15 producer profiles (all 21 e76 entries retained with equal values: 21 -> 36). Everything else is comment compaction.
- Native reach: This is the native compiler (COMPILER). The route-producer table is unreachable in the native cases: skills/implementaudit/scripts/route-transaction.py is absent at 3e0f4b6d, e76a07b2 and 338c4c36, so _observe_native_run_current_sources_v1 takes the FileNotFoundError branch (route_available=False; ROUTE_PRODUCER_UNAVAILABLE, as the unchanged case test_native_intake_uses_current_original14_not_retired_root expects). The Linux-reachable delta is the two pins.

**14. `skills/implementaudit/scripts/host-session-binding.py`** (58351 B `8b4f91a51e2e` -> 65831 B `f37015a4256d`)

- Change: Windows store custody (windows_custody/security/private/store_directory/store_write), typed first-activation custody, and lookup_binding refactor (d10264be, 76d47406, 5900a598). os.name "nt" admitted.
- Native reach: Not invoked by any native-path owner (no reference from claim-run.sh, claim-run-rotation.py, rotate-canonical-state.py, validate-run-root.sh, read-canonical-pair.py, compile-work-graph.py, operational-evidence.py or the case bodies). It is copied into the constructed scripts dir only.

**15. `skills/implementaudit/scripts/host-stop-interlock.py`** (27873 B `b9ac38ecbda0` -> 35420 B `75e4cf425d22`)

- Change: DG17 selected Stop v3: binding-owner-selected fallback argv, exact active binding, activation custody drift, Windows descendant containment (d10264be, 76d47406, 8caa0922, 5900a598, defa480b, 4a50065d).
- Native reach: Not invoked by any native-path owner (same reference check as host-session-binding.py).

**16. `skills/implementaudit/scripts/read-canonical-pair.py`** (27208 B `c2868db4f385` -> 27024 B `733964e51ed4`)

- Change: Docstring/comment compaction. The top-level AST differs only in FunctionDef call, inside its os.name=="nt" branch (ucrt64 then mingw64 Git) (11c0dbd0, 14ed4c71).
- Native reach: Executed on the native path (--native-guards), but the changed lines are Windows-only; the Linux behaviour is AST-identical.

**17. `skills/implementaudit/scripts/repo-state.sh`** (22629 B `b2220d0627c5` -> 24515 B `12ff66dc1a71`)

- Change: 5S census: link-object classification, rename membership, private-scratch exclusion, deterministic acquisition/text boundaries, hunk-based added-content detection, staged/committed evidence, normal pre-stop L4 route.
- Native reach: Not invoked by any native-path owner. It is copied into the constructed scripts dir only; canonical_reader_test reads references/repo-state-comparison.md, not this script.

**18. `skills/implementaudit/scripts/rotate-canonical-state.py`** (129890 B `7112fdbe9722` -> 127141 B `008d63f41e64`)

- Change: Pins move to hot projection 94767/6ff0fe34 and native input module 27931/33c9ae52. Windows ucrt64 Git path and PATH (nt). full_or_calibration_contract_v1 is rewritten as a literal. _historical_or_calibrations_v1 is regenerated and retains the dc95 producer as _RETAINED_WINDOW_INPUT_SHA256. _check_native_input_record v2_producers adds dc95.
- Native reach: Executed on the native path (rotation). The calibration and native-input-record changes govern OR/native-input manifests. The Linux-reachable delta in the original14 cases is the pins plus calibration membership checks.

**19. `skills/implementaudit/scripts/validate-run-root.sh`** (114967 B `d51d7355a3ca` -> 126682 B `9ff4ffb1503c`)

- Change: Substantial POSIX-reachable validator logic changes:
- per-owner private TMPDIR with removal and a refusal if it is not removed;
- OwnerTimeout -> OWNER_TIMEOUT disposition kind;
- live-owner stop on exit;
- current_andon_rows (case-insensitive headers, indented tables, unique row identity) shared by closure and handoff;
- case-insensitive Andon heading;
- DONE-phase "expected: output line" capture checks;
- one unambiguous Current phase record;
- NONTERMINAL_YIELD concurrent structural run with review-owner fence;
- parallel sibling-run captures (max 4).
It also adds Windows job-object owner containment (nt).
- Native reach: Executed on the native path: it is the validate half of the claim/validate helper pair evaluated by the compiler native continuity, and it is pinned by claim-run-rotation initialization.

**20. `skills/implementaudit/templates/PROTOCOL.md`** (73424 B `4e006be6c32d` -> 72555 B `af651637a779`)

- Change: Procedure text: prose compaction and a new normal-gate rule declaring Smoke "expected: output line <literal>" (a0fc7788). Also: finding-row anchor restored (7e2f9407), evidence-anchor route restored (329ff297), OR pin scope wording (b4335c33, be74fe66). No implementaudit-work-graph fences at either revision.
- Native reach: Copied into the constructed run root by initialization and validated for required anchors by validate-run-root.sh. It contributes no native graph source (0 work-graph fences at 3e0f4b6d and 338c4c36).

## Commit subjects

- `11538085` Compose distinct unselected OR source materialization [skip ci]
- `19587dbe` Compose unselected DG18 capture and repair carried text [skip ci]
- `e61ead42` Include both prior-protocol sources in the constructed identity fixture
- `53a80108` Compose corrected DG18 A5 owners with exact DG16 readers [skip ci]
- `11c0dbd0` Restore accepted UCRT64 Git selection in integrated continuity runtime
- `14adb7c4` Guard DG17 Windows owner containment and preserve source closure
- `b41051e2` Compose exact Stage B readers and final DG17 compiler pins [skip ci]
- `529f2a53` DG16: prospective readers for the OR-rotation initializer pair at a84b5b6c [skip ci]
- `6729f156` Compose the 5S readers and derive exact compiler pins [skip ci]
- `fe569146` DG16: bind prospective readers to the T14 initializer and validator
- `fd516dee` DG16: bind prospective readers to the joined DG18 OR core
- `8d2a2918` DG16: add the original14 peer overlay for the DG18 A5 hot projection
- `ba5df5ce` DG16: bind prospective readers to the shared-successor initializer and validator
- `11762d9f` Compose the Current phase continuity reader tuple [skip ci]
- `39e6a7a7` Join the exact N07 readers and DIST test correction [skip ci]
- `51416b2f` Fix current continuity source selection and preserve historical profiles
- `1b6b8911` Integrate reviewed R3 containment and source corrections
- `8ee4ae44` Bind the current Windows continuity receiver and scoped C5 source successor
- `d5670374` Compose DG18 qualified Stage B source and prospective alias pins [skip ci]
- `860c282c` Compose DG18 prospective OR source identity and shared alias pins [skip ci]
- `d298e64c` Bind the shared initializer to the measured 5S prejoin validator [skip ci]
- `09cef7dd` Bind the shared initializer to the T14 Andon validator
- `ae6a48c9` Bind the prospective OR initializer to the Smoke B validator
- `ca06d866` Bind initializer to exact duplicate-Andon diagnostic validator
- `9a71560f` Bind prospective initializer to shared successor validator
- `c36c8833` Bind initialization to prospective Current-phase validator
- `fb8177fd` Bind initializer to frozen N07 validator bytes [skip ci]
- `a84b5b6c` Pin the claim shell to the composed prospective OR owner [skip ci]
- `300aa000` Recover mandatory reserve with compiler comment-only changes [skip ci]
- `768bd734` Bind the revised Stage B initializer to the prospective route [skip ci]
- `ed8843c5` Bind both compilers to the exact prospective OR readers [skip ci]
- `6bfcaf90` Bind the exact prospective OR initializer to the route receiver [skip ci]
- `02852b65` Fit both 5S compilers under the bounded source cap [skip ci]
- `5a285255` Bind the verified 5S initializer pair to the prospective route [skip ci]
- `daaa0819` PROPOSAL for DG17: T14 route pair, compiler pins and route manifest
- `9a0bda46` Bind both compilers to the prospective OR readers [skip ci]
- `15a411ca` Bind exact shared successor readers and route in both compilers [skip ci]
- `8e4d4baf` Pin both Current phase readers and prospective route in the compilers [skip ci]
- `fc3534f0` Match compilers to the exact N07 operational reader [skip ci]
- `bf8b986e` Derive compiler pins from composed N07 source [skip ci]
- `5900a598` Add Windows custody for typed first host-session activation [skip ci]
- `76d47406` Keep Stop fallback closed on activation custody drift
- `d10264be` Implement DG17 selected Stop v3 and structural acceptance checks
- `defa480b` Require exact active binding for selected v3 Stop [skip ci]
- `8caa0922` Select Stop fallback argv according to the pinned binding owner [skip ci]
- `4a50065d` Contain DG17 Windows Stop descendants and adopt bounded reserve revision 5
- `14ed4c71` Restore required package reserve with concise reader documentation
- `2e72a912` Classify untracked link objects before reading census text [skip ci]
- `6f422597` Fix census rename membership and exclude private scratch [skip ci]
- `0cf89c2b` Qualify deterministic 5S census acquisition and text boundaries [skip ci]
- `858906e7` Distinguish added content from file headers by diff hunk [skip ci]
- `3027f796` Recover 5S successor archive margin in helper comments [skip ci]
- `e31e5b60` Preserve staged and committed evidence in 5S census [skip ci]
- `cd7d9ffb` Make the normal pre-stop L4 route executable [skip ci]
- `d80c1e3a` Select current Andon rows for closure and audited handoff [skip ci]
- `f598bd6f` Recover package reserve in validator implementation comments [skip ci]
- `fd8942f6` Reject ambiguous Andon row identity before readiness [skip ci]
- `a0fc7788` Require declared Smoke output at the normal phase admission gate [skip ci]
- `658d4995` Keep duplicate Andon header diagnostic and retain M06 mutations [skip ci]
- `be670382` Share one Andon table between structure and dispatch checks [skip ci]
- `f60f8817` Bind normal readiness to one unambiguous Current phase record [skip ci]
- `9ee33444` Refuse current unresolved Andon before dispatch [skip ci]
- `7e2f9407` Restore the required protocol finding-row anchor [skip ci]
- `329ff297` Restore the evidence anchor procedural route after compaction [skip ci]
- `be74fe66` Bind the prospective OR route and preserve qualification headroom [skip ci]
- `b4335c33` Correct OR member pin scope and preserve the v4 reserve [skip ci]

## Local ordinary runs (fresh WSL clone of V21)

fresh WSL Ubuntu clone of 338c4c36 (git clone --no-checkout + checkout; clean status), python3 3.12.3, env -i, private TMPDIR; tests/native-work-graph.test.sh (maintained native case bodies) and the native probe deliberately NOT run

- `andon-class-contract`: rc 0, stdout `622a5ce6368f43ecd7eca2d4d5e3a8e23480f75cfa2efbeb55280676928d6a73`, stderr `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `canonical-state-rotation`: rc 0, stdout `71b66f2496209ff5f7c4b424dc0dd662d92aa0608da96345c5c23b8c544ff12e`, stderr `3eddf690cba5a109045bafdfb9c873593cfe9ccd6b7c22a3e0617d0faf132c5f`
- `claim-run`: rc 0, stdout `cd3ce625fa4e55b81518d8332233f701238d237145f8452aeb70821c4d35219f`, stderr `056be428f93d5c221fb5111f4d266e542ea3d7ce13f6fa95f050091739b87b53`
- `continuity-contract`: rc 0, stdout `3ec7b737abe4a68a1262624494bd166b294ecb5b45df7f9af2c04bbb036482e1`, stderr `9445bec30e46f37454928c755f735769c4edba0e7c9cf95924d03ac72abf836f`
- `evidence-anchoring`: rc 127, stdout `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, stderr `b71c9b9f7aaf2de98bfc97aa6d5868839533aac935e03683bd709ddf871fa411`
- `evidence-anchoring-shim`: rc 0, stdout `e82862542e825b6fd014247b627d9d63a92c7ce85653ed0f5b701f2a2530815c`, stderr `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `host-session-binding`: rc 0, stdout `bb2a599add1f310364e1fb9094e5559e5e0e7a2f8289ffa02a5a08ce7bad14b8`, stderr `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `host-session-binding-hardening`: rc 0, stdout `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, stderr `2f7e12b09f59bcbe4cff020a537884a4c30a3ac2b6e0c52719f3b928b8b12eaa`
- `host-session-terminal`: rc 0, stdout `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, stderr `e3cc70f7ea2f67e90d9efdfababe5e452584137afdb4f72f7e1f1309a23053d3`
- `operational-evidence-contract`: rc 0, stdout `22c263cc40c9b8996e21f6da32da000046e03a7dd7cc867fb471f59b58bb264f`, stderr `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `repo-state`: rc 0, stdout `77496276f0f21b2d2d1b67dca4d8b2adb0508933fce2d834dc98798ba6f91b3e`, stderr `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `run-root-validation`: rc 0, stdout `22c1bfde3c44bfa896ec228c1a627e64980edac0a0636e02de1df2c9195cda04`, stderr `f03cb17d9dad7a8afbc03075f86225b93f6ff3d8d89ac4fd2919fd065128eba7`
- `wg-continuity-cases`: rc 0, stdout `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, stderr `7c3a9b301de18146337fba454d938d99a91de6dd17bf92acf157a4658dd74c14`
- `wg-source-observation-cases`: rc 0, stdout `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, stderr `f8198396cd4a1c7c75d45a25bdfd686b75836051780e9d658e624ea6e1f69bb6`
- `work-graph-compiler`: rc 0, stdout `22b949e5d7af5b19b30d52630695d67fcff687eb8031ee4d9646e4e288256f32`, stderr `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
