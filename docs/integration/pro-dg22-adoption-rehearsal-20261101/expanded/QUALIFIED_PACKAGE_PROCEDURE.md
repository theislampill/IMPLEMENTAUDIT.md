# Qualified package-source procedure

## Decision and qualification

Build both canonical roles from the **exact prepared adoption commit**, in a
clean disposable checkout, with the existing supported builder and unchanged
strict verifiers. This directly satisfies `source.commit` consumers. It is
qualified at two accepted METHOD_ONLY identities, not at a final DG21 selection.

The published role `cdfec64a6dfad645f4b27a3a77562bc55c61c35c` has tree
`8cb97d13e2b4f5e8bf99cc3e6e17e9267cbdef77`. The engineering role
`c56ff57d4d2fd5d91ad6f2cc4be3d43eaa9a3642` has tree
`d0446a12550dca6c885a3c569ffed21a9ec7dcd1`. Each has only parent
`e78f7cb21af4197d490f10bc95917a4c75f748aa`. Exact source trees, blobs and modes
were preserved. Their historical retention and absence of donor ancestry are
the accepted method evidence; the nineteen controls were not repeated.

Both supported builder invocations completed with exit 0 and emitted a new
`IMPLEMENTAUDIT.plugin.zip`, `IMPLEMENTAUDIT.skill` and `CHECKSUMS.txt`. All four
explicit strict clean-source checks passed. The produced inventories identify
their actual new commit/tree, and all member bytes, modes, population, role,
identity guards and package budgets are checked by the original verifier.
No archive or inventory was relabeled. Exact SHA-256 values and sizes are in
`PACKAGE_RESULTS.json`.

## Reproduction at a genuine selected candidate

1. Receive the selected source/tree from Sol and source-writing authority from
   CE021. Freeze the new commit's tree, one parent, message, author/committer
   identities and timestamps. Read back the resulting commit object. Changing
   any commit identity input requires newly identified packages.
2. Create a clean detached disposable checkout of that exact commit. Build
   outputs and Python environment must be outside the checkout. Verify HEAD,
   parent, source/adoption tree equality, complete `git ls-tree --full-tree -rz`
   equality and clean status. Keep the selected source and all donor history
   carriers reachable. Do not import their ancestry through the adoption parent.
3. Use Python 3.12 with a private environment containing `zopfli==0.2.3.post1`.
   This execution used Python 3.12.14, Git 2.51.1 and Bash 5.2.21 on Linux x86_64.
   Record actual versions again if the environment changes. The first dependency
   install was blocked by sandbox networking; the same pinned install succeeded
   after authorized network access. That first failure is retained.
4. From the exact checkout execute, with `OUT` a new external directory:

   ```sh
   bash scripts/build-release-asset.sh "$OUT"
   python scripts/package-contract.py --verify-artifact canonical_plugin "$OUT/IMPLEMENTAUDIT.plugin.zip" --require-clean-source
   python scripts/package-contract.py --verify-artifact standalone_compatibility "$OUT/IMPLEMENTAUDIT.skill" --require-clean-source
   bash scripts/write-release-checksums.sh --check --all "$OUT" "$OUT/CHECKSUMS.txt"
   ```

5. Receive actual archive SHA-256, inventory SHA-256, source commit/tree and clean
   state, complete members/bytes/modes, cap and reserve. The unchanged budget is
   589,824 bytes per role with a 2,000-byte required reserve. New builds retained
   13,709–19,163 bytes of total headroom.
6. Use the supported plugin, Codex standalone and Claude standalone copy
   installers in explicit new private roots. The plugin root must have the
   `.implementaudit-isolated-host-root` sentinel. Never use a real home. Separate
   plugin and standalone roots avoid an ambiguous co-installation. Verify every
   installed member against the actual archive; repeat installation to test
   idempotence; resolve all four internal children and run the installed durable
   registry's read-only `--validate` consumer. Record that these are file-copy
   consumers, not native host import, discovery, allocation or original authority.
7. Require a wrong-source/changed-commit strict refusal. This execution verified
   the new published archives from the original `4af2e43b` checkout: both
   verifiers refused with `inventory source binding`. The accepted earlier
   converse refusals remain intact and were not replayed.
8. Re-receive affected consumers and exact final package identities under the
   actual finite COMMON claim set. Do not claim final packages from provisional
   artifacts or use these checks to mint CE059.

## Existing-copy and scanner limits

Eight fresh new-artifact routes succeeded, including four child resolutions and
one registry validation per copy. All eight identical reinstalls preserved the
copy. Four canonical-plugin self-containment scans passed.

The additional standalone scan returned exit 1. Its completed traversal reported
seven generated inventory member declarations and zero runtime-file diagnostics.
Independent receiving confirmed all seven members' actual source/archive/install
bytes, modes and lengths. The source-layout scanner lexically scans inventory
metadata only when the standalone projection places it under `skills/`.
Its original invocation and failure remain unchanged. No full standalone scanner
PASS is claimed. If that exact predicate is included in final finite claims,
the entitled scanner owner must resolve it; no source correction is adopted here.

All three installer implementations correctly refused a new inventory over an
existing different `0.4.0` inventory. Complete predecessor snapshots remained
equal. No downgrade option bypasses this same-version rule. If final deployment
requires replacing an existing `0.4.0` copy, the source owner must select a
supported version/migration policy before the final build. Fresh during-swap
faults on the three implementations returned failure and removed the incomplete
target without staging/backup residue. These cases have no predecessor and do
not claim a newly tested different-version predecessor rollback.

## Truthful original-build bridge

The original `4af2e43b` archives installed successfully using their matching
original checkout in three isolated roots. Every non-inventory archive member
and mode equals the new published build. Inventory provenance and archive hashes
change because the source commits differ. This establishes a real narrow
original-build/helper route, consistent with existing documented contracts.

It does not satisfy strict verification from the adoption checkout. A complete
alternative bridge still requires actual finite consumer acceptance, truthful
original provenance and CE059. No such final bridge receipt is present. The
engineering payload additionally changes two shipped helpers, so published
archives cannot represent that full payload through metadata alone. Rejected
alternatives are relabeling, equal-tree-as-equal-commit, a new allow-either-source
rule and treating the narrow old-build route as final adoption acceptance.
