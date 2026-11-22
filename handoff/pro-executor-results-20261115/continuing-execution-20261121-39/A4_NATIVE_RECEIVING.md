# A4 compiler-memory R2 — independent receiving of native run 44964191955

## Disposition

**PASS_RECEIVING_AUTHENTIC_FAILED_DIAGNOSTIC_NO_ORIGINAL_AWARD.** The retained evidence authentically records a failed diagnostic. The first native compile worker exited zero and produced ten memory records, but its Job contained **two observed processes**, while the diagnostic qualifier required exactly one. The supervisor stopped at that qualification failure. The R2 reuse and audit workers did not run, and the final source/host checks and held-Git terminal rehash did not occur.

The exact-one-total-process condition is an additional restriction in the compile-only diagnostic. The unchanged pinned Job harness requires complete accounting of its process population and exactly one root lifetime; it does not require the total population to equal one. Current Issue215's applicable aggregate-memory clause likewise requires pinned population and verified descendant accounting, not a universal one-process total. These provenance findings **do not relax this run's frozen qualifier**, admit an additional executable for a future run, replace the preserved original A4 64 MiB guard, or interpret the still-unavailable original R01–R09 contract.

Reviewer: `/root/independent_review`; authority **NONE**. This is ordinary independent receiving, not an internal route, launch decision, original acceptance, or closure. Root alone adjudicates the result. Root supplied G0045 currentness **9be00b/0**, receipt `da78b456997516f38e8e8b048c221bec6e4c0c4b`, with Results38 published at `56f00601d9d6e3083a35014b53610541008f7af5` and PR source still exact51416.

## Exact source, provider and artifact custody

| Surface | Received identity |
|---|---|
| Raw retained packet | `/workspace/scratch/097486cde2dd/a4-compiler-memory-r2-native-44964191955` |
| Raw seal | 8,923 bytes; SHA-256 `524181ef0e38ca9a87639eb7546a4619229bd8faf04ef653ddbc35e33fb8fcfb` |
| Raw payload | 52 files / 593,930 bytes; complete inventory and every hash matched |
| Workflow run | **44964191955**, attempt **1**, run number **1**, push event; completed **failure** |
| Job | **137029396727**, `compile-only-native-diagnostic`; completed **failure** |
| Hosted commit | `105c6c197d27860dc63c4ed149011085ed8ca6a9` |
| Hosted tree / sole parent | `098ff67306e52878422712f2a9ba082e98e7c5fa` / `51416b2f156b341c4a5f09029e2c6ceb5b30b1e7` |
| Distinct branch | `pro/dg18-a4-compiler-memory-51416-20261121-02` |
| Provider artifact | **14730880971**, 26,684 bytes; SHA-256 `56913b5c836f07dc52b5752a4cef5b87597faeb51921f559fe5a84be1050c3c6` |
| Inner diagnostic ZIP | 52,724 bytes; SHA-256 `8b29edecd70f7cc76c2f23a8666b6e569af2cbe0ac17cf0f7c05aa3e198ec245` |
| Inner content | 37 exact members: 36 manifest-listed files / 370,969 bytes, plus `MANIFEST.json` |
| Independent mechanical receiving | **79018a/0**, `MECHANICAL_RECEIVING.json` |

The provider artifact digest, size, run, head commit and branch agree with the retained provider response and upload log. The outer ZIP contains exactly `DIAGNOSTIC.zip` and `ZIP_RECEIPT.json`. Both ZIPs have unique safe member names, valid CRCs, no directory/symlink substitution, and exact byte equality to the retained extraction. Every inner manifest entry was independently hashed; no absent result or missing stage was synthesized. The finalizer and upload steps succeeded after the execute step failed. Artifact availability proves retention, not diagnostic passage. Evidence: raw `RUN.json`, `JOBS.json`, `COMMIT.json`, `BRANCH.json`, `ARTIFACTS.json`, `JOB_LOG.txt` lines 261–280 and 335–338, and both archive receipts.

The complete frozen source packet was rehashed: **13 files / 162,777 bytes**, `FROZEN_SEAL.json` SHA-256 `2a267be1bacd9c735c14a9e42e4014fbd66af90c004866eeb4a7e96889226788`. The complete prior independent source review was also received under seal `429162f6f6b1a3a5f940e7b3eaa9863607e26bd3eb93d9f063aa7a32986f3f6b`. Its independently derived tree matches the actual provider commit and Root's publication plan/readback. All four actual hosted source bodies exactly match the frozen source, hashes and Git blob identities:

| Added source | Bytes | SHA-256 |
|---|---:|---|
| `.github/workflows/dg18-a4-compiler-memory-r2.yml` | 5,224 | `15a9d3d11137a626ce0b306f77e72a8be30bbb674d4994775bbc3249162b5f13` |
| Diagnostic `compile_memory.py` | 40,124 | `5b1c69db38ba68dfb436cbef190efa04d5a592e6b3fd0260346a0da138577a34` |
| Diagnostic `compile_adapter.py` | 6,595 | `4baffb9fdadde5333a1bf535593d4aa794936578be297b1ce723e1f0bd1683b2` |
| Diagnostic `observed_tool_profile.py` | 28,985 | `aa61123993614898f8d731352d04862a5a8fe9b77d1811f640e40870e8bf09b5` |

The three Python files are under `handoff/pro-executor-results-20261115/dg18-a4-compiler-memory-r2/`. Root's admission binds this exact source review, tree, first branch creation and attempt-1 operation; it is historical G0044 admission evidence, not a new grant from this receiver. The source and publication records establish four additions over exact51416, without changed product files. The prior independent full-tree proof is reused at its exact digest rather than recomputed through a new Git operation.

## Observed host and executed prefix

The actual runner log reports **windows-2022 image 20261116.370.1** and successful setup of **CPython 3.12.10**. The selected executable is `C:\hostedtoolcache\windows\Python\3.12.10\x64\python.exe`, 104,952 bytes, SHA-256 `4d6f5f81a4bca11191c4c7c6b43632694d0a4ce74e068619d8fdc161d469859a`. The worker's observed image hash agrees with the supervisor's tool binding. The log does not independently identify cache-hit versus acquisition, so this review makes no cache-hit claim. The reviewed entry also requires native x64 CPython 3.12.10 without optimization and Windows Server 2022 runtime before acquisition; reaching the observed prefix is consistent with those executed guards. Evidence: raw `JOB_LOG.txt` lines 17–20 and 234, `diagnostic/INTENT.json`, `native/STARTED.json`, and `native/job/measurement.json`.

The retained sequence is:

1. The supervisor, PID **3460**, records the fresh-operation admission intent.
2. It acquires the exact Git file and five ancestor handles, hashes the held file, and receives its four-name hardlink population.
3. Four held-Git host checkout checks and two held-Git source checkout checks complete. `INTENT.json` and `SOURCE_BEFORE.json` are written.
4. One `native` worker is started suspended, placed into the private Job, then resumed. The Python root is PID **7412**. A second in-Job image, `conhost.exe`, is observed as PID **6124**.
5. The worker completes four native compile requests, retains four code objects, writes ten native memory observations and `native/RESULT.json`, and exits zero.
6. The Job reaches root exit and kernel active-process zero. Its events reconcile with two process lifetimes, and native cleanup reports success.
7. The supervisor's additional single-process qualifier fails. It closes the held Git/ancestor handles, records `ERROR.json`, and exits nonzero. Independent finalization retains the failure without replay.

This order follows the actual records and the exact executed source path, `compile_memory.py` lines 493–530. In particular, `completed_workers: []` means no worker passed the supervisor's `qualify_job` append. It does **not** mean the native worker was never started or produced no result.

## Fresh held-Git admission and its precise lifetime limit

The actually opened spelling was **`C:\Program Files\Git\ucrt64\bin\git.exe`**, with exactly **4,414,792 bytes** and SHA-256 **`9bf8ee81d79f38a11eaf7799499a634c46a718e009a4a9b2b20b115804643302`**. The initial held-descriptor hash reached EOF and matched that size/hash. The full enumeration terminated with Win32 code 38 and successful enumeration-handle closure. Its four unique names were `git.exe`, `git-upload-pack.exe`, `git-receive-pack.exe`, and `git-upload-archive.exe`, all under `\Program Files\Git\ucrt64\bin`. The recorded counts for aliases opened, admitted, or executed remain zero as applicable. No returned alias became an execution fallback.

The acquisition records five ancestors, root first: `C:\`, `C:\Program Files`, `C:\Program Files\Git`, `C:\Program Files\Git\ucrt64`, and its `bin` directory. The source requests target read-only sharing without write/delete sharing and directory list/read-attributes access `0x81` with read/write sharing but no delete sharing. Handles are created noninheritable. Current acquisition is evidenced; the old metadata run is only a historical constraint, not cached permission. Evidence: `diagnostic/GIT_ACQUIRE.json`, `GIT_OBSERVATION-01.json`, and source `HeldGit.__enter__`, lines 288–328.

All **13** raw observation records were independently checked without invoking the profile code. The receiver rederived same-API path/descriptor identity, the exact CPython path-stat/fstat mode and ctime mapping, ancestor ordering and identities, native file type/final spelling, four-link counts, native handle identity, all alias names and completion status, and comparisons back to the initial live admission. Access time remains the reviewed read-sensitive exclusion; full mode and ctime remain in same-API comparisons. Stat-device value **333453060169384722** and native volume serial **2695480082** remain distinct raw API values; no truncation or numeric coercion was used to make them equal.

Observation 1 is the fresh hash/admission. Observations 2–13 are before/after pairs for **six** Git commands, in fixed source order:

| Command | Checkout and purpose |
|---|---|
| 1 | Diagnostic checkout: host commit, tree and sole parent |
| 2 | Diagnostic checkout: exact four changed paths |
| 3 | Parent tree: all four diagnostic paths absent before addition |
| 4 | Diagnostic checkout: clean status |
| 5 | Product checkout: exact51416 commit and base tree |
| 6 | Product checkout: clean status |

The source uses only the fixed Git executable with `protocol.allow=never`, disabled hooks/fsmonitor, noninteractive operation, no lazy fetch and no allowed protocol for these commands. The six calls' success is established by the guarded control flow reaching `SOURCE_BEFORE.json` and the worker, plus their complete before/after metadata pairs. The diagnostic does not retain independent stdout/exit records for each Git call, so this review does not describe six standalone process-capture receipts.

All observations bind the same receiver PID and monotonic uptime sequence. That supports this in-process held-handle lifetime; it is not a unique boot identifier. `GIT_CLOSED.json` reports the file handle and all five directory handles closed, in reverse ancestor order, with no errors. This is genuine cleanup evidence on the failure path.

**The missing terminal bookend remains material.** Only the initial hash ran; `terminal_rehash_complete` is false. There is no `SOURCE_AFTER.json`, successful final host receiving, or `terminal-held-rehash` observation after the worker. Successful acquisition/use of the prefix and successful handle closure therefore cannot be promoted to complete twelve-command/twenty-six-observation lifetime qualification. The current result supplies a successful held-Git acquisition/use prefix and failure cleanup, not the entire intended lifecycle.

## Native Job observations and exact failed conjunction

The complete retained native Job record contains:

| Predicate | Actual observation |
|---|---|
| Launch | Started suspended; assigned before resume; root membership confirmed; completion port associated before assignment; prior suspend count 1 |
| Flags | Initial and terminal `0x2000` (`KILL_ON_JOB_CLOSE`); no terminal breakaway |
| Root | Python PID 7412; expected pinned executable image; exit 0 |
| Additional image | PID 6124, `C:\Windows\System32\conhost.exe`, in Job; SHA-256 `4670e2d339001988eace0219462dfaa750418fddf09c004adb28f13aa8a4df2e` |
| Events | NEW 7412 → NEW 6124 → EXIT 7412 → EXIT 6124 → ACTIVE_PROCESS_ZERO |
| Kernel reconciliation | Total 2; creations 2; exits 2; abnormal exits 0; terminal zero event 1; active processes 0 |
| Cleanup | `ROOT_EXITED_AND_JOB_EMPTY`; `cleanup_complete: true`; kernel-terminated processes 0 |
| Timing | 302.4146 ms for this Job observation; 120-second diagnostic timeout configured |
| Capture | Empty worker stdout and stderr retained exactly; no process observation failures |
| Admission | `COMPLETE_UNADMITTED`; `metric_admission: UNADMITTED_DIAGNOSTIC` |

The complete event stream and kernel count agree independently. `sampled_pid_census_complete: false` remains unchanged: opportunistic sampled PID data is not what establishes the complete Job census. The bounded kernel/event reconciliation and held process observations supply the separate evidence. No external broker work outside the Job is proved absent by this mechanism.

At `compile_memory.py` lines 478–485, the first qualifier conjunction has exactly these three mismatches:

| Field | Required | Observed |
|---|---:|---:|
| `kernel_total_processes` | 1 | 2 |
| `creation_event_count` | 1 | 2 |
| `exit_event_count` | 1 | 2 |

All other fields in that initial expected dictionary match. The traceback identifies the failure at line 485, with `ValueError: native Job conjunction incomplete`. The later lines 488–491 also require `len(observed_processes) == 1` and one exact Python root image; that branch was not reached, and its population condition would also be false for the retained two-image list. Merely changing the three counters or dropping the `conhost` record would not be faithful receiving or a complete future qualification change.

### Provenance of the one-process restriction

The exact-one-total and exact-one-image requirements are in the **additional compiler diagnostic**, `compile_memory.py::qualify_job`. The prior independent source review established this definition remained byte-identical from the earlier compile-only packet into R2. The four-file additive host tree does not change the inherited native Job harness or product sources.

The actual harness is the unchanged **25,678-byte** `scripts/r0039-windows-job.py`, SHA-256 `0191eb110977e8aad6c615f7130052c08a38b83297c65748768608a2959ecd8b`; its local full body matches the product pin. Its `reconcile_process_events`, lines 42–88, permits a positive total and requires all created/exited lifetimes to match kernel accounting, exactly one root lifetime, and one final zero event. Its native launch/measurement path, lines 319–409, retains suspended assignment, no breakaway and final active-zero/event checks. Its cleanup, lines 411–478, remains fail closed. Those security/accounting conditions are not equivalent to a one-total-process restriction. The actual two-process record satisfies the harness's observed accounting but fails the added diagnostic qualifier.

Root supplied a freshly received Issue215 body: `/workspace/scratch/097486cde2dd/a4-contract-current-intake-20261122/ISSUE215_BODY.md`, **35,566 bytes**, SHA-256 **`40dbebcc34083f49a49af13e5c6ab50ffe6fbf5a99395d9594926e4668fd09f1`**, with its provider receipt. This reviewer verified the bytes and read the applicable source clauses. Line 340 retains a prospective Windows full-operation envelope of **60,000 ms** and **201,326,592 bytes (192 MiB)** peak aggregate Job committed memory where applicable to the pinned population and verified process/descendant accounting, with no baseline subtraction. It preserves security checks, test deadlines, historical failures and all functional requirements. That clause does not impose one total process.

This provenance supports a narrow finding: **one total process is this diagnostic's extra acceptance assumption, not a requirement established by the inspected native Job mechanism or that Issue215 clause.** The genuine assumption failure remains recorded. The unavailable original A4 R01–R09 body/locator prevents inferring the full original contract from this finding. Under the continuing commission, A4's **64 MiB guard remains separately preserved and unmodified**; the 192 MiB clause is not permission to replace or disable it. No new population, image allowance, launch configuration or original execution is admitted here.

## Ten raw worker-memory observations

All ten files bind PID **7412**, exact sequence/labels, nondecreasing observation timestamps and lifetime working-set peak, and the unchanged reference value 67,108,864 bytes. They report direct `GetProcessMemoryInfo` counters. The source takes no baseline subtraction, no peak reset and no explicit garbage-collection workaround. Every observer/helper overhead within the worker remains in its process lifetime. This measurement is a new controlled compile worker, not the original test suite.

| Seq. | Boundary | Current working set, bytes | Lifetime peak working set, bytes |
|---:|---|---:|---:|
| 1 | Worker before source | 20,099,072 | 20,099,072 |
| 2 | Before compile 1 | 21,508,096 | 21,508,096 |
| 3 | After compile 1 | 27,664,384 | 44,560,384 |
| 4 | Before compile 2 | 27,668,480 | 44,560,384 |
| 5 | After compile 2 | 28,749,824 | 44,859,392 |
| 6 | Before compile 3 | 28,893,184 | 44,859,392 |
| 7 | After compile 3 | 28,643,328 | 44,859,392 |
| 8 | Before compile 4 | 28,782,592 | 44,859,392 |
| 9 | After compile 4 | 28,930,048 | 44,859,392 |
| 10 | Worker after source | 29,229,056 | 44,859,392 |

The final raw lifetime peak is **44,859,392 bytes (42.78125 MiB)**. Current working-set values after compilation are lower than the lifetime peak; that difference is retained, not treated as a reset. The Job separately records **45,473,792 bytes** peak aggregate committed memory and **38,932,480 bytes** peak single-process committed memory. These are different metrics and scopes from worker working set. Their differences do not measure console-host overhead or compiler savings and must not be subtracted to construct a new acceptance number.

The worker compiled each of two exact pinned bodies twice: `claim-run-rotation.py` (291,693 bytes, SHA-256 `9eebc5d5e57b47b0e4b4a2a846de1c0b55407713e14008a6de4d01e7a8c5e19e`) and `rotate-canonical-state.py` (129,959 bytes, SHA-256 `86a9a2a8501aea60f1e333c421e25b19d4e9758a121296fedfa881185de0a5fd`). The exact filename hashes, source pins, occurrence order and four retained code objects agree with the frozen workload. `SOURCE_BEFORE.json`, the runtime guards, and the worker's before/after pinned reads bind those bodies. The product bodies themselves are not copied into this diagnostic artifact; the prior exact-source proof and guarded reads supply that binding, not the reviewer's unrelated current working-copy files.

The native mode loads and constructs the exact adapter but does not install it. Its recorded adapter requests, native compilations and cache hits are all zero; this is consistent with direct native compilation outside the adapter. Product body execution is zero, compile restoration is true, and code equivalence is recorded. The original test file is only source-pinned, not invoked. No original method, original memory guard or A4-07 runs. Evidence: `native/RESULT.json`, `native/native-memory/01.json` through `10.json`, and `compile_memory.py` lines 92–147 and 453–475.

Neither the numerical values below a reference nor the successful worker exit supplies original A4 passage. There is no R2 worker measurement to compare for reuse, no audit-worker refusal evidence, and no completed three-worker experiment. The 192 MiB full-operation envelope is also not qualified by this narrower partial population and failed diagnostic.

## Bounded technical return and evidence limits

The actual result narrows the next engineering question to the diagnostic's launch/population assumption: an exactly observed Python root plus console host was fully accounted inside this Job. A future separately reviewed diagnostic can investigate whether the intended launch should avoid that companion or should explicitly bind and account for a supported companion population. It must preserve the exact source and executable bindings, suspended assignment, no breakaway, full event/kernel agreement, raw aggregate accounting, image receiving and terminal cleanup. This report does not select either change, approve a wildcard population, or authorize another attempt. The existing failed run must remain immutable.

The owner's suggested sequential fresh-process execution of all 28 methods is outside this actual receiving task. This run supplies no evidence that such a population would satisfy the original contract, preserve all required observations, fit the applicable envelopes, or complete the frozen originals. No design, source change, native qualification or original admission for that proposal is issued here.

The reviewer used only file reads, hashes, archive decoding, JSON/AST data inspection and an independent standard-library receiver. No candidate or product module was imported, no local/native/Git process from the candidate was executed, and no source, provider, controller or integration state was modified. Complete failure bytes remain retained. The existing no-replay/original-unaccepted state, unavailable R01–R09 contract, and `A4_07: UNKNOWN_NO_REPLAY` remain unchanged.

**Return to Root:** accept this as authentic receiving of the failed diagnostic and its bounded partial observations. Preserve the additional-population failure, the complete two-process Job record, ten raw native memory samples, successful held-Git prefix and cleanup, and all missing final/stage evidence. **New original awards: none.**
