# R0035 finite original audit-spec command

The repository helper `scripts/qualify-work-graph-finite-leaf.py` admits this
independent original command, `bash tests/audit-spec.test.sh`, under its default
`CONTROLLED_TASK_AUDIT_SPEC_V1` profile. The same owner also has an explicit
andon-class, registry-wrapper and marker-order contracts; no unknown future command or caller-supplied read set is
admitted. It reuses the existing compiler, acquired runtime,
isolated-leaf launcher and live-producer custody. It adds no executor, packaged
compiler API, native authority or canonical predecessor substitution.

Author execution controls have run the original positive, unchanged reuse and
two meaningful fixture negatives through the actual no-proc Bubblewrap image.
Non-authoring qualification and the qualifier's small integration remain separate
receiving gates. The earlier prefix24 proc-mount refusal remains open; this
profile does not require proc and gives no credit to prefix24.

## Exact source contract

The canonical registry remains the complete original 117-node population, pinned
to SHA-256
`77f26397b276fa1b6e494558d1796cb4c43d14b1e1a6755e68f542cdc4c37698`.
The compiler derives the mapping and command bytes; this helper selects only
original index 57, `COMMAND:tests/audit-spec.test.sh:0`. Its source is exactly
`bash tests/audit-spec.test.sh` followed by a newline. The other 116 nodes are
explicitly omitted. The original test and registry are unchanged.

The original test sets its own shell flags and root, calls one validator on a
valid fixture, then calls it on five named invalid fixtures. The validator reads
only the explicit fixture, lowercases it into one temporary file, checks fixed
patterns, prints the result and removes that file on exit. There are no source
imports, directory enumerations, Git operations, proc reads or whole-source
copies in this pinned command closure.

The acquirer reads exactly these nine candidate files:

| Role | File |
|---|---|
| Selection owner, not mounted as subject data | `scripts/verify-package.sh` |
| Pinned original test | `tests/audit-spec.test.sh` |
| Pinned validator | `skills/implementaudit/scripts/validate-audit-spec.sh` |
| Valid fixture | `fixtures/audit-spec/valid-mixed.md` |
| Invalid fixture | `fixtures/audit-spec/invalid-missing-owner.md` |
| Invalid fixture | `fixtures/audit-spec/invalid-missing-rollback.md` |
| Invalid fixture | `fixtures/audit-spec/invalid-missing-evidence.md` |
| Invalid fixture | `fixtures/audit-spec/invalid-missing-generated-plan.md` |
| Invalid fixture | `fixtures/audit-spec/invalid-missing-release-boundary.md` |

The test SHA-256 is
`eef97a07f531e002a752264848d38697a636041b574385828a9b364fe20bcee3`;
the validator SHA-256 is
`f0b88b4b2d2745eb2df1f339b5daaa1bf7d20a148b4ecccb3de7d9c0de0074d7`.
Changed executable or registry bytes refuse admission. Fixture bytes are acquired
as data and reach the actual validator. All six fixtures must exist: accepting a
missing invalid fixture could make an expected-failure branch pass for a different
reason. Extra candidate files are not mounted because this exact command has no
path to read or enumerate them.

Every literal ancestor is opened without following symlinks. Files must be
ordinary, single-link files with mode `0644` or `0755` and no extended metadata. Each
file is bounded at 64 KiB and their aggregate at 256 KiB. File bytes/modes, ancestor
modes and exact physical identity stamps are checked again after runtime
acquisition. The runtime image normalizes subject files to read-only `0444` and
directories to `0755`; the acquired source records retain the original modes.

## Existing runtime and execution owners

The prefix helper is loaded from one captured buffer only after matching its
reviewed whole-file SHA-256
`86f4e02dbf7b25ee3a4dab2fb90ef4dd3e21cfe350e8ce38470e36c4f4733016`.
Its bounded reads, runtime acquirer, sealed objects, private evidence custody,
engine checks and session lock are reused. The new helper and all other engine
files are themselves captured, retained and checked against the live loaded
engine identity. A changed prefix helper needs a newly reviewed exact contract;
the loader does not execute unknown bytes.

Execution calls the qualifier's existing `VerifierTaskSession._execute`, which
uses `run-work-graph-verifier.sh --isolated-leaf`. That runner closes retained
input descriptors, verifies the command digest and executes the exact source.
The acquired scope is used in its receipt. Prefix23's whole-group receipt is
never relabeled as this profile.

The image uses the existing fixed environment, Python bootstrap/runtime, captured
Unix tools/libraries, sealed memfds, seccomp restrictions and private namespaces.
Its captured generated Python wrappers set `umask 022` before the isolated-leaf
bootstrap and original command. This is an explicit closed startup profile;
it does not claim correspondence under arbitrary observer masks. The observer's
process-global mask is not changed. An actual component control launched with
mask `077` observes `0077` under the previous wrapper and `0022` under the fixed
wrapper. The control uses a separately labeled synthetic command and earns no
original-node execution credit.
It mounts no host root or proc. The eight subject files are read-only; only the
existing bounded private `/tmp`, null device and observer output streams are
writable. The validator uses one bounded temporary file at a time. Admission
derives its scratch reservation from the largest acquired fixture, rounded in
64 KiB allocation units plus one unit of file overhead, and checks that it fits
the unchanged inherited 32 MiB temporary filesystem.

## Live consumption

`bind_session(VerifierTaskSession, compiler, engine_root, captured_helper_bytes)`
returns the fixed session class for the qualifier integration. A session accepts
only `run()`; callers cannot supply an execution receipt, claimed exit, command,
profile, environment or reuse plan. A new process cannot consume an inherited
live session.

The internal factory may explicitly choose one of the four known profiles; the
run-only receiving interface cannot supply a profile or executable policy.

Every consumption acquires current source/runtime/observer facts, retains the
exact graph and selected scope, and either executes or consumes the same live
producer's issued result. It reacquires after the execution or reuse and checks
all retained output, receipt and input bytes/modes. The profile has separate
issued-result keys. Source/runtime/engine drift, expiry, missing input objects,
altered output, concurrent consumption and interrupted or failed execution
refuse reuse. No private temporary artifact or shell state is passed to another
canonical node. The original serial verifier remains available.

## Verification commands and evidence boundary

Small source/admission controls:

```bash
/usr/bin/python3 -B tests/work-graph-audit-spec-cases.py -v
```

Actual original-command controls require a host where the established no-proc
namespace launcher is supported:

```bash
R0035_AUDIT_SPEC_LIVE=1 /usr/bin/python3 -B \
  tests/work-graph-audit-spec-cases.py LiveCases -v
```

An optional fresh `R0035_AUDIT_SPEC_EVIDENCE` path retains each completed case's
original source projection, acquisitions, raw child streams, integer exits,
dispatches, receipts and source digests. Input objects are deduplicated only
after the live case ends. `R0035_AUDIT_SPEC_OBJECTS` can select an existing exact
content-addressed retention pool for a later run; it never supplies runtime or
source bytes to a live session. Retained paths are historical evidence and cannot
be imported as live producer authority.

The real positive emits the original validator's valid-fixture message and the
original test's success message. An unchanged second consumption returns the
same receipt without another dispatch. Changing the valid fixture afterward
refuses the stale result. An actual fork of the producing process also refuses
before acquisition. Separate real controls show that removing both owner phrase
occurrences from the valid fixture produces the validator's missing-owner exit 1,
and replacing an invalid fixture with valid contents produces the test's own
unexpected-valid exit 1. Output tampering and removal of an acquired input object
refuse without redispatch.

The first missing-owner control removed only the heading; the same phrase remained
in the fixture's constraints paragraph, so the original validator correctly
returned 0 and the author test failed. That failure and actual output/exit remain
retained. The corrected mutation removes both matching phrases and passed its
targeted rerun. This correction changes only the private test fixture mutation;
the helper, original test, validator and acceptance predicate are unchanged.

After moving the unpublished helper into the common finite-leaf owner and adding
the fixed startup mask, all nine admission controls and all four actual-command
controls were rerun against that exact shared source. The 13 tests passed under
an observer process launched with mask `077`. The historical helper, tests,
documentation and failed attempts remain preserved separately; earlier executions
are not relabeled as evidence for the changed shared helper.

The later extension for original nodes 113 and 45 preserves that two-profile
packet. Its final shared source received a new audit-spec run of all nine
admission controls and the actual positive/reuse, stale-input and foreign-process
control. Those ten tests passed. The earlier semantic-negative and corruption
results keep their original source identity; they are not relabeled as new runs.

These are author observations for an independent original command. They do not
establish the 117-node canonical chain, predecessor/successor effect transfer,
accepted JOIN, native currentness/scheduling, installed product loading or issue
closure. The prior qualified union remains 24/117 pending independent review of
this new finite result; accepting original node 57 would add one distinct node,
giving 25/117 and leaving 92. Prefix24 remains unqualified by this result.

The new helper, tests and maintenance note are repository-only and add no package
payload members. No cap, reserve, compressor, compatibility source profile or
packaged API is changed. Final integrated package provenance and acceptance are
separate receiving checks.
