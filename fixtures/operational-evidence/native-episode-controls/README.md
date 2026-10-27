# Public native-source regression fixtures

These tests exercise generic source controls. They do not qualify a native
episode, provider, private selection, campaign, H0 lifecycle, or Q/E/JOIN.
All host metadata, public messages, IDs, route records and pending facts used
by the tests are synthetic fixtures. Native transport is mocked or refused
before launch. There are no model calls, native RPCs or configuration reads.

Keep the twelve `test_*.py` modules, `native_test_support.py`,
`run_native_source_regressions.py`, and `guard-golden.json` together. The
portable launcher takes an explicit repository root:

```sh
python3 -I -S -B path/to/run_native_source_regressions.py --repo-root .
```

It loads the actual public implementation from
`source-peers/native-runtime/skills/implementaudit/scripts/` and the actual
canonical route peer from
`source-peers/route-graph/skills/implementaudit/scripts/route-transaction.py`.
There is no installed-cache, private-profile, task-evidence, or `.inc.py`
fallback. A source-owner module with a private selection bound is refused.
The unbound-selection test assembles the complete canonical public closure
inside its owned temporary directory. A partial closure refuses; after the
last actual RT dependency is supplied, the complete unbound producer reports
FIXED_SELECTION_UNBOUND. Subprocess entry points are forbidden in that test.

`--list` verifies the unchanged 42-control baseline and prints all 74 registered
IDs: the original 42, four profile, three export, and 25 source-only controls, without running them.
Repeat `--case FULL_TEST_ID` to run focused adaptation checks.
`--scratch-parent DIRECTORY` optionally places all owned temporary fixtures
under a selected directory; otherwise Python's temporary directory is used.
The launcher checks that public source hashes remain unchanged during a run.

The original nineteen guard populations remain in:

| Module | Controls | Scope |
| --- | ---: | --- |
| test_native_probe.py | 6 | Bounded read allowlist and metadata/public projection |
| test_current_source_owner.py | 6 | Public-only records, version relation, physical range/revision and fixed-selection controls |
| test_review_repairs.py | 7 | Verified-byte loading, growth, aliases, parent custody and failure-complete cleanup |

The other 23 controls cover catalog/launch restrictions, unchanged original
R/A checks, original/prior/retry selectors, canonical task selection, frozen
source/cutoff/lifecycle/route/scope binding and pending-owner integration.
The R/A golden AST hashes exclude only the separately tested additive
occurrence sink. Updating these goldens requires review of the original checks.

Nine Windows handle/launch tests use explicit platform skips elsewhere. A
volume without a distinct short filename alias also skips that one alias
check. The directory minimum-access guard uses a mocked NT call to inspect
the actual relative-open arguments, including READ_ATTRIBUTES, DONT_REPARSE,
no directory SYNCHRONIZE and no delete sharing. It does not reread a private
WindowsApps package or claim that package's native permission qualification.
Windows launch tests use only a trusted system utility or an owned harmless
copy, discard its output, and never launch Codex. All other source/fixture
checks are portable.

The frozen export fixture includes `owner.canonical_route` and
`owner.host_and_scope`. Resealed foreign controller, receipt, transaction,
parent and malformed scope controls exercise internal checks. The R0038
consumer must additionally compare these values with its independently
captured canonical C03/R0035 route and scope; a coherent foreign tuple is not
authenticated by a self-contained structural validator.

Four additional current-profile controls exercise retained metadata through the
actual history parser, result/member/delivery validation, and exact raw-to-native
public binding. The selected runtime emits `final_answer` in both retained raw
records and the native item API; its generated schema's `final` spelling was
not used as evidence of live behavior. The bounded adapters preserve that
observed spelling without rewriting source bytes. Unknown metadata, foreign
turns, malformed provenance and copied delivery still refuse. The original
42-control identities and complete R/A guard golden remain unchanged.

Three export controls additionally preserve the pending owner's unresolved
signals, bind assigned/covered kinds and versions to the observation census,
and apply the original source ordering and nonoverlap predicates to every
selected occurrence. These controls do not establish producer authentication.

The adaptation return records 15 distinct focused checks against the integrated
successor source, including a recheck of the R/A golden after making its empty
AST metadata handling portable across Python versions. It does not repeat the
unchanged 42-control bank. The earlier
sealed source return remains unchanged. CI can run the full registered bank
through this launcher after ROOT integrates the fixture directory.

The 25 additive source-only controls preserve those earlier populations. Seven
exercise all three real pinned issuer-code readers with constructed modules: a
source above the old 128 KiB limit and the exact 256 KiB ceiling pass; ceiling+1,
wrong digest/length, replacement and FIFO refuse before evaluation. The finite
code-artifact allowance does not enlarge any native transcript/window bound.

Eighteen relation/causal controls distinguish the root creation version from a
fresh child's pinned running-provider version, and qualify the exact-header
causal rule for a child that activates/loads during its spawn RPC. Both spawn
reply and full LOAD result must precede parent acknowledgement. Legacy and
unqualified headers retain strict response-before-activation/LOAD ordering.
The tiny native-record fixtures use real record, artifact, identity and ordering
checks; only native provider authentication is substituted by an exact fixture
reader. Source-reader fixtures separately substitute outer native acceptance
gates. Neither set authenticates a host, real child, native occurrence or
acceptance. Current 64-record / 2 MiB windows, 256 KiB frames and HOLD/prefix bounds
remain unchanged; broader writer metadata/settings/equal-tick support is absent.
