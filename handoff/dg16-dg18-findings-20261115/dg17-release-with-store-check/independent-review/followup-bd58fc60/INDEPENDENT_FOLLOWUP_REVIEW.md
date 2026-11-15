# DG17 independent source followup review — 2026-11-15

## Disposition

**SOURCE_PUBLICATION_SCOPE_QUALIFIED.** No blocking finding was found in the
exact six-file followup for root's guarded source publication and the unchanged
bounded source-only workflow. This is advisory independent source-engineering
evidence, not a grant or a formal audit-assess lifecycle disposition.

Reviewer: `/root/dg17_independent_review`, distinct from the source author and
root principal execution controller. Root controller `pro-executor-01`, G0003,
owns reconciliation and publication. No reviewed source, native application,
remote object, grant, acceptance state, or custody disposition was changed by
this review. Review evidence was written only under `dg17-review`.

The review continues the earlier source review; it does not repeat unrelated
qualified work. The commission, original issue #211 contract, native-turn
amendment, and prior review's evidence ceilings remain applicable.

## Exact object

| Item | Identity |
|---|---|
| Candidate commit | `bd58fc6087f6bf35c244f2661c71d28467296204` |
| Candidate tree | `7219d14138ee96e13e301b078a1502fdfba193de` |
| Local parent | `5a6825c73de82d7ba45d584527da882310f20a62` |
| Parent tree | `7da9f4e0d40e8dfb32d5dcf78df46b4e70c31f14` |
| Published parent with that tree | `52065bcee405715a2fc31d78b3aefd2958ba96a0` |
| Worktree | Clean before and after review |
| Scope | Exactly six changed files; no workflow, packaged runtime, native driver, operation-limit, or Windows custody-predicate change |

All following paths are relative to
`handoff/dg16-dg18-findings-20261115/dg17-release-with-store-check/`.

| Changed file | Bytes | SHA-256 |
|---|---:|---|
| README.md | 2630 | `3327dc00d87c8ef9026e6f24da8cf50b0937534648cbf63e2e346f25426e2dca` |
| SOURCE_QUALIFICATION_MANIFEST.json | 19380 | `3113a83df3b651bdec4049902fcdbcbf90c2b5f20e65a430a7e7de2f257fe081` |
| SOURCE_REHEARSAL_20261115.md | 17098 | `0296e334ffbadcdc2910543843eec1104ca78e82aac81585b56b6c930180a189` |
| tools/build_release_acl.py | 16332 | `1342d5c89dbe73bba4ddeec07bc2b7217ffe211f4d6405e3f80d4e617b6adc6f` |
| tools/rehearse_lifecycle.py | 26290 | `59b0cc7daf8ffd65bbff00293b03235755a668e8b94254ff42f7c3075fb4cb16` |
| tools/test_driver_bundle.py | 18126 | `55eba74095bbfeddd0f70bd773dd32be78b4ab64f73c431858c46a7fe1f2b066` |

The manifest's followup population, lengths, and hashes match this exact diff.
Its initial author snapshot remains separately preserved.

## Findings by changed behavior

### Executable identity and binding data

The first hosted Linux failure is an actual harness defect: the previous guard
applies a Codex-name test to every argument, including the valid binding data
`--host-id codex`. The independent test extracted the exact nested guard from
the frozen parent Git object and reproduced that refusal without spawning a
process. The successor admits that same command through the exact selected
Python interpreter.

The successor still resolves argv[0] and admits only the selected Python, Bash,
and Git paths. Direct foreign/native executables, foreign executable lookup,
literal app-server arguments, string commands, empty commands, and shell=True
are refused. Bash is further restricted to the two exact canonical owner paths:
`claim-run.sh` and `validate-run-root.sh`. Both owner paths pass; Bash without a
script, relative script names, -c, -lc, and foreign scripts refuse.

The current call sites do not supply an alternate Popen executable or a shell
override. Native RPC construction remains the unchanged process-free fixture.
As in the prior review, this is a guard for the inspected deterministic command
surface, not a universal sandbox for arbitrary descendants of Python or Git.
The source-publication finding does not expand that claim.

### Windows identity refusal

The before/open equality still uses precisely st_dev, st_ino, st_mode, st_nlink,
st_size, st_mtime_ns, and st_ctime_ns. The after-read and final-path comparisons
retain that same complete tuple. No field is normalized, ignored, or weakened.

The new diagnostic is emitted only after the original pre-read mismatch. It
contains Python version, the differing field names, and the two numeric tuples;
it excludes input paths and payload bytes. Independent instrumentation proved
that a mismatch raises before any stream.read call, including a simultaneous
two-field mismatch. Separate controls changed each of the seven fields after
reading; every case retained the original during-read refusal.

The previous Windows job remains failed. Its original traceback gives neither
the differing tuple field nor Python version. This followup gathers the missing
facts on another bounded source-only run; it does not repair or qualify Windows
identity, store custody, or owner-machine behavior.

### Preserving the first failure

The new failure summary preserves stage status/error fields and completed
nonzero source-command records even when a cleanup exception is the final
traceback. It records authority NONE, no native acceptance, zero genuine turns,
zero native appservers, and fourteen unresolved custody differences.

Independent controls retained both an earlier binding failure and a later cleanup
failure, kept the stage's original predicate, enforced the 4096-character stderr
tail, excluded oversized and symlinked evidence members, and excluded boolean
values from numeric exit-code records. A separate main-path control made the
diagnostic itself fail and proved that the original exception object was still
reraised. The diagnostic failure does not turn the run into success or replace
the causal exception.

## Hosted failure evidence retained

The locally retained logs, result, PINS, metadata, and receiving receipts for
run 43675846002 were inspected. Every retained artifact-member hash agrees with
the exact followup manifest. Archive bodies were not reacquired in this review;
the preexisting transport receipts retain their own authority ceiling.

| Earlier job | Preserved finding |
|---|---|
| Linux 132695703877 | Native-boundary fixture passed real deterministic steps 01–10 and stopped before native creation. The full fixture later refused the binding data argument and ended with unknown teardown. Complete lifecycle remains failed; blocked-hook was not reached. |
| Windows 132695704092 | Builder refused the pre-read lstat/fstat comparison. No generated PINS and no private-store controls were reached. |

The received Linux PINS binds published source
`52065bcee405715a2fc31d78b3aefd2958ba96a0`, tree
`7da9f4e0d40e8dfb32d5dcf78df46b4e70c31f14`. These are retained historical source
observations, not outcomes for the new candidate.

| Retained evidence | SHA-256 |
|---|---|
| Linux full.log | `55b2aad658a20e44e0b5623775e41cc12c2d2d031d3c39f9e458b88504626298` |
| Linux native-boundary result | `fa29f86df2cc923a998ee54949c39ea00875b9569f46c3e973997b1dbfb40167` |
| Linux rebuilt/PINS.json | `c78f6332e614ba9d4ed3f4ea4ca96eb05f7758e21153782d439a25bf1a2706d1` |
| Windows rebuild.log | `2feea6bbab976b5496a41e59353add154ddb82cee7cd73054bca4a4eb750723f` |

## Independent verification

| Check | Observed result |
|---|---|
| Supplied focused suite | PASS, 18 methods |
| Independent followup suite | PASS, 7 methods |
| Exact six-file manifest and retained artifact-member hashes | PASS |
| git diff --check against frozen parent | PASS |
| Final candidate identity and clean worktree | PASS |
| New complete hosted lifecycle | NOT RUN by this reviewer; still pending |
| Real Windows API/store controls | NOT RUN by this reviewer; still pending |
| Native/model/remote effects by reviewer | None |

The supplied suite used unchanged assertions and code. Only its disposable
TemporaryDirectory location was redirected into the review directory.

| New review evidence | SHA-256 |
|---|---|
| supplied-18-controls.log | `2d44a8f393b75b33a451bec5a09c3d73a6a7a81b010e340522365fb823164a43` |
| independent_followup_controls.py | `f4c5193588352c3efd222e19e9d7be75b28e76f4f11fd64a19c7013fb003fbd4` |
| independent-7-controls.log | `69d094b7a055b668a1d342484a1612289b34e49391dcfb248fa872b7c42752c9` |

## Root-owned continuation and retained limits

Root can reconcile this review with the existing source-engineering authority
for the exact guarded engineering branch. The unchanged workflow's branch,
permissions, action pins, bounded fixture scope, and prior source-head receiving
condition remain in force. The new run must be received at its actual source
identity; earlier failed runs remain failed.

The Windows mismatch's cause remains unknown, and complete deterministic
Stage A/B qualification remains pending. There is no authority for a native
episode in this review. The final Windows operation, all exact host inputs,
fresh written owner grant, two authentic Codex turns, independent post-A
receiving, POST_B, T12, original14 receiving, and custodian certification remain
required. All fourteen custody differences remain UNKNOWN, with no replay.
