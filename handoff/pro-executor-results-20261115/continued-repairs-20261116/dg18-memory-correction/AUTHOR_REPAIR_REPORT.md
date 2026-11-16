# DG18 bounded process-overhead source repair

## Result and authority boundary

The isolated candidate corrects the observed Windows Git layout omission and requests replacement of the otherwise final claim-validation shell by its Python interpreter. Five focused ordinary controls pass, the active source bindings are exact, and both candidate archives retain the original 2,000-byte reserve. This is a source repair with ordinary verification. It does not establish that a future Windows execution will meet 192 MiB, change the failed original result, admit C02/C5, or authorize a protected operation or retry.

The candidate is frozen at `/workspace/scratch/7fbb79f74aa4/recovery/dg18-memory-correction`, based on commit `775d6a0add0a1edcbc7f6cf5ccd68d350757fe8a`, tree `66607502c26f533416aa9cc00b3b5728e1e0e11e`. No commit, publication, hosted run, native operation, new preparation, grant or retry was performed by this author. Root retains publication and acceptance decisions. The distinct DG18 lane receives this candidate independently.

Root's narrow commission, the existing repository instructions and the actual retained run were consumed. Only active runtime bindings and the required retained reader dependency were changed; no broader source qualification programme was started. `SOURCE_FREEZE.json` records all nine exact paths. `SOURCE_CORRECTION.diff` includes the added retained file as well as tracked modifications.

## Actual failure retained

The original Windows run is **43775060535**. Its measured owner command completed with exit **0** in **29,961.0286 ms**. The actual G0003 transition/currentness result remains earned. The recorded complete Job peak was **250,466,304 bytes**, above the unchanged **201,326,592-byte / 192 MiB** limit by **49,139,712 bytes**. The successful command and failed aggregate-memory predicate are separate facts. Original operation `e0ac5d2992e44b45e838802c571fa84e27542aa72afab6ebb05c015e3207ec23` remains consumed; source changes do not reopen it.

The retained measurement is:

`/workspace/scratch/7fbb79f74aa4/recovery/received/dg18/actual-43775060535/extracted/dg18-w-full-43721708486-1/operation/execution/MEASUREMENT.json`

It is **923,283 bytes**, SHA256 `95ff8852269e6877bb4765125bd3c8db75ada2ac49e7c9e6558c4fa23877f201`. The compact `PROCESS_OVERLAP_PROJECTION.json` was derived from that actual file without modifying it.

There are 2,340 distinct observed processes, all recorded inside the Job, exactly 2,340 creation events and 2,340 exit events, a kernel total of 2,340, and terminal active count zero. The independent ordered-event sweep found no duplicate active creation, unmatched exit or nonempty final population. Among the images were 1,120 `Git\cmd\git.exe`, 1,141 `Git\ucrt64\bin\git.exe`, 57 `Git\usr\bin\bash.exe`, three `Git\bin\bash.exe`, four Python processes and one PowerShell process. All these processes remain included in the original measurement.

The maximum outstanding population in the ordered event stream is ten: five usr Bash, one bin Bash, two Python, one direct Git and one conhost. **The events contain neither timestamps nor per-event/per-process memory.** This overlap cannot be identified with the moment of the aggregate memory peak. The single-process high-water value, 56,119,296 bytes, cannot be attributed to a particular PID from this record. No memory subtraction, PID exclusion or quantified saving is claimed.

## Findings and corrections

### DG18-PROC-01 — avoidable Git launcher selection

**Severity:** material runtime overhead; source defect demonstrated. **Owner:** existing fixed Git selectors in `claim-run-rotation.py` and `rotate-canonical-state.py`, with the same omission in `read-canonical-pair.py`.

At base775 the two runtime owners search `mingw64\bin`, then `cmd`, then `bin`; neither includes the actual observed `ucrt64\bin` executable. Their Windows child environment also places `mingw64\bin` ahead of the wrapper directories rather than following the selected executable. Consequently an eligible installation containing ucrt64 and cmd, without mingw64, selects cmd for those calls. The original run's 1,120 cmd image observations support the relevance of this exact source omission. They do not by themselves identify parent-child edges or peak-memory ownership.

**Minimal correction:** both runtime selectors now prefer the fixed physical `C:\Program Files\Git\ucrt64\bin\git.exe`, retain the old mingw64/cmd/bin alternatives and their existing regular-file/symlink refusals, and put the selected executable's directory on the child PATH. The claim owner recognizes both direct layouts when deriving the Git root. The projection helper uses `PureWindowsPath` for its explicitly Windows environment construction. Python selection, fixed roots, long-path settings, no-system/global Git controls and refusal behavior remain intact. The reader receives the same direct-layout preference while preserving its existing cmd fallback and Bash invocation.

The paired correction matters: the existing shared custody scope rejects a nested scope that selects a different executable. Changing only one owner could therefore replace overhead with a deterministic nested-binding refusal. Both selectors are changed and tested together. No cache, Git object-read reuse, freshness relaxation, custody change or source-image relaxation was added.

**Verification:** actual runtime functions were loaded and exercised with a modeled Windows filesystem boundary. Controls cover ucrt64 preference, mingw64 and cmd fallback, symlink-only refusal, selected-directory propagation and removal of inherited Git/override variables. Those controls failed against the unmodified base because ucrt64 was absent and the PATH did not follow the selection; they pass against the frozen candidate. This is source behavior verification, not a Windows execution claim. The reader has the same concrete omission but was not established as a separate Python process in the measured resume; no measured saving is assigned to that reader change.

### DG18-PROC-02 — final claim-validator shell retention

**Severity:** bounded avoidable process retention; Windows memory effect unmeasured. **Owner:** the early `--claim-only` / `--claim-custody-only` branch of `validate-run-root.sh`.

The branch selects the existing interpreter, invokes its inline Python, then immediately exits with the result. No shell resource or trap is active in this branch. The later EXIT trap belongs to the full-validation path and is unreachable here. The only code change is the word `exec` before the same interpreter invocation; Python arguments, stdin body, file/Git custody checks, stdout and ordinary numeric exit codes are unchanged.

An initial controlled POSIX probe retained an important distinction: a Python SIGTERM was represented as **143** by the old shell and **−15** by direct subprocess receiving after exec. `TAIL_CALL_BOUNDARY.json` preserves both actual observations and the initial conservative exclusion conclusion. That exclusion was superseded after checking the real consumers and Root's clarification that the numeric representation was not an independent original requirement.

The actual consumers require success versus refusal:

| Consumer | Existing treatment of validator result |
| --- | --- |
| `claim-run.sh` controller custody load | Validator must succeed in an `&&` chain before the claim-id check. |
| `check-evidence-anchor.sh` | Any `returncode != 0` refuses claim validity. |
| `apply-observed-mutation.sh` request/validator paths | Any nonzero result refuses; a reported validator code may differ, but no effect is admitted. |
| `claim-run-rotation.py` initialization validator | Any nonzero result raises refusal after retained-source verification; the Python parent owns its temporary-directory cleanup. |

No inspected consumer depends on numeric 143, treats a signal as success, or requires shell-owned cleanup after this branch. The diagnostic representation difference is retained rather than emulated. Ordinary controls exercised both scopes with exit 0, 1, 2, 3 and a signal, verified success only for zero, and confirmed that the final interpreter uses the invoked process PID on POSIX. Separate real claim-validation controls preserved valid claim/partial-custody success, missing-template refusal for full claim validation, and malformed-schema refusal. These tests do not establish how many physical processes MSYS retains or the size of any Windows memory reduction.

**Exit-3 migration fallback is unchanged.** `rotation_io` in the claim shell remains a child invocation because its caller must inspect exit 3 and retain the existing legacy fallthrough. After reversing only the updated companion byte count and digest, the entire claim shell equals base775. No further tail-call opportunity was changed.

### DG18-PIN-01 — exact active binding closure

**Severity:** required correctness dependency. **Owners:** the existing claim companion source pins and its public shell loader.

The companion's exact projection and initialization-validator byte counts/digests were updated to the changed bodies, then the public shell's companion byte count/digest was updated. All checks remain exact. `ACTIVE_PIN_CLOSURE.json` records those checks, Python parsing, Bash syntax and whitespace verification, and unchanged custody, measurement, limit, package-contract and historical-registry bodies.

The old reader is now materialized byte-for-byte under the existing native-runtime peer layout, and its original manifest dependency is selected there. It remains **27,208 bytes / SHA256 `c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8`**. No historical native peer body or pre-existing manifest file record was modified. This prevents the older donor overlay from silently acquiring the repaired current reader under an old digest.

## Historical scope and known limits

The C5 transport/compiler/operational registries remain exactly as at775. Their latest admitted current-core tuple is an older DG17 source domain, with claim companion 291,624 bytes/hash `866e…` and shell `0815…`. Base775 itself instead has companion 286,898 bytes/hash `420f…` and shell `5700…`. That distinction already existed before this repair. The measured claim/resume path does not consume the C5 transport. Adding a new C5 admission domain, compiler pin/revision or qualification suite would expand this repair's scope, so none was added. This candidate does not claim that those historical registries admit its source or base775.

One unrelated peer-manifest discrepancy also predates the change: `source-peers/native-runtime/skills/implementaudit/scripts/compaction-source-owner-codex-app.py` is 196,162 bytes/SHA256 `83670fe9d57e4c52ef25982b8bf7baf2895d6133e5af3e103e2de46ed31e02d5`, while its retained manifest entry names 185,531 bytes/`5bb21eed89945a8da97857f980b1f85a06dc07df47b25475b9173f23e82ce8f8`. Both actual body and entry were independently compared with git775 and are unchanged. The receipt therefore claims validity of the changed active binding/reader scope, not validity of every unrelated peer entry. Root assigned a separate read-only lineage receiving task; this repair does not alter that discrepancy.

## Verification and archive reserve

The focused command was:

```text
python3 -B fixtures/canonical-state-rotation/windows_qualification_test.py WindowsRuntimeGitLayoutControls ClaimValidationTailControls
```

It ran **five tests, zero failures, zero errors and zero skips**, reporting **OK** in 0.604 seconds. The source fixture and result are bound in `FOCUSED_REGRESSION.json`. The existing current-validator negative-control test received only its exact expected digest update; no broader composite test suite was run or claimed.

The required changed-source archive check used the unchanged builder with the already-installed pinned zopfli **0.2.3.post1**:

```text
/usr/bin/python3 -B scripts/package-contract.py --build /workspace/scratch/7fbb79f74aa4/recovery/received/dg18/memory-correction/archive-reserve
```

The build and built-in verification completed with exit zero. The initial attempt using the default Python stopped before compression because that interpreter lacked zopfli; the successful attempt used the existing `/usr/bin/python3` environment. No dependency, builder or budget was changed.

| Candidate artifact | Bytes | Headroom below 589,824-byte cap | Original required reserve | Result |
| --- | ---: | ---: | ---: | --- |
| `IMPLEMENTAUDIT.plugin.zip` | 586,957 | 2,867 | 2,000 | PASS |
| `IMPLEMENTAUDIT.skill` | 582,356 | 7,468 | 2,000 | PASS |

The configured revision5 canonical builder threshold is 1,240 bytes; it is **not substituted for the original 2,000-byte requirement**. The actual canonical archive passes both. The archives truthfully record dirty worktree content based on775, rather than a published successor commit. Their SHA256 values are `75ee5638bd4b4d53e81bfad12cf7a6a959097d6c29df701c533397b77cd91473` and `18bbf496c03c6e5ab2f567792b7cd04664b7cfe5e09161da35210ff2ea83c1b0`, respectively. `ARCHIVE_RESERVE.json` retains exact counts, identities and both reserve predicates.

No whole canonical suite, hosted Windows measurement, original operation replay, retry, model/native effect, C02/C5 admission or original-memory acceptance is represented by these ordinary results. The next step within this commission is distinct source receiving and Root's ordinary publication decision.

## Frozen packet identities

| Record | Bytes | SHA256 |
| --- | ---: | --- |
| `SOURCE_FREEZE.json` | 2,600 | `b8017f55c1c7dd58145f61eaa5a9e789c61d56a1d3ad52474a9c905e20a00464` |
| `SOURCE_CORRECTION.diff` | 47,838 | `b32d7d851b8e3033fc84d99c97f9be20126ba7acdf5c41133e132d75a71e1eb0` |
| `ACTIVE_PIN_CLOSURE.json` | 3,631 | `b1949965f27a1dc7d710f8b5894763ec1dc2a19ed808dfd04f8994cf88706af6` |
| `FOCUSED_REGRESSION.json` | 1,674 | `2633f17e9b911efaf33e0646ba63c4352ac3fd7998f9f3f67236ccd87338e4c3` |
| `ARCHIVE_RESERVE.json` | 2,162 | `0cb6f2565d06c865e8198d5758d286a3e57583dd6c365818b846b2ca531c4086` |
| `PROCESS_OVERLAP_PROJECTION.json` | 4,314 | `b714f49b210903a72aff5bf962d76f879fdf278a9bda76f85917a97c98b8bffb` |
| `TAIL_CALL_BOUNDARY.json` | 805 | `485385af43fa1604edb52fb5899c739cbe47e10b8290c3f06076449b3f932e2b` |
