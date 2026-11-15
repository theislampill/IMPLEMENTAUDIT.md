# DG17 source qualification return — 2026-11-15

Status: **the first source-only CI run is received with both jobs failed. Linux
Stage A steps 01–10 reached the explicit native boundary; the full fixture and
Windows rebuild remain unqualified. A focused harness correction and unchanged
Windows refusal with diagnostic facts await independent review and source CI**.
This record grants no native admission, receiving, R0037 acceptance or closure.

## Binding and scope

- Executor: bounded source engineer under PRO-EXECUTOR-01.
- Input branch: engineering/dg16-dg18-findings-20261115.
- Input commit: e4cba42cb5704f00b78d64e43f5da88501c28229.
- Input tree: 7dd2b0b3921eb764669eaad98a9f0fd94f873c84.
- Binding texts: original R0037 issue #211; PRO_UNIFIED_COMMISSION.md and
  RETROSPECTIVE_20261115.md at the input commit.
- Changed surface: campaign generator, its generated successor carriers,
  source-only tests and one narrowly scoped source CI workflow. No packaged
  runtime file is changed by this return.
- The historical author sets and historical 13/13 Windows receipt are unchanged.
  Generated successor files are written to a fresh explicit output directory.

## Preserved baseline and corrections

| Finding | Actual baseline | Correction and local evidence |
|---|---|---|
| Published rebuild path | Running the published builder fails with FileNotFoundError for dg17-next/release/author, absent from the published tree | The generator resolves the published dg17-next-release/author, accepts explicit source/output paths, and parses Windows paths correctly on POSIX |
| Incomplete B2 pin forwarding | Operation and constructor name the old binding owner 8b4f91a5 and handler b42fbbc2; current source is 2e784dbb and e180069d | Rebind operation readset, explicit owner, source closure, constructor literals, five skill pins, and dependent launch/binder pins. Each runtime source is compared with selected HEAD before generation |
| Stale Stage A state | write_state called with e4cba42 still emits b0fcb565 in Baseline ref | Generated driver uses its supplied head. Focused state-output control passes |
| Windows DACL scope mismatch | Modeled Win32 descriptors show the published guard admits an Administrators ACE | Generated guard admits only user and SYSTEM, matching the commission. The historical behavior is retained as a counterexample. Real Windows test expectation is explicitly revised, with the old 13/13 record preserved |
| Parent A command overflow | The 24,895-byte published driver produces a 33,777-character Windows command in the reproduction, against its own strict 30,000 bound | Generated parent uses the unchanged capture function inside the child, checks the exact driver digest, and executes the captured buffer. Its measured command is 1,897 characters at this local output path. The size check now precedes the episode-window write |

The parent A correction preserves the physical identity, regular-file,
reparse/link, size, before/open/after identity and exact-digest checks. No
unverified file is executed. It follows the capture architecture already used
by parent B; it does not enlarge the command or timing limits.

## Tests actually run here

| Check | Observed result |
|---|---|
| git diff --check | PASS |
| bash tests/host-session-binding.test.sh | PASS: 15/15 R003A plus 14/14 R0035 custody cases |
| bash tests/host-session-binding-hardening.test.sh | PASS: 27 tests |
| bash tests/host-session-terminal.test.sh | PASS: 23 tests; one platform-specific skip |
| tools/test_driver_bundle.py | PASS: 15 test methods, including ten modeled adversarial DACL descriptors, historical Admins acceptance vs successor refusal, pin closure, path alias/hardlink rejection, command size, source-state identity, capture substitution refusal and original receipt deadlines |
| Canonical package build with exact zopfli 0.2.3.post1 | PASS against clean e4cba42 source |
| Existing package owner verify-artifact, canonical_plugin, require-clean-source | PASS against a clean local clone of e4cba42 |
| Real Stage A main on this Linux host | Steps 01–05 pass; step 06-new-claim refuses the host interpreter profile |
| Real Windows ACL controls | NOT RUN on this Linux host |
| Full Stage A/B fixture lifecycle | NOT QUALIFIED locally: blocked by the same exact Stage A interpreter gate |

The initial package attempt lacked the exact zopfli dependency. It was installed
only under the task-owned evidence directory. A later package attempt detected
test-generated __pycache__ files; only those task-produced files were removed,
then the clean build passed. These setup failures are not runtime defects.

The first Stage A rehearsal found that a partially hydrated Git clone could not
supply all objects to the source clone. Hydrating the exact source commit fixed
that setup failure. The later step-06 refusal is preserved: this host executes
as uid 1000, and its physical Python binaries are owned by uid 65534. The source
owner requires a root-owned POSIX interpreter and root-owned, non-writable
ancestors. No ownership fact, helper, source predicate or system installation
was altered to pass that gate. Supplying an absolute interpreter path did not
change the refusal.

The modeled Win32 tests exercise Python refusal logic with fake API descriptors.
They are not Windows API execution, ACL parity or evidence about 3701MEDIA.

## Exact local package and rebuilt record

The build source is e4cba42cb5704f00b78d64e43f5da88501c28229.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| IMPLEMENTAUDIT.plugin.zip | 588580 | a5fb101f28da2477cd071985a93ffe1036acc90bcbea66bb79e64a6ff157ba3d |
| IMPLEMENTAUDIT.skill | 583968 | e9d03cce8585165e244512091ff82ba4e8103e91852a50e8d9b8e802eb510d45 |
| Source-only OPERATION_A.json | 19483 | c497826f6b3b803390b344a1df40e8eccb6d0a6a7544ca3b2e119380ed6edca4 |

Canonical usable limit is unchanged at 588584 bytes; this build has 4 bytes
remaining. The commission's 588581-byte measurement belongs to its earlier
source identity and is not overwritten.

Local rebuilt author directory:
.IMPLEMENTAUDIT/dg17-offline-20261115/final-reviewed/author

The operation is explicitly INERT_SOURCE_REBUILD_NO_NATIVE_ADMISSION. Eight
Windows inputs remain unobserved: the historical owner carrier, native binary,
Python, Bash, Git, signature carrier, restore carrier and isolated-home config.
Historical issuer/carrier values are retained as unresolved inputs, never
presented as a fresh grant. This is a source-only rebuild at its actual local
path, not a grant-ready operation at 3701MEDIA's final Windows path.

To generate a fresh candidate at a real final path, use the source generator:

    python -B tools/build_release_acl.py --source-root <clean-selected-source> --output-author <new-final-author-directory> --package <exact-canonical-plugin.zip>

The package option invokes the existing package owner for full population,
identity, budget and parity validation. Without a supplied package, that input
remains explicitly unresolved. Existing output paths and manifests are refused.
The builder never creates a home, case, native process, grant or reviewer result.

## Scoped CI candidate

.github/workflows/dg17-offline-lifecycle.yml triggers only on a push to
engineering/pro-executor-dg17-source-20261115. It uses contents:read, does not
persist checkout credentials, pins checkout/upload actions, and has 15-minute
Linux and 10-minute Windows job bounds. No native episode is launched.

Linux runs the real driver entry points with three explicit fixture modes:
native-boundary, full and blocked-hook. The native transport is a subclass that
does not create a process. An additional process allowlist permits only the
exact Python, Bash and Git used by the deterministic source owners and refuses
Codex/app-server invocation. Each fixture directory declares SIMULATED_ONLY.
The harness retains real source-command results, exercises the actual B
formatter, binding CLI, receipt consumer and teardown where the host allows
them, and separately labels the synthetic transport/permission/reviewer inputs.
A first non-PASS hook case must interrupt, disable the fixture hook and tombstone
the fixture binding. No fixture result can be received as native evidence.

Windows runs only the driver-side private-directory tests in RUNNER_TEMP.
There are 14 planned cases, including the new strict Administrators refusal and
an actual wrong-owner setup. Failure to establish the wrong-owner fixture is a
test failure, not a reported pass or silent skip. This tests the proposed
source on a hosted Windows runner, not the owner machine or native Codex Stop.

CI receipts were pending at the initial author return. The following additive
record preserves the actual first published outcome and the followup scope.

## First published source CI — run 43675846002

The published source commit is
52065bcee405715a2fc31d78b3aefd2958ba96a0, tree
7da9f4e0d40e8dfb32d5dcf78df46b4e70c31f14, on the exact guarded branch above.
The local reviewed-source base 5a6825c73de82d7ba45d584527da882310f20a62 has
the same tree. This identity is distinct from the earlier e4cba42 local build.

Both jobs failed and both artifact uploads succeeded. Artifact metadata was
received before the body, and the received body size and SHA-256 matched it.
Each artifact had one bounded body GET through the platform transport. Signed
URLs, raw materialization wrappers and archive bodies were not retained; only
bounded source logs, result/marker JSON, PINS and safe metadata/receipts were
retained under .IMPLEMENTAUDIT/dg17-ci-43675846002. These are source artifacts,
not a protected acquisition or native episode.

| Job / artifact | Actual outcome | Artifact bytes | Artifact SHA-256 |
|---|---|---:|---|
| Linux job 132695703877; artifact 14146507079, dg17-linux-source-only | FAILED; upload succeeded | 6315 | 1898209fe489e8c726f1551ebb57974a2b1dabee2c99b1264ad9fd479d17177f |
| Windows job 132695704092; artifact 14145752673, dg17-windows-store-source-only | FAILED; upload succeeded | 474 | 0dae263a22520d082f295e4aed4e46aa9ea0841d24f2a4d269de59ab1e83c449 |

### Linux observations and first refusal

The original 15 source-control methods passed on the runner. In the separate
native-boundary fixture, the real source owners completed clone, selected
checkout, HEAD/tree verification, controller-absence check, claim, initialization
inspection, activation, resume, receipt verification, currentness and the
positive validator. Its exact result is
SOURCE_STEPS_01_TO_10_PASS_NATIVE_BOUNDARY_NOT_CROSSED, with elapsed time
6.317373794 seconds. The driver records
STAGE_A_STOPPED_FIRST_REFUSAL_OR_UNKNOWN_NO_RETRY because the explicit fixture
Client raises before native appserver creation. There were zero genuine turns
and zero native appservers. The result is 1212 bytes, SHA-256
fa29f86df2cc923a998ee54949c39ea00875b9569f46c3e973997b1dbfb40167.

In the full fixture, Stage A reached
STAGE_A_BOUND_CONTEXT_READY_FOR_INDEPENDENT_REVIEW with
892.083397502 seconds remaining. All native traffic in that fixture was
simulated. The real B formatter emitted a 6566-byte fixture operation with
SHA-256 7540dd1e20e32fb151a79b106d87032e937642a443ad6c045b7505d8326af736
and issuer SIMULATED-NO-AUTHORITY. Stage B completed its currentness and owned
store initialization. Before spawning 03-owned-bind, the harness rejected the
ordinary binding data argument in `--host-id codex` as though it named an
executable. The same guard prevented cleanup lookup; the final traceback is
`Teardown unknown; parent reconciliation required`. The full lifecycle and
cleanup are failed, not qualified. The blocked-hook fixture was not reached.
The original full.log is 3307 bytes, SHA-256
55b2aad658a20e44e0b5623775e41cc12c2d2d031d3c39f9e458b88504626298.

The received rebuilt/PINS.json binds the published source HEAD/tree above and
the following generated source carriers. These are actual Linux-runner path
bindings, with no supplied package and nine explicitly unresolved inputs.

| Generated carrier | Bytes | SHA-256 |
|---|---:|---|
| OPERATION_A.json | 18684 | 43e1428c469a8919aead08ce530c64b8c94b82addeb4ce8904bae3ede2546d43 |
| stage_a.py | 24857 | 683c1e0693eeebfd94b39239baa8896b045aeb2e57663876b8e349efe6d5978b |
| stage_b.py | 33468 | 590a92cc09b835a4a50af8e40364cd6337fecc7d0fbbb08b956fdd4c335e0dd1 |
| parent_launch_a.py | 6069 | 7a068cbb4309dd7539dd7f3d2538549cdd521745cce983b467a0019d3a599176 |
| parent_launch_b.py | 5054 | 88ed30567c877614fa24d3fad8cd9ebdc2d5d1a90eecc23beae80b6233cbd0f7 |
| bind_stage_b.py | 3244 | 2f0a37e9611ee7d88229311f522665f506c80d9dce87ae636e90a07ed74d1731 |
| positive_hook_constructor.py | 10996 | 028fc1c7290fdcb461da7cb9a87e1c3e16a4de1c1717b4563987c8eb0019f2d3 |

PINS.json itself is 3935 bytes, SHA-256
c78f6332e614ba9d4ed3f4ea4ca96eb05f7758e21153782d439a25bf1a2706d1.
Its authority is NONE, native_admission is false, limits are unchanged and all
14 custody differences remain UNKNOWN. A source rebuild is not a fresh grant.

### Windows first refusal and diagnostic boundary

The Windows job stopped inside build_release_acl.pin while comparing the
source file's before-open lstat identity with its opened fstat identity:
`ValueError: Input identity changed before read`. It produced no generated PINS
and never reached the real Windows private-store controls. The artifact's only
member is rebuild.log, 1087 bytes, SHA-256
2feea6bbab976b5496a41e59353add154ddb82cee7cd73054bca4a4eb750723f.

That log contains neither identity tuple nor Python version. Which field
differs, and why it differs on that runner, remain unknown. The followup keeps
the exact seven-field comparison: st_dev, st_ino, st_mode, st_nlink, st_size,
st_mtime_ns and st_ctime_ns. On this same refusal it now reports only those
before/open numeric facts, the differing field names and Python version. It
does not log input paths or file contents in the diagnostic. No tuple field,
ownership check, DACL requirement or after-read check is relaxed. A separately
reviewed source-only run must receive these facts before proposing a Windows
identity correction. No Windows ACL or owner-machine parity is claimed.

### Followup source change and focused verification

The Linux harness now distinguishes the resolved executable from protocol data.
It still admits only the exact selected Python, Bash and Git, refuses a literal
app-server invocation, and limits Bash entrypoints to the actual deterministic
claim-run.sh and validate-run-root.sh owners. Direct native executable, string
command, shell=True, Bash -c/-lc and foreign Bash script controls are rejected;
the Python binding argument `--host-id codex` is admitted. No model transport
implementation changes; the native Client remains the process-free fixture.

The harness also writes a bounded failed REHEARSAL_RESULT.json before reraising
the original exception. It retains first source-command failures and stage
errors when a final cleanup exception would otherwise hide them. The existing
workflow already uploads that result file; its trigger, job permissions,
actions, timeouts and artifact selection are unchanged.

The local focused command is:

    PYTHONDONTWRITEBYTECODE=1 python3 handoff/dg16-dg18-findings-20261115/dg17-release-with-store-check/tools/test_driver_bundle.py

All 18 methods passed after the correction. The three additional methods cover
executable/data classification with seven negative cases, each of the seven
unchanged identity-field refusals with bounded diagnostics, and first-predicate
preservation with explicit authority NONE. git diff --check passed. These local
checks do not resolve the previously recorded HOST_OUT_OF_PROFILE interpreter
refusal and do not establish a complete hosted lifecycle or Windows outcome.

Independent review of this exact followup is pending. The author does not
award approval, dispatch another workflow run, retry a protected episode or
alter a grant. A root publication after review may run only the same bounded
source-only controls. Earlier failed source runs remain failed evidence.

## Remaining acceptance dependencies

1. Successful complete deterministic CI/source receiving at the exact published
   source candidate, with any failed fixture or host outcome preserved.
2. Actual final Windows location, exact product/package/tool identities, current
   issuer reconciliation and independently reviewed operation-record readback.
3. Fresh written owner grant naming that exact operation, unchanged limits and
   two genuine Codex model turns: one A observation and one B qualification.
4. Independent post-A receiving, POST_B, T12 and original14 receiving, followed
   by custodian certification.
5. All 14 custody differences remain UNKNOWN. This source work neither resolves
   them nor authorizes replay.

AGENTS_UPDATE_DECISION: no instruction change; focused generator and behavioral
controls address these campaign-specific defects.

CONTINUITY_DECISION: retain this source report, exact manifest, historical
failures and source-only artifacts. No native continuity or acceptance record
is synthesized.
