# DG18 W-FULL — actual independent receiving, run 43775060535

Received 2026-11-15T23:37:06Z by the distinct DG18 receiving lane. Scope is the single actual authorized Windows attempt and its retained originals. No source change, native invocation, test replay, cleanup, compensation or retry was performed by this receiver.

## Disposition

The exact owner operation **ran once, completed the G0003 transition and returned exit 0**, but **failed the original W-FULL aggregate-memory limit**. The actual recorder disposition is `OWNER_LAUNCH_ATTEMPTED_UNQUALIFIED`, with `QualificationError: invalid or over-envelope aggregate Job committed memory`. This is an actual consumed operation with successful continuity effects and failed numeric qualification. It is not an unlaunched preparation, and it cannot be replayed as an unused attempt.

The first failing source predicate is `scripts/check-r0039-windows-resume.py` line 122 at runtime 775d6a0a: `peak_single_process_committed_bytes <= peak_job_committed_bytes <= MAXIMUM_JOB_BYTES`. The retained complete job log reaches that predicate through `run-r0039-windows-resume.py` line 363, after its source-currentness and original14 transition checks. `FAILURE.json` records the failure at 23:31:08.203656Z. Subsequent bounded observation ended at 23:31:24.937308Z; the provider run was terminal failure by 23:31:33Z. `RESULT.json` is absent, as expected after rejection.

## Exact execution and acquisition

| Item | Actual identity |
|---|---|
| GitHub run / attempt | 43775060535 / 1 |
| Executing job | 132999386253, `execute-received-operation` |
| Workflow commit | `acc54478991a5a0e2193e12af5d76ecffd266188` |
| Workflow tree | `526677cf81c2160f58cf2913c13250924c477012` |
| Product source / tree | `775d6a0add0a1edcbc7f6cf5ccd68d350757fe8a` / `66607502c26f533416aa9cc00b3b5728e1e0e11e` |
| Operation SHA-256 | `e0ac5d2992e44b45e838802c571fa84e27542aa72afab6ebb05c015e3207ec23` |
| Artifact | 14186060941, `dg18-w-full-continuation-43775060535-1` |
| ZIP | 1,292,527 bytes; SHA-256 `cd56c78ed6b80959d229275da6ef1c7bd02b012b053989fc28d23722a83c6a18` |
| Complete executing-job log | 41,522 UTF-8 bytes; SHA-256 `62cf05b7e2f9a82facc7bba53ff9c29c5688d41ae4a3b06ccba355602391c2d8` |

The ZIP was acquired once through the ordinary configured network and matches both provider artifact metadata and the upload log digest. The complete executing-job log was fetched once. The 70 unique ZIP members were safely materialized and compared with the retained archive bodies; their descriptors are in `ARTIFACT_MEMBERS.json`. No G132 frozen resolver was used, no second artifact acquisition occurred and no protected operation was launched by this receiver.

Provider originals are retained in the initial and terminal `*_TOOL_RESPONSE.json` files. The execution job's checkout, guarded-push check, physical runtime selection, original-artifact receipt and exact restoration steps succeeded. Its one execute step failed; both post-attempt capture and upload succeeded. The old preparation job was skipped. Actual run: https://github.com/theislampill/IMPLEMENTAUDIT.md/actions/runs/43775060535 .

## Actual process and memory observations

| Observation | Actual value | Original qualification implication |
|---|---:|---|
| Whole measured interval | 29,961.0286 ms | Within 60,000 ms |
| Root exit observed | 29,960.9153 ms | Before the whole interval ended |
| Aggregate Job peak committed memory | 250,466,304 bytes / 238.86328125 MiB | Exceeds 201,326,592 bytes / 192 MiB |
| Excess | 49,139,712 bytes / 46.86328125 MiB | 24.407958984375% above the limit |
| Peak single process committed memory | 56,119,296 bytes | Does not replace the aggregate metric |
| Kernel total / creation / exit events | 2,340 / 2,340 / 2,340 | Ordered lifetimes reconcile |
| Final zero events / terminal active processes | 1 / 0 | Job empty after root exit |
| Abnormal exits / kernel terminations | 0 / 0 | No abnormal termination recorded |
| Observed processes / observation failures | 2,340 / 0 | Actual process identities retained |

The receiver independently reconciled the ordered event stream against kernel totals, including unique live lifetimes and the sole final `ACTIVE_PROCESS_ZERO`. The exact pinned root Bash, Python and direct Git images were observed in the Job. The measurement retains `cleanup_complete: true`, root suspended before assignment, completion-port association before assignment, Job flags 8192, breakaway disabled and zero baseline subtraction. Its complete scope is this private Job and descendants; it does not claim a census of work outside the Job. The field `sampled_pid_census_complete: false` is the maintained design: completeness comes from kernel/process-event reconciliation, not sampled PID observations.

The actual native control also completed: five creation and five exit events, one final zero event, 1,117.7383 ms, aggregate peak 95,350,784 bytes and single-process peak 41,234,432 bytes. Its child and Git exited 0. The control discriminates aggregate memory and is retained separately from the main owner interval.

The main image population includes 1,120 `Git/cmd/git.exe` wrappers and 1,141 direct `Git/ucrt64/bin/git.exe` processes, 57 `Git/usr/bin/bash.exe` processes, four Python processes and the remaining recorded shell/console processes. Those counts describe actual observations. They do not themselves attribute the aggregate memory peak to a particular source call or authorize excluding any process.

## Actual continuity effects and preserved task state

The owner stdout, receipt verification and currentness requirement all returned the same actual G0003 receipt, with exit 0. Canonical generation resolution and the separate STATE/ROADMAP reads also exited 0. The receiver checked the original 14 receipt fields, exact Git blob identity, pointer identity, unchanged controller/claim/run, predecessor receipt binding, permanent marker and protected payload equality against the prepared operation.

- Current pointer: `refs/implementaudit/current-generations/dg18-w-full-43721708486-1@db4886253d0ed4a596aba8da111798f42ef954ec`.
- Current receipt: `refs/implementaudit/continuity-receipts/dg18-w-full-43721708486-1/G0003@6eb7f743aa3c41537f4e01a486f8c977a793502c`.
- Permanent marker remains `8126b77007aeb74d1fde5a0da86a7e8de8f4b255`.
- `RECEIPT.raw`: 784 bytes, SHA-256 `be9c26ba2edd928958f285f06b96dccbb85a5fbe7630d66bd7d5377e8d920b5e`.

All six retained predecessor/archive/retired-document bodies and all 25 retained original refs match the prepared record. The captured after-subject contains all 44 unchanged runtime files. The raw G0003 pointer and receipt objects also match the captured Git objects and refs. The actual post-attempt STATE and ROADMAP hashes are `c5615c7b1dc1e019502bc256d4d480ccd1cf49d7ba32e3ebab87d460f8124e83` and `045a4b6ca1c002b5a2eb867799ac270a0d4dc3ab15eab3e307ba6d4ba0c3c367`; their protected payloads equal the prepared payloads.

The subsequent unqualified readback preserved equal before/after ref scans, no recorded observation errors and successful currentness/canonical-resolution queries. Its resume-resolution query exited 1 with the actual message: **`native boundary is already consumed by the current generation`**. This is decisive against reusing e0ac.

`SUBJECT_AFTER.tar` is 4,505,600 bytes, SHA-256 `c1a1d4ff1d1b4553360fd933851b33db4f2adaf16f6e4f05e852b65b3e8b25ce`. Its 263 safe entries contain 186 regular files; every file body matches `SUBJECT_CAPTURE.json`. Its 40 loose implementaudit refs include the recorder's exact 38-ref owner projection plus two existing initialization refs. A receiver-only assertion initially compared the full population with that smaller projection; correcting the comparison to the existing `refs()` definition yielded an exact match. No source or original artifact was changed to resolve this receiver comparison.

## Authority and acceptance boundary

This attempt used the actual owner grant and the owner's express retirement of the commission-only two-owner-original requirement. The retained grant body equals the reviewed launch input. The exact operation, runtime and original 60-second/192-MiB constraints remained unchanged. Root supplied the actual G132 terminal/noninterference determination before its sole guarded push; this receipt does not substitute an independent whole-host census for that Root observation.

The one granted Windows operation has been consumed. Its task transition is preserved as a real successful effect; its W-FULL memory result remains a real failure. No automatic retry, compensation, limit change or new operation follows from this receipt. No OR, C02 native-event, E/F participant, H0, N1 or whole-issue acceptance is claimed. N1 remains LOST/UNKNOWN, and criterion 5 is neither reconstructed nor waived.

## Retained originals and receiver files

The acquired ZIP, `JOB_132999386253.log`, original provider responses and all 70 extracted files are retained in this directory. The complete facts are in `ACTUAL_RECEIVING.json`; the member descriptors are in `ARTIFACT_MEMBERS.json`.

| Original | Bytes | SHA-256 |
|---|---:|---|
| `execution/FAILURE.json` | 276 | `838841c5d44557f8b431f83c6e64669eb6cedb245204a9e6ef1844ea231d629f` |
| `execution/MEASUREMENT.json` | 923,283 | `95ff8852269e6877bb4765125bd3c8db75ada2ac49e7c9e6558c4fa23877f201` |
| `execution/CURRENT.json` | 2,613 | `8dd6c794ddaf2fc499928de69919b96c685534526303d0c4dcad54e6a5545019` |
| `execution/PRESERVED_AFTER.json` | 4,544 | `496c9e2526e994c6761db7a92c4c7b434ba6a2a4448c376cdd88298d97c88252` |
| `execution/unqualified-readback/OBSERVATION.json` | 13,196 | `a093c0e6e7dedce4523688bc422ad80b9fa775d147e8c354aa14d8c0cdbb560b` |
| `execution/native-control/control.json` | 4,408 | `662a5a3724359ef5c27bb3e485ea815379c391c4143350bbfad0aea5524c7b97` |

All paths in the final table are under `extracted/dg18-w-full-43721708486-1/operation/`.
