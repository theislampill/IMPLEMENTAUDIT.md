# Task 1 repair round 2

**Ready for independent re-review.** All 33 focused checks passed, including 11 new repair controls, 16 prior lexical/projection controls, five historical byte comparisons and the actual public input receipt. The five historical outputs total 92,916 bytes. All nine recovered implementation and test files matched their pinned 595,916 bytes. The new candidate remains unaccepted pending Root review.

The governing admission is 2,376 bytes, SHA-256 `1d05bfbda5e1ce738142e76254c3c0637683f36fdf1705959929841251f241a1`. Separate reads of STATE and ROADMAP preceded an installed read-only G0003 check. The same check passed after the final readback. The receipt was `G0003@9ae8c11c90091bda3cc9b822341b9abcd6f530c3` both times. The dispatch requested gpt-6.2-astra at xhigh. The host response supplied no resolved-model attestation. The author can self-report Codex/GPT-6 only. Model-specific claims remain IDENTITY_UNBOUND.

## Findings and repairs

| Finding | Change | Observable result |
|---|---|---|
| R1-01, augmented global read | The temporary symbol-analysis tree makes a simple augmented target's implicit read explicit in its own lexical scope. The emitted source is untouched. | A nested increment selects its module COUNT. Its enclosing function parameter and nonlocal closure variable do not select same-named module declarations. A missing COUNT refuses unless supplied. |
| R1-02, compiler context | Dependency analysis uses the pinned runtime's postponed annotations context. Compile-only inspection checks source features against that context, and each returned basis records the compiler flags and runtime pin. Function, class and comprehension symbol analysis observes postponed annotations. | Sources with and without an explicit annotations future directive yield the same target-runtime closure for the fixture. An annotation-only type can be absent. A default value still selects its binding. The synthetic compiled annotation tuple, owner method flags and owner's three-argument compile call were independently asserted in the tests. An additional incompatible future feature refuses. |
| R1-03, module dictionary | An unshadowed direct literal lookup of a named module entry adds an explicit module dependency even if a parameter shadows the key. A missing dictionary entry cannot fall back to an ordinary builtin. The analysis refuses dynamic keys, direct namespace mutation, escaped/shadowed globals, namespace copies, explicit function-global attributes and FunctionType rebinding. | Controls check a selected declaration, registered supplier, runtime namespace entry, absent entry and absent builtin-only entry. Unsupported copy and rebinding examples refuse, including a minimized example of the G3 pattern. An access present only in a postponed annotation adds no runtime dependencies. |

The compiler policy is bound to the 38,161-byte runtime with SHA-256 `46a3e27dccb0b30dc75b4d20b7dca659ec5f4f8ae2a3e04c9ec175e577d3b743`. Its CurrentSources.module method inherits flag 16,777,216. The preserved runtime compiles its AST with three positional arguments. The independent R1 probe used standalone compilation with inheritance disabled. Root's compiler-context evidence establishes why the corresponding actual runtime behaves differently. The genuine proof_consumer source already declares future annotations. R2 accounts for both the actual target and any incompatible enclosing compiler feature. Standalone eager-annotation semantics are outside the basis claim.

The G3 owner contains a whole-dictionary copy with six keyword overrides at lines 759–761 and a types.FunctionType call at line 762. The enclosing function is receive_unchanged_package_successor. It belongs to neither the historical G3 roots nor the historical G3 declaration list. The pinned G3 runtime supplies its nine common names and current_original_scope_body. Its G3 registry has no types or Path, and the function also references __file__. A whole dictionary with overridden bindings is outside the finite literal-key policy. If an independently admitted after-basis reaches this owner, Root must decide its owner-grounded representation and runtime binding policy. R2 makes no reachability assertion about the after-basis and introduces no runtime capability.

The finite policy addresses statically identified namespace forms. It does not attempt a behavioral proof for arbitrary Python metaprogramming or values injected through external suppliers. Lexical scopes that shadow globals can conservatively refuse even when scope separation could distinguish them.

## Checks and custody

Commands used Python 3.12.14 with `-B`, from the new owner directory. `PYTHONPATH=tests` and the explicitly pinned `G132_TASK1_CONTEXT` select the test harness and public data. `TMPDIR` pointed inside the R2 report boundary. Existing receiver negative tests were unaffected by the repair. Text readback confirmed the receiver, path/descriptor/closing helpers and project_exact entry function remain byte-identical to their R1 definitions.

| Command after python -B -m unittest -v | Exit | Evidence and result |
|---|---:|---|
| test_joint_source.ProjectionRepair test_joint_source.Projection.test_shadowing_and_definition_time_dependencies | 1 | task-1-r2-red.log, 11 tests with 16 failed subtest assertions and three errors against R1 |
| test_joint_source.ProjectionRepair test_joint_source.Projection test_joint_source.OldProjections | 1 | task-1-r2-first-repair.log, 32 tests with two subtest assertions expecting an annotation string at the wrong constant-pool level. Python stores the key/value sequence in an annotation tuple. The test was corrected to assert that entire tuple. |
| test_joint_source.ProjectionRepair.test_other_explicit_namespace_copies_and_function_rebinding_refuse | 1 | task-1-r2-namespace-red.log, four unsupported forms initially passed |
| test_joint_source.ProjectionRepair test_joint_source.Projection test_joint_source.OldProjections | 0 | task-1-r2-green.log, final 33/33 passed |

A separate standard-library byte readback exited 0. It verified the unchanged nine original source pins, all frozen R1 inventory entries, the R1 evidence files still present in the candidate, and the named unchanged definitions. The current public-role receiver control checked 190 roles / 5,999,010 bytes including the new 23,942-byte generator. Its destination remained absent. No original owner was executed. No full new-source derivation, original operation, Git mutation, remote write, historical rerun or award was issued by this repair. Authority NONE.

| R2 artifact | Bytes | SHA-256 |
|---|---:|---|
| restoration/derive_joint_source.py | 23,942 | 081a844e9d5a9877439a2f6490a9452b4dea73f2dfec059adeeda365ec9a30e4 |
| tests/test_joint_source.py | 23,009 | 3f13a9575ec75ee3aad3a9e1f2fa9baf82ff44e96a9f6eab3d86f06c6c5e8457 |
| task-1-r2-review.diff | 17,192 | c7553a7fb4cff61f6f71a35255dead0fb7a3925449a6c4c3d07dcbce4b99146c |
| task-1-r2-readback.json | 5,678 | bf5eac3d0c80ff8055e1ad6774f37d75c9fdb369bea2e4d41468be3eb34199c5 |

The review diff is the complete R1-to-R2 delta of both amended files. Its hunks were applied in memory against frozen R1 and the reconstructed bodies were checked byte-for-byte. The R2 inventory pins both source files, the before/after readback, the diff, all four test observations and this report. The inventory has a detached handoff pin. R1 evidence retains its original names and identities.
