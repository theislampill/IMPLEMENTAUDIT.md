# DG18 installed-current candidate: independent source review

Disposition: **GAP-REVISE — source/static scope only.** Two concrete retention gaps must be corrected before this operation is published. No product-semantic repair, new certificate scheme or additional runtime test programme is requested.

Reviewer: `/root/dg17_recovery`, distinct from the DG18 author and Root publisher. This reviewer authored a separate DG17 ordinary consumer adapter, but did not author or edit this DG18 candidate. The review received this exact frozen DG18 packet and checked its own source, archives and consumers. No source test, installed runtime, model/native event, protected operation or replay was executed. This report grants no operation, receiving or original-acceptance authority.

## Frozen identity

Worktree: `/workspace/scratch/7fbb79f74aa4/recovery/dg18-installed`.

Base: `080cc0e29bd6382b0c31f3f69e9ad2f8d42991b2`, tree `3a00fcab84741877e66479c610a6f6c723f424ba`. The only candidate changes are the existing workflow and the new repo-only operation pair below. The file sizes and SHA-256 values were independently recomputed and equal `INSTALLED_CANDIDATE_CHECKS.json`.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `.github/workflows/dg18-source-qualification.yml` | 11127 | `763eeaaac7f111e2b9bde637af2fe241be2225b1c8460a6dbf1fdc2870106b3d` |
| `handoff/pro-executor-results-20261115/dg18-installed-current/qualify.py` | 18403 | `ab511a1bbba7ef673fff1f5905f8163bbfcc664c49f13254ff90512352c11746` |
| `handoff/pro-executor-results-20261115/dg18-installed-current/README.md` | 3479 | `c067406463d6ef17500367f0771cce0190f6c8c589e16b014d2e7e7e116a8006` |

## Findings requiring revision

### R1 — Hidden claim/controller evidence is excluded by the upload action

`qualify.py` copies each successful actual run root into `evidence/<route>-runtime` at line 253. The run population includes `.claimed` and `.controller`, and the task/currentness evidence binds those files. The workflow's final upload step supplies only the `evidence/**` path and does not enable hidden-file inclusion.

The exact pinned [actions/upload-artifact action definition](https://github.com/actions/upload-artifact/blob/ea165f8d65b6e75b540449e92b4886f43607fa02/action.yml) was read through GitHub. Its `include-hidden-files` input defaults to `false`. Therefore those raw claim/controller files are omitted even on a successful job. Aggregate hashes and controller readback do not reconstruct their original bytes for independent receiving.

Required correction: include the selected hidden runtime files within the existing bounded evidence upload, for example by setting `include-hidden-files: true` on that evidence-only path. Do not broaden the upload to user homes, the checkout's `.git` directory, build environments or unrelated files.

### R2 — Failure does not retain the promised actual partial task state

`qualify.py` writes `<route>-TASK.json` only after activation at lines 213–215. Raw task files are copied only after all of that route's consuming operations succeed at line 253. The exception handler at lines 288–293 saves failure metadata but does not copy any selected partial task root. The upload covers `evidence/**`; the actual task roots are under `<output>/<route>/subject/.IMPLEMENTAUDIT/runs/...` and therefore lie outside that upload.

A failure after claim, during authoring/inspection/activation, during the separate reads, or before a route's final success copy consequently retains command output and failure metadata but loses the actual partial task files when the runner disappears. Earlier prepared routes also remain uncaptured if a later route fails during `prepare`. This contradicts README's claim that failure retains actual partial task state and weakens diagnosis of precisely the interrupted ordinary operation being added.

Required correction: retain each already selected fresh task's actual partial records on failure, with its real route/root identity recorded as soon as the owner returns it. A small bounded snapshot in the existing adapter is sufficient. Preserve missing/incomplete files as such; do not synthesize successful state, re-run an owner, discover an unrelated root, or replace the first failure with a snapshot success. Mark any failed snapshot explicitly. No new receipt or authority scheme is needed.

## Checks that support the proposed operation

### Exact retained package reuse

The actual transport was read without extraction or execution. Its 5,939,419 bytes match SHA-256 `7ce615a41b914afd7ba779482658b0e02a991bb747db0457dc7e6d527b4c7d49`; it has the expected six unique members and passes ZIP CRC verification.

| Archive | Actual bytes | SHA-256 | Headroom under 589824 | Inventory files |
| --- | ---: | --- | ---: | ---: |
| Canonical plugin | 586931 | `32f63a1759ac3852ed51ad20fea87e2ed524a14322d9d97210d4b7345cb81556` | 2893 | 75 |
| Standalone compatibility | 582329 | `4ad29f2eccdaa4133f4d0f0f852b4aa4dcfb6a57b9a337b3a0e727cfb7496dfb` | 7495 | 72 |

Both embedded inventories bind clean source `775d6a0add0a1edcbc7f6cf5ccd68d350757fe8a`, tree `66607502c26f533416aa9cc00b3b5728e1e0e11e`. Every inventory member's byte length and digest matches the actual ZIP member, and both archives pass CRC and exact inventory-population checks. The packaged `claim-run.sh`, `claim-run-rotation.py`, `read-canonical-pair.py` and `validate-run-root.sh` match their exact source Git blobs in both layouts. The operation's mandatory existing package verifier additionally checks complete source projection, metadata, modes, budgets and clean-source identity before installation. No rebuild or dependency installation is selected.

### Existing four installation routes

The route mapping is correct: canonical Codex and Claude use `install-plugin-from-release.sh` with a fresh explicit host root and required sentinel; standalone Codex uses `--codex-home`; standalone Claude uses `--claude-skills-dir`. None falls back to a real user home. Canonical helpers are selected from `skills/implementaudit/scripts`; standalone helpers are selected from the flattened `scripts` directory. The existing installers explicitly restore archive modes, so the workflow's preparation `umask 077` does not defeat declared installed file-mode parity.

The operation compares complete installed populations, sizes, hashes and modes with the appropriate archive immediately after installation and after consumption. The actual archive verifier's source identity check prevents merely relabeling an older archive as current.

### Actual task and currentness composition

The claim, initialization inspection, expected-token activation, first `G0001/new-session` resume, receipt verification, currentness requirement and controller readback forms match the exact installed owner interfaces. The public installed `claim-run.sh` remains the execution path; the adapter does not call the rotation implementation directly or bypass interpreter selection. The pinned companion and all relevant source helpers/templates are unchanged between the exact archive source and the review base.

The existing author writes a fresh actual checkpoint from exact source templates without its optional activation flags. All owner decisions use the installed copy. Its authored epoch row binds the new disposable subject's real HEAD/tree and claim time. Initial activation establishes eligibility only; the subsequent normal owner calls establish actual currentness. This is first-session initialization, so an invented predecessor invalidation is neither needed nor asserted.

Every route's STATE is read in the `read-state` host action; every route's ROADMAP is read in the following separate `read-roadmap` host action. No action batches STATE with ROADMAP. The adapter compares record populations before and after those reads, verifies the actual receipt, records its raw Git object and controller, and checks unchanged refs and task files during readback. The proposed output does not claim that this source/currentness leg provides N1, authentic compaction, OR, accepting C02 or W-FULL evidence.

### Hosted execution scope

The packet checkout is fixed to `github.sha`; the product checkout is fixed to source `775d6a0a`. Both disable persisted checkout credentials, submodules and LFS. The workflow has `contents: read`; existing permissions/concurrency and both pre-existing jobs are byte-equivalent as parsed YAML. Their original branch guards exclude the new installed-current branch. The added job has an exact repository, push-event, branch and first-attempt guard.

Commands use an explicit minimal child environment and standard system Python/Bash/Git. The observed root-owned, nonwritable tool ancestry is required, and the existing product's physical interpreter admission remains in force. No credential read, model CLI, native hook, protected consumer, original receipt replay or external publication appears in the new operation. New Git seed commits are confined to fresh disposable subjects. Timeouts fail the operation and do not create currentness or acceptance.

### Local review actions and limits

This reviewer independently checked the frozen hashes, parsed the candidate Python AST and YAML, syntax-checked the four Bash step bodies without executing them, compared old jobs/permissions/concurrency against the base, read the actual package bytes and inventories, and traced existing source ownership/CLI contracts. No package build, source test, installer invocation, claim/init/resume invocation or host effect was performed. These are static/read-only findings; hosted success and independent receiving remain future evidence.

After R1/R2 are corrected, provide the new exact hashes for a focused review of those changed paths. Repeating the accepted source suite, rebuilding these archives or changing the product is unnecessary for these retention defects.
