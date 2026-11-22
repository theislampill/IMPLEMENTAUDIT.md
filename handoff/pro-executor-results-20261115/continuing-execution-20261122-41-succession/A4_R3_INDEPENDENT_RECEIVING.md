# A4 R3 independent evidence receiving

Status: **RECEIVING_COMPLETE_AT_BOUNDED_DIAGNOSTIC_SCOPE; Root adjudication pending.**

Repository: `theislampill/IMPLEMENTAUDIT.md`. Collection date: 2026-11-22 UTC.

## Recommendation and authority ceiling

Recommend that Root receive the existing R3 run as authentic, internally consistent **separate native compiler diagnostic evidence**, including its observed process/Job measurements and bounded compiler-reuse/audit controls. The exact provider ZIP, inner ZIP, manifest members, source files, provider run/job records, decoded job log, and issue contract text have been retained and checked.

This does **not** recommend an original A4 award, original 28-method safety/custody acceptance, a 64 MiB original-guard award, whole-operation 192 MiB/60,000 ms qualification, or a demonstrated reduction in the original lifetime working-set peak. Original A4 remains unaccepted. A4-07 remains `UNKNOWN_NO_REPLAY`; frozen R01–R09 contract availability remains false at this received scope.

This lane holds no Root, lifecycle, release, closure, publication, controller, or original-A4 authority. It is factual receiving with a bounded recommendation, not a formal `audit-assess` disposition: no immutable digest-bound governor route envelope was supplied for that internal skill. Root must independently inspect and adjudicate this result. No workflow, compiler diagnostic, original method, or historical A4 operation was launched or rerun by this receiver. No repository source/controller/publication change was made.

## Exact provider and source identities

| Object | Received identity |
|---|---|
| Ordinary GitHub Actions run | [44969346074](https://github.com/theislampill/IMPLEMENTAUDIT.md/actions/runs/44969346074), attempt 1, push, completed / success |
| Workflow | `.github/workflows/dg18-a4-compiler-memory-r3.yml`, workflow ID `426427637`, run number 1 |
| Host commit | `d258984cb3dad509b07623e797a1669ff4136f00` |
| Host tree | `77a6249eef25d1dc78aaa0fc519283d57220daa1` |
| Host branch | `pro/dg18-a4-compiler-memory-51416-20261122-03` |
| Product source / sole host parent | `51416b2f156b341c4a5f09029e2c6ceb5b30b1e7` |
| Product tree | `9c3913ceaa95f3f36b0377fe2dba4a302afcba89` |
| Provider actor / triggering actor | `theislampill`, account ID `266501826` |
| Job | [137045470127](https://github.com/theislampill/IMPLEMENTAUDIT.md/actions/runs/44969346074/job/137045470127), `compile-only-native-diagnostic`, completed / success |
| Job time | 2026-11-22 01:00:17–01:00:44 UTC; run created 01:00:15, updated 01:00:45 UTC |
| Runner | `GitHub Actions 1000006249`; Windows Server 2022 10.0.20348; image `windows-2022` version `20261116.370.1`; Python 3.12.10 x64 |
| Artifact | `14732334790`, `dg18-a4-compiler-memory-r3-44969346074-1`, created 01:00:39 UTC, expires 2026-11-29 01:00:38 UTC |
| In-artifact receiver process | PID `1964`; this is the diagnostic's own coordinator, distinct from the present independent receiver |

The raw attempt-1 jobs endpoint reports `total_count=1`; the raw artifacts endpoint reports `total_count=1`. Both entire populations were received, avoiding the normalized wrappers' first-page ambiguity. Git commit API records independently confirm the host tree, sole product parent, and product tree. The job log independently records both exact checkout refs and the actual execute/finalize/upload steps. The current result/publication branch was not treated as this diagnostic's source identity.

Primary provenance is the connected GitHub plugin: `github_fetch`, `github_fetch_issue`, `github_fetch_issue_comments`, `github_fetch_workflow_run_jobs`, `github_fetch_workflow_run_artifacts`, `github_fetch_workflow_job_logs`, `github_fetch_file`, and `github_download_workflow_artifact`. Provider envelopes and retrieval timestamps are retained in `*.provider.json`. The decoded log preserves the provider-returned UTF-8 BOM and CRLF bytes; this is not a claim of receiving its original compressed HTTP transport bytes.

## Artifact byte custody and deterministic receiving

The download tool returned a reusable ZIP file reference, which was successfully consumed through its temporary HTTPS URL. HTTP status was 200. The file is a valid ZIP and its locally computed SHA-256 equals GitHub's artifact digest.

| Retained object | Bytes | SHA-256 |
|---|---:|---|
| Provider artifact ZIP | 61,909 | `9a70879c3780da482f965707ee9802714f0b317fabc12824f5458c04dba7b7c8` |
| Inner `DIAGNOSTIC.zip` | 128,167 | `868be35c828bf313c01d831f0b41f7cf751c4015fe92266f937eb79302ebd672` |
| `ZIP_RECEIPT.json` | 1,005 | `1c9c83bf553d06f7949345c9301b2f72f63e4ca53b7d2351303a7aba50eaa407` |
| `MANIFEST.json` | 13,986 | `60b249c946d67f1c8d7179bca5b463b983fb1f1e762ab1f97823a7426b84747f` |
| Diagnostic `RESULT.json` | 2,124 | `8a8ff9f08e219fff89a976fd4cd589d9df1de7b02471d124b33b44d0e9bd6316` |
| Decoded job log | 31,158 | `7c7399d242421e62f5d2d9b5274ac1b504186c0646c53eeb3cb210836fa5a8c1` |

The outer ZIP has exactly `DIAGNOSTIC.zip` and `ZIP_RECEIPT.json`. The inner ZIP has 84 unique members: the 83 declared manifest members, totaling 885,116 bytes, plus the manifest itself. CRCs, extracted bytes, every declared member size, and every declared member SHA-256 match; no missing or undeclared inner evidence member was found. Both source snapshots are byte-identical.

All four diagnostic helpers were retrieved at the exact host commit and all four product inputs at the exact product commit. Recomputed Git blob OIDs match the provider's OIDs. Their SHA-256s match the artifact/workflow pins. Full mappings and byte counts are in `source-receiving.json`. These are received source files, not executed source. The 5,603-byte workflow has SHA-256 `d9aef9eddcacb401f948775e081c4f0c34618c84b41e10bdf3850c78c91df42c` and Git blob OID `0f5a0cc55688ac45d397aa369556997945315cf3`.

`verify_received_evidence.py` performs read-only deterministic checks on this retained package and writes `receiving-verification.json`. Its run exited 0 with **62/62 receiving checks verified**. It does not import or execute any received diagnostic/product file, launch a worker, contact a provider, or change a repository. `manifest-verification.json` separately records each declared member's local hash check. These checks establish this receiving result; they are not new original acceptance tests.

## Observed measurements and their meaning

| Worker mode | Python PID / conhost PID | Job elapsed ms | Peak aggregate Job commit, bytes | Peak single-process commit, bytes | Last retained lifetime working-set peak, bytes |
|---|---|---:|---:|---:|---:|
| `native` | 3104 / 6088 | 290.1076 | 45,367,296 | 38,858,752 | 44,703,744 |
| `r2` reuse | 3236 / 8176 | 197.5228 | 44,986,368 | 38,449,152 | 44,855,296 |
| `audit` controls | 6428 / 3924 | 93.6593 | 21,192,704 | 14,659,584 | Not recorded by that worker |

The reuse worker's last retained lifetime working-set peak is **151,552 bytes higher** than native. Its aggregate Job committed-memory peak is 380,928 bytes lower. These are different metrics; the latter cannot be substituted for the former. This is one bounded run and establishes neither a general memory improvement nor a performance prediction for original A4.

The working-set column comes from the tenth retained `GetProcessMemoryInfo` lifetime-peak reading (`worker-after-source`), before final result-file writing and process termination. It is not a claimed post-exit reading of the original suite's full process lifetime. There are ten ordered observations in each native/reuse worker, with observer overhead included inside that worker and no baseline subtraction.

The Job readings cover each compiler/audit worker and its conhost until the Job is empty. The coordinator/harness is explicitly excluded (`harness_included=false`). They are marked `UNADMITTED_DIAGNOSTIC`, with `numeric_performance_admission=false`. They cannot establish a whole-operation envelope even though their individual numbers are below that envelope.

Each Job records suspended creation, assignment before resume, completion-port association before assignment, root membership, two unique process creation/exit lifetimes reconciled with `kernel_total_processes=2`, a final `ACTIVE_PROCESS_ZERO`, no abnormal exits, no terminated processes, no process observation failures, no breakaway flags, zero active processes at terminal readback, and completed cleanup. The observed process paths and hashes match the exact Python image and separately held conhost image. `sampled_pid_census_complete=false` remains explicitly retained: completeness here rests on the reconciled completion-event/kernel population, not a claim that a sampled PID list is a complete census. The source itself limits this to work inside that Job and does not prove absence of external broker work.

The diagnostic retained 26 Git custody observations across 12 Git calls and 8 conhost custody observations across the three worker boundaries. Initial and terminal held hashes agree; comparisons report exact metadata matches; errors are empty; all held file/directory handles were closed after terminal rehash. The exact Git four-name set and the conhost inventory are preserved. This is the narrow fresh observed-tool admission used by this diagnostic, not an alteration of original aggregate Job accounting.

The `native` and `r2` workers each make four compile requests: twice each for the exact two product source bodies. The reuse mode reports two native compilations and two cache hits, retains four result references, preserves filenames, restores native `compile`, and does not cache module instances or execute product bodies. The audit worker records three construction refusals, one installation refusal, and native/cache-hit/cache-miss audit refusal controls with four hook events. These are compile-only controls. Reported `code_equivalence=true` is the source's within-worker duplicate-result condition; no original functional execution or whole-suite equivalence follows.

## Original #215 contract received

The actual [issue #215](https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/215) body is retained as `issue-215-body.md`: 35,566 UTF-8 bytes, SHA-256 `40dbebcc34083f49a49af13e5c6ab50ffe6fbf5a99395d9594926e4668fd09f1`. The provider reports OPEN, updated 2026-10-23 07:25:46 UTC, with one comment. Its full [normative criterion-5 comment 5638756120](https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/215#issuecomment-5638756120) is retained: 4,943 bytes, SHA-256 `3774677f6aa3ad2676d8afbded7dce277f5e561a8bf492200418a0495393caaf`. These are exact current provider-returned body bytes, not an inferred historical issue revision.

Criterion 4 retains interrupted-write/corrupt-archive/stale-receipt/concurrency/wrong-controller-candidate/path-traversal/symlink/Windows-POSIX safety and recoverable-preimage requirements. All fourteen criteria, the criterion-5 amendment, and C02 remain required. The amended cold receiving duties preserve authentic occurrences, cutoff/coverage, selected prior/retry identities, unresolved compaction obligations, TC06 continuing duties, and TC11 historical scope. A diagnostic does not complete them.

The body preserves the separate prospective Windows full-operation envelope: **60,000 ms and 201,326,592 bytes (192 MiB) peak aggregate Job committed memory**, applicable only to the pinned population with verified process/descendant accounting and zero baseline subtraction. It preserves original calibration/cost failures and original functionality. This cannot be used to relax the diagnostic's retained original 67,108,864-byte lifetime-process-peak reference guard. The diagnostic explicitly says that guard was neither changed nor invoked.

## Absences and next Root decision

- Original method executions, original guard invocations, and product body executions are all zero. The original 28-method matrix is not exercised by this run. The separately hash-checked product `windows_custody_test.py` has 18 `test_` methods; this one unchanged input is not a reconstructed original 28-method denominator and was not executed here.
- The frozen R01–R09 receiving-contract body/locator is not present in the received diagnostic, issue body/comment, or exact source files inspected. This is a bounded absence claim, not proof that no historical copy exists elsewhere. The retained `frozen_R01_R09_contract_available=false` remains truthful.
- A proposed 28-fresh-interpreter route cannot obtain original-equivalence credit from this compiler diagnostic or from its per-worker numbers. It requires its own original-contract/owner/equivalence proof before original acceptance could be considered.
- Earlier failed diagnostics and historical A4-07 were not replayed or reclassified. `historical_R3_peak=UNKNOWN` and `A4_07=UNKNOWN_NO_REPLAY` are preserved exactly; the known current R3 diagnostic measurements do not fill that separately labeled historical unknown.
- Root's earlier receiving/publication state, results40, and any current results-branch integration remain Root-owned reconciliation. This report does not infer that publication or acceptance already occurred.

The next decision is Root's independent bounded acceptance/rejection of this diagnostic receiving package and whether to publish these findings at that exact scope. It is not a decision to execute or award original A4.

## Retained evidence locations

Evidence root: `/workspace/scratch/75de74f83f5c/recovery/a4/`.

Canonical lane report: `/workspace/scratch/75de74f83f5c/recovery/lanes/a4-receiving.md`; identical package copy: `RECEIVING_REPORT.md`.

Key files are `receiving-verification.json`, `verify_received_evidence.py`, `manifest-verification.json`, `source-receiving.json`, `artifact-download-receipt.json`, the original provider artifact ZIP, `artifact/DIAGNOSTIC.zip`, `artifact/ZIP_RECEIPT.json`, `diagnostic/`, `source/`, the job log, original issue body/comment, and provider envelopes. `PUBLICATION_MANIFEST.json` enumerates the publication-ready files with exact bytes and hashes.

Temporary signed download URLs are omitted from all publication-ready files. The unmodified transport response is isolated under `transport-private/`, excluded from the publication manifest and evidence bundle; `artifact-14732334790-download.public.json` preserves its safe file-reference/artifact provenance. This omission does not alter the raw downloaded ZIP, inner bytes, authenticated log, source, or provider run/job/artifact records.
