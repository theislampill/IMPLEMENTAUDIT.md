# DG17 source qualification return — 2026-11-15

Status: **the fourth source-only CI run passed the three Linux modes and
demonstrated successful direct .NET owner readback on Windows. Ten Windows
fixtures then stopped at an unwanted Administrators grant in their private
baseline. A one-command fixture correction awaits distinct review and Windows
verification. All failed runs remain recorded; no product guard is changed**.
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

At this followup's author return, independent review was pending. The author
did not award approval, dispatch another workflow run, retry a protected episode
or alter a grant. The subsequent reviewed root publication is recorded below.
Earlier failed source runs remain failed evidence.

## Second published source CI — run 43677179224

The preceding harness correction received a distinct source review, which root
retained in local commit 06b22dcfa07cbfed8fc69d922530d05d544d0aef. Root published
the same tree, b81b8b30065b6620a5eaff9a21bb087825b217fa, as commit
0d262630b826ecf634a44e3b8b9535b46a6dc14c on the guarded engineering branch.
Run 43677179224, attempt 1, began at 2026-11-15T04:32:02Z and reached completed
status at 04:32:38Z. Its overall conclusion is failure: Linux succeeded and
Windows failed. Both artifact uploads succeeded.

| Job / received artifact | Result | Artifact bytes | Artifact SHA-256 |
|---|---|---:|---|
| Linux 132699780574 / 14147060553, dg17-linux-source-only | SUCCESS | 10711 | 1be8f2027ede5fbe02c54b53e09fd4b6082d6c5e8f955a02df1a859eb95a8195 |
| Windows 132699780775 / 14147315042, dg17-windows-store-source-only | FAILURE | 2906 | 7d56e96fd6d46dd0224dd95e4e1f46b612a75982d5566c37131b7c6834e3fc29 |

Each artifact was received in one bounded body GET after metadata, with exact
size and digest agreement. Only source members and safe receiving metadata were
retained under .IMPLEMENTAUDIT/dg17-ci-43677179224. No signed URL, raw download
wrapper, archive body or protected/native replay was retained or performed.

### Linux modes actually completed

| Mode | Actual result | Elapsed seconds | Result JSON SHA-256 |
|---|---|---:|---|
| native-boundary | SOURCE_STEPS_01_TO_10_PASS_NATIVE_BOUNDARY_NOT_CROSSED | 5.888422223 | c4d631d4ecfa6a0e29fd65e05306b833c2807976ac306844946f11dadac43060 |
| full | DETERMINISTIC_LIFECYCLE_PASS_WITH_SIMULATED_NATIVE_SEAMS | 9.442584381 | bea8729a35e1b6b7cebe03a6707d9c7c6fb6617c3deb78e04863116902d028d8 |
| blocked-hook | FIRST_NONPASS_CONTAINED_AND_CLEANED_UP | 9.428914913 | 5d281fc5259e8987eb1ddcdf11095439dcac9f7924b4d969b603196fe975edc8 |

The full and blocked-hook fixtures completed Stage A source steps through 17
and Stage B source steps 01–08. Both report teardown_known_in_simulation true;
the fixture assertions require hook disablement and binding tombstone readback.
The full fixture consumed the selected synthetic receipt. The blocked-hook
fixture observed the non-PASS condition, requested its simulated interrupt,
disabled its hook and withdrew its binding. Its expected caught AssertionError
is retained alongside FIRST_EVENT_OR_LATE_EXTRA_ACTIVITY_NOT_QUALIFYING.

These are deterministic source producer/consumer and cleanup results. Native
RPC/model traffic, grants and reviewer inputs remain explicitly simulated, and
the Windows custody seam remains replaced by a private POSIX fixture. Every
result records authority NONE, zero genuine Codex turns, zero native appservers
and all 14 custody differences UNKNOWN. No native acceptance follows from the
driver's native-shaped status vocabulary inside these fixtures. The earlier
failed full fixture is not regraded.

### Actual rebuilt source identities on both runners

Both received PINS records bind source HEAD 0d262630b826ecf634a44e3b8b9535b46a6dc14c
and tree b81b8b30065b6620a5eaff9a21bb087825b217fa. Both retain nine unresolved
inputs, unchanged limits and native_admission false. The manifest retains every
generated member digest from each PINS record.

| Carrier | Bytes | Linux SHA-256 | Windows SHA-256 |
|---|---:|---|---|
| OPERATION_A.json | 18684 Linux; 18437 Windows | 415c81735f9e143f72510b622fb6a5c17e5f4ea98baa87428276da63c62e2f39 | e3521bd303069bc5d6d31704cab8b4f3cf808390f5addd36c0c47018f46603de |
| stage_a.py | 24857 | 683c1e0693eeebfd94b39239baa8896b045aeb2e57663876b8e349efe6d5978b | 683c1e0693eeebfd94b39239baa8896b045aeb2e57663876b8e349efe6d5978b |
| stage_b.py | 33468 | 590a92cc09b835a4a50af8e40364cd6337fecc7d0fbbb08b956fdd4c335e0dd1 | 590a92cc09b835a4a50af8e40364cd6337fecc7d0fbbb08b956fdd4c335e0dd1 |
| parent_launch_a.py | 6069 | 32ef6d3179c8d7e2010682874c5647784bd90dbd01cd3bd2ac44f409a818bf43 | 2923541af52db739faae45576f9026fac655bbed1773df40253a895cc1c69e75 |
| bind_stage_b.py | 3244 | d212f5a9641c0560bbad5d65c4c2a9f6359011c02967c7f3d547b57b4d2ed202 | f22dc3474953bc383944a2b8faeaf76ef423c89b15134654634300f79dc1087f |

The Linux PINS.json is 3935 bytes, SHA-256
c8f18b44f59794e391b7d6f9cb15504d0422aa0857bda20a4b95ef64651651a0;
Windows PINS.json is 3851 bytes, SHA-256
149e0f7146073890790368d8d00bd7ef426aa0925afb61f4cb20faf19c42254c.
Their path-bound operation and dependent launcher/binder hashes differ as
expected for their different final locations. Neither is a fresh native grant.

### Windows first failure and intercepted negative cases

The unchanged seven-field file-identity guard passed this rebuild. It emitted
no mismatch diagnostic. This is a no-mismatch observation on this run; it does
not explain, repair or erase the previous run's identity refusal. No identity
field or custody/TOCTOU predicate was changed.

The actual Windows test output reports CASES 14 FAILED 1. Driver-created store
creation and re-check passed with the current token user as owner and only
user+SYSTEM access entries. The icacls-created positive failed: its observed
owner was BUILTIN Administrators (S-1-5-32-544), whereas the driver requires the
current token user. The source factory called mkdir and set a DACL but never
established or independently verified the owner.

Seven nominal negative successes were intercepted by that same wrong-owner
predicate and do not qualify their intended controls:

- Administrators access entry outside the permitted principal set.
- Everyone write access entry.
- Everyone read-only access entry.
- Inherited Users write access.
- Inherited Users write access under the otherwise private parent.
- Junction to a private directory; its target failed before the link was tested.
- Unprotected DACL inheriting only user+SYSTEM.

The missing-directory, existing-path create and regular-file cases reached
their named refusal predicates. The separate wrong-owner case reached the
owner refusal, but lacked a verified positive preimage before its owner change.
The reported 13 nominal matches are not a claim of 13 independently qualified
controls. The exact original output remains unchanged: store-custody.log is
4284 bytes, SHA-256
669574b9d62dbca1f017e7d47f390bce9fc1a0becc110c90766f87819920661d.

### Fixture-only correction at the second author return

Only the test fixtures and their focused source controls change. The factory
now explicitly assigns the current user's owner with icacls, then independently
reads the object's owner SID and current token SID using read-only Get-Acl and
WindowsIdentity. The fixed query runs without a PowerShell profile, takes its
literal fixture path through a process-local environment value and has a
30-second timeout. This is a fixture verification helper, not another product
custody implementation or an authorization source.

Each ACL or owner perturbation starts from a verified user-owned private
baseline. Child fixtures are verified before inheritance is enabled. The
junction target must pass that baseline, and the link must independently show
the reparse attribute before the driver checks it. The wrong-owner control
first proves its private current-user preimage, then independently proves the
specific Administrators owner before expecting refusal. Setup errors are test
errors; each of the eleven negative cases must match its specific intended
refusal reason. An unrelated wrong-owner exception can no longer count as a
junction, inheritance or foreign-principal control success.

All 23 local focused methods passed after correcting one initially detected
parser typo; the failed and passing local logs are both retained. Five added
methods cover ownership/readback order, setup-error classification, child and
junction preimages, the bounded literal owner query, and the complete
14-case/11-negative reason population. These Linux tests model fixture helpers
and inspect source; they do not execute Windows APIs or prove the new Windows
preimages. A distinct source review and an actual Windows source-only result
remain required.

The product private_store_directory, seven-field pin guard, packaged runtime,
workflow and native gates are unchanged. No Linux lifecycle mode was re-executed
for this fixture repair; the three actual successful results above are retained.
The existing push workflow has no Windows-only selector, so any root publication
using that unchanged workflow will still schedule both jobs. This does not
authorize a protected/native retry or transform fixtures into genuine turns.

## Third published source CI — run 43678583519

Root retained the independently reviewed fixture correction and receiving
records in local commit c430ef8e5759bfd4eddff4c10b7ab2e442b6d60c, then published
the same tree f87743459496d6a3bfe7d5bf5f8a3312eecfa0e3 as
5f90dd5ecf80ad2d3f153811348d5da72287c4da. Run 43678583519, attempt 1, began at
2026-11-15T04:51:45Z and was completed at 04:52:21Z with overall failure.
Linux job 132704049669 succeeded; Windows job 132704049500 failed. Both uploads
succeeded. Metadata and all received artifact identities bind that exact source
HEAD/tree. Each artifact was received once, with matching byte count and digest.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Linux 14146654617, dg17-linux-source-only | 10848 | 87cc4c6d93f954b1f5a392a8e502d3cda61b5e3ac165baa74c8ccbddd8575bc2 |
| Windows 14146584706, dg17-windows-store-source-only | 3330 | 82efef942ea2d4f83f7ecfd5540a760c1cfb33e63f67585aece40eed24a28150 |

The immutable receiving packet is
.IMPLEMENTAUDIT/dg17-ci-43678583519/SOURCE_CI_RECEIVING.json, 43050 bytes,
SHA-256 c7b2ef7e4bd10232e73f8c59ae5e956a86a5efd838b4fe038bdd943e517dc2e4.
It includes provider/jobs metadata, both artifact metadata and one-shot receipts,
complete PINS records, all Linux result records and all original Windows rows.
It was frozen for a distinct receiver before this next source correction.
Received members/receipts are not rewritten. Signed URLs and raw materialization
wrappers were transient only; no archive body was retained locally.

### Deterministic results and Windows first failure

| Linux mode | Actual result | Elapsed seconds | Result JSON SHA-256 |
|---|---|---:|---|
| native-boundary | SOURCE_STEPS_01_TO_10_PASS_NATIVE_BOUNDARY_NOT_CROSSED | 5.97036886 | 628d7b392b4354510402d4c1815f85132877d7f13cfcc0dbde5e14d426aedf6a |
| full | DETERMINISTIC_LIFECYCLE_PASS_WITH_SIMULATED_NATIVE_SEAMS | 9.624214375 | 5525daa01d61c61d4d84287d68efd16c0dd96bb14f0ed4798167ca42a9993d88 |
| blocked-hook | FIRST_NONPASS_CONTAINED_AND_CLEANED_UP | 9.561137405 | 94a42cdc93764084f3add7d3c4aa62ed1c115014cd41ba58553bbee50fb430eb |

The hosted source-control suite also passed 23 methods in 0.156 seconds.
All native-shaped activity remains simulated, genuine turns/appservers remain
zero, and both full/blocked results retain known teardown only in simulation.
These results add no native authority or original14 receiving.

Windows again passed the unchanged seven-field source-identity check and
generated PINS. No mismatch diagnostic was emitted; the first run's identity
refusal remains unexplained. Its operation is 18437 bytes, SHA-256
ea9c5102721baf9157e84eae9e5f327cf50e32bfed3d69cbebf89e07bc9ca04f;
Linux's operation is 18684 bytes, SHA-256
7f9b7b71127552ff4c904d81a7dd3e5e89ee08bebb3281acf0d40ec28c6753a1.
Both remain source-only with nine unresolved inputs and unchanged limits.
All generated member pins are retained in the receiving packet and manifest.

The Windows output is CASES 14 FAILED 13. The first error is the independent
fixture owner query: PowerShell found Get-Acl in Microsoft.PowerShell.Security
but could not load that module, with error identifier
CouldNotAutoloadMatchingModule. All thirteen owner-dependent cases reported
ERROR and recorded zero verified preconditions. Only the missing-directory
negative reached its intended refusal. This is a failed verification-helper
execution, not demonstrated completion of the repaired owner/preimage controls.
The underlying module-load cause is unknown and is not inferred from the log.

The original store-custody.log is 14852 bytes, SHA-256
ef52a3baa386e74437bdd6fd40465d7b6fe38db0ace153fa83cfd3eeafc6b706.
All 13 ERROR outcomes remain unqualified. They are not relabeled as skips or
negative-control passes. The previous 14-case/1-failure result and its seven
intercepted negatives also remain unchanged.

### Smaller owner-query correction at the third author return

The product's existing ctypes/Win32 owner and DACL implementation and the entire
fixture were re-read before choosing the correction. Get-Acl was introduced by
the fixture alone. A separate engineering documentation check compared a direct
.NET read with a new ctypes owner reader. The latter would add FFI signatures,
token and descriptor buffers, and explicit native resource lifetimes. The
smaller change retains the already executed fixed Windows PowerShell engine and
replaces only its cmdlet-dependent query/output contract.

Microsoft documents the .NET Framework
[Directory.GetAccessControl](https://learn.microsoft.com/en-us/dotnet/api/system.io.directory.getaccesscontrol?view=netframework-4.8.1)
and
[File.GetAccessControl](https://learn.microsoft.com/en-us/dotnet/api/system.io.file.getaccesscontrol?view=netframework-4.8.1)
overloads taking AccessControlSections. The query selects Owner, chooses the
directory/file method using the Directory attribute bit, obtains the owner as a
SecurityIdentifier, and reads the current WindowsIdentity.User SID. The
[WindowsIdentity.User contract](https://learn.microsoft.com/en-us/dotnet/api/system.security.principal.windowsidentity.user?view=netframework-4.8.1)
and
[ObjectSecurity.GetOwner contract](https://learn.microsoft.com/dotnet/api/system.security.accesscontrol.objectsecurity.getowner)
support that independent SID readback. These documentation checks are not an
actual Windows execution result.

The query now disables automatic module loading and uses only direct .NET calls
and PowerShell language constructs. It resolves both SID values, disposes the
WindowsIdentity and emits exactly two lines with Console.WriteLine. Get-Acl,
ConvertTo-Json and Import-Module are absent. The fixed executable, NoProfile,
NonInteractive, encoded fixed query, absolute fixture path supplied through a
process-local environment value, and 30-second timeout remain. No host module,
profile, environment installation or global configuration is repaired or altered.

Python requires a zero process exit and exactly two ASCII numeric SID strings.
It preserves the distinction between a syntactically valid different owner and
the current user: the former still fails the current-user ownership precondition.
Every explicit ownership assignment, independent equality check, private
baseline, child/junction preimage and intended refusal reason is unchanged.

The focused contract was RED against the prior query/parser, with the failed
log retained as owner-query-controls-red.log. After the minimal correction,
all 24 methods passed in 0.140 seconds. Positive controls cover both matching
and different owner SIDs; adverse controls cover nonzero query exit, missing
values, extra output, malformed or non-ASCII SID text, and an extra blank line.
The source control also checks both directory/file API branches, owner-only
selection, module-autoload disablement, native identity disposal, exact console
output population, literal path separation and the existing timeout.

These are Linux source/model controls. The direct .NET calls still require
actual Windows execution after distinct source review. This author does not
award that result or a receiving disposition. Product guards, the seven-field
file identity check, runtime, rehearsal, workflow and native gates are unchanged;
no native/protected retry or workflow dispatch was performed.

## Fourth published source CI — run 43679794953

The reviewed .NET query source and independent records were retained in local
commit 4db726a4f5c7f6429589a941977e233ece967e91 and published by root as
50c7fd7e279cd1f97345941d1ef13d6d76412cd8, tree
df9b72c932a0b60dca918232567e725fa0585771. Run 43679794953, attempt 1, began
at 2026-11-15T05:08:44Z and completed at 05:09:19Z with overall failure.
Linux job 132707719487 succeeded; Windows job 132707719628 failed. Both uploads
succeeded. Exact source HEAD/tree and artifact metadata were received before
one bounded body GET per artifact; received size and digest matched.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Linux 14148315355, dg17-linux-source-only | 10890 | 3d14e32df915506fe50516088566b49ecbcbb6dc7dd561347fdc6bf4186a4a32 |
| Windows 14148045576, dg17-windows-store-source-only | 3314 | 69abaf53d164e88ca49c10f5c846cb887f01d9b0a77abdf08aedb295dfb729fc |

The immutable receiving packet is
.IMPLEMENTAUDIT/dg17-ci-43679794953/SOURCE_CI_RECEIVING.json, 42735 bytes,
SHA-256 b2abc0db85b8c0faa3708b6d9b8e3ef642c42c45468abdf5471c6c03d5fad03c.
It preserves provider/jobs metadata, both one-shot receipts and complete source
PINS, all Linux results, and all original Windows rows and preconditions.
It was frozen for distinct receiving before the fixture correction below.
Raw received members and receipts are unchanged; signed download URLs and raw
materialization wrappers were not retained.

| Linux mode | Actual result | Elapsed seconds | Result JSON SHA-256 |
|---|---|---:|---|
| native-boundary | SOURCE_STEPS_01_TO_10_PASS_NATIVE_BOUNDARY_NOT_CROSSED | 5.298220503 | 9eb97621d7d23091343a34e0ff1ad4104866b51a411611a51dfc347b7085519d |
| full | DETERMINISTIC_LIFECYCLE_PASS_WITH_SIMULATED_NATIVE_SEAMS | 8.153142539 | 4258704e15b5e6c24e3f0963cef2518aaeb28f69b3661fb4571a4a2058875986 |
| blocked-hook | FIRST_NONPASS_CONTAINED_AND_CLEANED_UP | 8.082771011 | e46b133bf341499ed5a6af0a13f4684be81511b55da1467345d3051e4554586b |

The hosted source suite passed 24 methods in 0.146 seconds. Simulated native
traffic remains simulated; all results retain authority NONE, zero genuine
turns/appservers and all 14 custody differences UNKNOWN.

### Actual Windows progress and first remaining predicate

Windows rebuilt successfully under the unchanged source-identity guard. Its
PINS.json is 3851 bytes, SHA-256
ee440d0526b4e26eca88852f89186d69c35eb2b31c2ab23500cc3935922d155e;
Linux PINS.json is 3935 bytes, SHA-256
0c297f0084e25275a195c6d4de33554ee24804e5408bcdcbbcd77770770bfdb8.
All generated-source pins remain bound to this exact run in the receiving
packet and manifest. No mismatch diagnostic occurred, and the original
unexplained identity refusal is preserved without a guard change.

The direct .NET owner query actually succeeded: the log contains 23 independent
owner-SID readbacks, each matching the expected current-user SID. It also records
one complete private-baseline precondition. Driver-created store creation and
re-check both passed. The missing-directory and regular-file negatives reached
their intended reasons. This qualifies the owner readback only for these actual
fixture observations; it does not regrade the failed Get-Acl run.

The Windows population reports CASES 14 FAILED 10. The first remaining failure
is the icacls-created positive's private baseline. Ownership is now correct, but
the product guard sees an Administrators allow ACE for S-1-5-32-544 with mask
0x001f01ff. The guard checks inherited-entry rejection before its foreign-SID
rejection, so its reported foreign-SID branch identifies this as a non-inherited
entry. No more detailed origin of that remaining entry is inferred.

Ten cases correctly report ERROR before their intended positive or perturbation:
manual private positive, Administrators ACE, Everyone write/read, both inherited
Users cases, junction target, unprotected DACL, existing-path create and wrong
owner. Thus only two of the eleven intended negative predicates were reached.
The full 14-case Windows population is unqualified. The original store log is
12700 bytes, SHA-256
c78eee46c626be1f4f6700c488d304edb685f5eeab21026597eaf823e8395fbe.

### One-command fixture DACL correction

Source inspection and the
[Microsoft icacls contract](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls)
explain the setup gap: replacing grants for named SIDs does not clear an
unrelated explicit grant, and disabling/removing inheritance removes inherited
entries. The existing `/grant:r` calls therefore do not establish a complete
private DACL by themselves. The documented `/remove:g` operation removes granted
rights for its specified SID.

The shared fresh-directory factory now calls
`icacls(p, '/remove:g', '*S-1-5-32-544')` after granting user+SYSTEM and before
the unchanged complete private baseline. This addresses every affected factory
use, including parent and child preimages. Intended extra grants still occur
only after that baseline, so the Administrators negative adds its tested ACE
back afterward. An unexpected different principal still fails the baseline;
the correction neither suppresses that error nor substitutes a partial check.

The focused test was RED with three failures before that one command was added.
Afterward all 25 methods passed in 0.145 seconds. The regression models the actual
residual Administrators grant, requires its removal before a positive baseline,
then verifies that the intentional Administrators perturbation is refused.
A separate adverse fixture retains an unexpected Everyone grant and must report
a baseline ERROR. The owner/query and perturbation ordering control also passes.
Both RED/GREEN logs are retained. These local models do not replace the required
actual Windows result after distinct source review.

The correction is limited to that fixture command and its tests/evidence. Owner
assignment, the now observed direct .NET reader, all 14 cases and eleven intended
negative reasons, product custody and file-identity guards, runtime, rehearsal,
workflow and native gates remain unchanged. No source CI was dispatched or
retried by the author, and no protected/native grant or UNKNOWN replay occurred.

## Remaining acceptance dependencies

1. Distinct review and actual Windows receiving for removal of the observed
   unwanted baseline grant and completion of all 14 intended controls. Retain
   actual direct-owner readback and Linux results, the seven intercepted
   negatives, both later ERROR populations, and every earlier failed outcome
   at its exact source identity.
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
