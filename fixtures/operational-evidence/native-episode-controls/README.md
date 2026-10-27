# Public native-source regression fixtures

These tests exercise generic source controls. They do not qualify a native
episode, provider, private selection, campaign, H0 lifecycle, or Q/E/JOIN.
All host metadata, public messages, IDs, route records and pending facts used
by the tests are synthetic fixtures. Native transport is mocked or refused
before launch. There are no model calls, native RPCs or configuration reads.

Keep all `test_*.py` modules, `native_test_support.py`,
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

`--list` verifies the unchanged 42-control baseline and prints the registered
IDs without running them. Original 42, four profile, three export, and the
25 source-only controls retain separate exact populations; acquisition and
startup controls are registered as additional groups.
The current total is 99: 42 + 4 + 3 + 25 + 12 acquisition + 13 startup/binding.
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
acceptance. Those 25 controls did not change transcript acquisition or startup
envelope grammar. The separately versioned acquisition controls below qualify
that later source policy.

## Physical acquisition policy v1

`codex-nonprotected-acquisition-v1` is a fixed policy in the existing observation
owner. Its constants and source digest are bound by the existing fixed policy P;
there are no caller-supplied resource limits or new receipt formats. Complete
physical acquisition and selected-evidence resolution have separate budgets.

| Domain | Scope | Bound |
| --- | --- | --- |
| Selected evidence (`read_records`) | All existing selected readers | 64 records, 2 MiB total, 256 KiB per record; unchanged |
| Complete physical turn interval | Exact nonprotected profile | 4,096 records, 16 MiB total, 2 MiB per frame |
| Complete source-prefix hash | Exact nonprotected profile | 128 MiB, streamed in at most 64 KiB blocks |
| Fresh-child HOLD history | Nonprotected profile, history starts at ordinal 1, no `historical_prefix` key | 512 records; existing 2 MiB prefix and 256 KiB frame bounds |
| Other complete-turn/prefix contexts | Including owned-stdio and unsupported profiles | Existing 64-record / 2 MiB / 256 KiB bounds |
| Other HOLD contexts | Including inherited history and a present null historical prefix | Existing 64 parsed-record bound |

The source-prefix ceiling matches the existing registered-source budget. Whole
turn acquisition can include large unselected host frames; admitting that
physical interval never selects those frames as evidence. Fresh HOLD still
reads every required physical row and checks contiguous ranges, ordinals,
metadata, prefix hashes, original calls and physical identity. The complete-turn
reader also checks the opened file and pathname after reading, so replacing the
source before open or during acquisition refuses.
The interval runs from the bound turn/activation anchor to the selected public
pin. A later message turn does not reset its budget or rewrite that anchor.
For inherited histories, the count bounds the parsed retained portion; the
earlier physical prefix is still fully hashed. A prior occurrence or retry is
not automatically a different policy class: the literal scope predicate controls.

Twelve source-only controls cover at-limit and over-limit cases, old-profile
fallbacks, malformed frames, replacement races, exact bounded prefix hashing,
and a prohibited USE beyond row 64. They use owned synthetic files. A larger
acquisition budget supplies no native occurrence, settings authentication,
acceptance, Q/E/JOIN, consumption or mainline authority. Historical policies,
source identities and refusals remain exact; this policy does not convert an
old refusal into an old success.

## Qualified startup records and same-source clock ticks

Thirteen additional controls exercise the existing full history consumer with
owned synthetic files. Eligibility for the new grammar comes from the complete
checked header: the exact nonprotected profile and boundary association, a fresh
history without an inherited prefix, CLI writer `0.164.0-alpha.11.1`, and the
actual child/parent relation. No caller-supplied eligibility flag is acquired.

- A selected `child_initial_settings_sha256` is validated by the existing source
  owner, copied into its derived context, and included in fixed P's exact host
  tuple. Only the exact child settings payload before LOAD is admitted. When
  that qualified branch has a selected baseline, exactly one matching event
  must occur; absent, duplicated, late or changed settings refuse. The baseline
  must be selected prospectively, not repinned to make an observed child pass.
- A bounded, closed developer `additional_tools` envelope before LOAD is inert
  data. Strict Boolean provenance rejects numeric zero. Declaring a tool never
  authorizes an actual forbidden call or early USE.
- Only the existing three transport call/output kinds gain the exact
  `client_authored:false` and nonnegative integer `user_input_order` metadata
  shape at that qualified history caller. Assistant retained-message grammar,
  operation allowlists and call/result identity checks remain unchanged.
- Equal timestamps are admitted only for adjacent records in the same complete
  checked physical history. Ordinals, physical lines and byte offsets must all
  be consecutive. The old owned-stdio case is preserved; `before()` remains
  strict, including at cross-source boundaries.

The combined history positive checks complete prefix bytes/hash and original
LOAD, EXCHANGE and pending BIND occurrences. Negatives cover the new grammar's
identity, provenance, order and effect boundaries. The selection/policy control
uses real pinned selection and code reads with live-provider acquisition
substituted; it proves no host authentication. Context derivation remains part
of the exact source review. Original result and separate acceptance checks are
unchanged, and these fixtures provide no original native acceptance or JOIN.
