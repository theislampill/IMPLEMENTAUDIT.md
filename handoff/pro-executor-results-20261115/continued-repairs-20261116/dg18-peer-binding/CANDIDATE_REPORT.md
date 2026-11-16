# DG18 peer binding correction

**Ready for distinct source review; ordinary repository binding scope only.**
The candidate fixes the stale current source manifest while preserving the
exact older owner required by the existing historical pending refusal fixture.
The two selected existing binding/materialization cases passed in one bounded
invocation. No pending-process suite, archive build, model, native operation,
source commit or publication was performed by this author.

## Exact candidate

Worktree: `/workspace/scratch/7fbb79f74aa4/recovery/dg18-peer-binding`.
Detached base: `75e7bc623dad7ec7e00e7ecd8b264ed1d26250f9`, tree
`e70d75bf81b2681c5750e10c188668cafc4736cf`.

| Changed path | Bytes | SHA256 |
| --- | ---: | --- |
| `source-peers/native-runtime/SOURCE_MANIFEST.json` | 24363 | `f63be8a73c83c40bd339685430d33e8d4577797e1b4bc17773744e4942315e4c` |
| `test-support/native-pending-history/compaction-source-owner-codex-app.py` | 185531 | `5bb21eed89945a8da97857f980b1f85a06dc07df47b25475b9173f23e82ce8f8` |
| `tests/cognition-pending-durability.py` | 54585 | `b823baab571a92139ebf2b06dcc1fdd393c9bb3ac966fd0e64edba10ef07deb0` |
| `tests/composite-source-cases.py` | 182070 | `3b7ea65fad97ec75d62812c1c5c7d47e208e6ac96db246ada28befd965136a2a` |

All four paths are mode 100644. The retained donor is byte-identical to existing
Git blob `21ff4e4caa1a05ec3c592ef84a062a23c2dfe0f8` from exact source
`205aeab7c93299b0666b261485ab5658d8e183de` (also present at a297).
It was copied from that immutable object after checking its size and SHA256.
It was not regenerated, normalized or relabeled.

## Behavior

The current manifest now binds the existing 196162-byte owner with SHA256
`83670fe9d57e4c52ef25982b8bf7baf2895d6133e5af3e103e2de46ed31e02d5`.
The row records actual public C02 source commit 4dad and the exact older
185531/5bb template preimage. Every earlier preimage and every other manifest
value is retained.

The portable fixture keeps `source_pins()`'s current-source meaning. A separate
explicit `refusal_source_pins()` selects the exact old donor for the existing
historical four-file refusal tuple. Its materializer still verifies the full
current manifest population against frozen Git and working bytes first. It
then copies the exact frozen historical donor into that constructed source
tree, verifies bytes/mode, records the verified current predecessor separately,
and lists the actual historical materialized member in `selected_files`.
Its scope expressly says historical pre-selection refusal and no native
admission. The top-level report retains both current and refusal source pins.

The existing composite case now names and selects the historical fixture. It
rejects the current owner as a substitute for the old closed tuple, checks the
physical historical materialization, and verifies that an altered donor is
refused without replacing the already materialized original. Existing
historical/mixed/missing-pin rejection controls remain in that same case.

## Verification and preservation

Exactly one command was run for source behavior:

```text
python -B tests/composite-source-cases.py CompositeSourceCases.test_documented_peer_materialization_supplies_exact_episode_owner_sibling CompositeSourceCases.test_historical_pending_fixture_profile_is_exact_and_still_refuses_native_reservation
```

Result: exit 0, two cases passed; unittest reported 0.192 seconds. Exact raw
stdout/stderr and timing are retained in this directory. This verifies source
binding and constructed data materialization, not a full pending-process or
native lifecycle. `git diff --check` and parsing of the two edited Python files
also passed.

AST comparison establishes that `source_pins()` and the complete 18-entry
`reservation_refusal_profile()` are unchanged. The live CLI source owner and
the canonical mechanical template gate are unchanged. Seven of the nine
published memory-correction paths remain byte-identical. The manifest is
extended only at this owner row. The composite file is extended only in the
one historical binding method; substituting its original method restores the
entire 75e7 file byte-for-byte. Thus the existing memory-specific tests and
reader dependency changes remain intact.

The whole change is outside the normal 75/72-member package projections.
The `skills`, plugin manifests, `package` and package builder inputs have no
delta from reviewed 75e7. No archive rebuild is needed for this successor;
that does not infer that an earlier memory-changed package already passed.

## Retained exact records

- `LINEAGE_FINDING.md`: 7508 B,
  `ae0d82b92de4dd9ea57738a2308de4a9ee602824ffb4105cf6a3ab9bdcc71b9a`.
- `CANDIDATE_FREEZE.json`: 6488 B,
  `37b6338cb2cb8d8aaa852ace888a521f7826d50eca41de983ce42885dd27d38b`.
- `SCOPED_SOURCE.diff`: 11087 B,
  `344e7de5e68411cb18372a725de597f2faa35efb9418de2b28a9799958970c2c`.
- `CANDIDATE.diff` including the exact retained donor: 199806 B,
  `820978d74f33e9b5325d1e8c9ff1792e21c19389892ab9058b597adb1cbdc73f`.
- `BINDING_REGRESSION_RESULT.json`: 977 B,
  `e715b53df047582065e38bec83bef0838e0fd7d47588db9af3a86f69967afa1e`.
- `BINDING_REGRESSION.stderr`: 496 B,
  `e6e678b6a90d66e90aff398e325d34e68466310b6229848117c692fc50c8255a`.

The first freeze-record generation stopped at an overly narrow bookkeeping
assertion that only the manifest could overlap the prior nine-path memory
publication; the already-authorized composite test is also one of those paths.
The final record explicitly accounts for both extensions and proves the
composite remainder unchanged. No source was altered or test repeated to
correct that record-generation assertion.

This candidate does not grant an original C5 profile, native launch, UNKNOWN
replay, source-owner selection, accepting result, retry or original14 award.
Root owns publication and any subsequent decisions. Rollback is discarding the
detached candidate; published 75e7 and all live state remain separate.
