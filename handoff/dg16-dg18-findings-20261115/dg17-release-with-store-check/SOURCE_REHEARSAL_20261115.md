# DG17 source qualification return — 2026-11-15

Status: **source corrections and focused controls qualified locally; complete
deterministic lifecycle and Windows controls await the scoped CI host**.
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

CI receipts are pending at this author return. The independent reviewer and
root publisher must inspect the exact candidate before publication; the author
does not award independent approval.

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
