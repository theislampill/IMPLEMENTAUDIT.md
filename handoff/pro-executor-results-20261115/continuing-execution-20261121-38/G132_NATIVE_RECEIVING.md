# G132 diagnostic 04 — independent receiving of actual native failure

## Disposition

**PASS_RECEIVED_AUTHENTIC_NATIVE_FAILURE.** The retained provider, source, artifact, runtime, native-return, and command-custody evidence agree. The diagnostic itself **failed** before the new capture-bound measurement was reached. This PASS concerns receiving integrity only; it is not source admission, runtime qualification, a successful diagnostic, original credit, or closure.

Actual run **44963085468**, attempt **1**, job **137025986456**, completed with provider conclusion **failure** and native observer exit **2**. Its first standalone-source clone returned **128** and recorded `fatal: fetch-pack: invalid index-pack output`. The command's direct child was reaped, but **`owned_group_absent=false`**. The evidence does not classify group members as living, terminated, or zombies and does not establish the clone/index-pack root cause.

Reviewer: `/root/independent_review`; authority **NONE**. Root supplied currentness `fbef7e/0`, G0044 receipt `3fb3e2d80b1575b3a4ec28cc196957f9ce498523`. This ordinary independent receiving performed no candidate/product/original execution, Git operation, provider call, controller operation, retry, or source mutation. Root retains adjudication and publication.

## Exact identity and artifacts

| Binding | Independently received value |
|---|---|
| Operation | `G132_ENGINE_SOURCE_OBSERVE_20261121_04_CAPTURE_BOUND` |
| Branch | `pro/dg16-g132-engine-source-observe-20261121-04` |
| Diagnostic commit | `5f0dce5e1756be3d9bf964d83de45587749a31a4` |
| Complete diagnostic tree | `baffbae6d7a19e289db100233704df2a0e721914` |
| Sole parent | `f75533f95f0d099c87e7a04beb11b0a25628acdc` |
| Raw packet seal | 3,865 bytes; SHA256 `0dd20543c17f70593bd024afcdd7f07e827eae1d5422ed94fc6f480c4cf9a4bb` |
| Raw payload inventory | **21 files / 268,924 bytes**, all exact |
| Artifact | **14730158293**, `g132-engine-source-44963085468-1` |
| Artifact ZIP | **9,555 bytes**, SHA256 `2790146432e27e75a0bc6dd63a483fb6a9311848fa7c092724ca657e8e2cea41` |
| Actual observation | **85,125 bytes**, SHA256 `2cd25579c192d8dddf27fd00e6071f0c75c6e27c944d4d8f957dad289ac93796` |

Raw evidence resides at `/workspace/scratch/097486cde2dd/g132-native-44963085468`.

The provider's run, discovery, job, commit, branch, artifact metadata, and job logs agree on this run/attempt/branch/commit. The run has no associated pull request. Checkout succeeded, the observation step failed, and artifact retention succeeded. The exact three provider file readbacks decode to the reviewed workflow, observer and Engine map; their blob identities and full bytes agree with the frozen candidate. The actual observer also records its own exact 20,455-byte body and SHA256 `49b7ea3deea034210964519c06cab344828194af147c0994c3f8831cb2816413`.

The included source candidate seal matches `ed10206609b732337d8e2faed40df8db68dd7fd08311a2c619bae1569726a2b2`; the independent source-review seal matches `33a80165f5a316479e34d7b5bba04f862ad280a34aea6ae40c0d90e72e268381`. All retained candidate and source-review payloads were rehashed as data and remain exact. The review's compile-only compatibility result is preserved as historical source evidence; this actual operation did not reach the new traceback receiver.

The ZIP has exactly four members: `OBSERVATION.json`, `STDERR.raw`, `NATIVE_EXIT_STATUS.raw`, and `RETURN.json`. Their complete bytes and CRC reads match the retained files. The provider digest matches the ZIP. The return receipt binds all three native streams/status files, preserves exit **2**, and declares no native admission or original awards. Observer stderr is empty; the clone error is retained inside the structured observation. Job logs independently corroborate the image, diagnostic SHA, exit 2, artifact ID, size, and ZIP digest. The complete raw inventory was rehashed again at closing.

## Actual reached phase and host observations

The actual context is the exact branch-04 push, attempt 1, job `observe`, workflow/source SHA pair, Ubuntu24 image **20261116.376.1**, and GitHub-hosted runner. The observer records UID/EUID/GID/EGID **0**, `/usr/bin/python3.12`, version **3.12.3**, PID **2413**, PPID **2412**, and process start ticks **13169**. These are retained observations, not a new live process inspection.

The diagnostic-checkout Engine loaded its exact **13-member** map. This is the initial Engine from the reviewed diagnostic checkout, not the later Engine from a successfully prepared standalone source.

Before clone, `/usr/bin/git` matched the exact **Git08ca** pin: 4,640,384 bytes, mode 0755, SHA256 `08ca4d2ee4d8915e86f1faaa52603752507c57af1d16d451dec9992bc9b6d801`. All **17** selected Git rows independently match their recorded expected pin fields; the unchanged Git-input validator is the only reached named gate and records PASS. This remains **initial-only evidence**: no final Git bookend or source-loading bookend exists.

The broader selected host inputs remain unqualified. Independent comparison of expected and observed pin fields confirms four mismatches: `/etc/ld.so.cache`, libc, the selected dynamic loader, and libpthread. The actual NSS check records a files-only refusal, full startup remains mismatched, and `/usr/bin/bwrap` is missing. No pin, launcher, policy, or private input was changed by this operation. These observations do not identify the clone failure's cause.

## First clone and custody record

Exactly **one Python-observed Git launch** is retained. It has the reviewed fixed Git prefix, cleared credential/configuration environment, public source URL, and the intended clone flags `--no-local --no-hardlinks --no-checkout`. It targets the new disposable source directory. The record still contains only `commands` and `expected_commit`; the source-preparation routine never returned a completed standalone source tuple.

| Actual field | Retained value and interpretation |
|---|---|
| Child PID | 2415; historical direct-child record |
| Return code | **128** |
| Elapsed time | **10.19336235099999 seconds** |
| Process creation | Handle returned |
| `command_received` | **false** |
| `wait_reaped` | **true**, for the direct child |
| `owned_group_absent` | **false**; group absence was not established |
| Command descriptor restoration | true |
| Observer descriptor restoration | true |
| Pipe EOF | true for both stdout and stderr |
| Output overflow / timeout | false / false |
| Recorded exception / cleanup errors | null / empty list |
| Stdout | 0 bytes; empty-stream SHA256 verified |
| Stderr | 103 bytes; complete retained excerpt, SHA256 `2c31c4d0a51e6e2798ee183fd15280c0eea54ee8426587b9bfcad337b3a53860` |

Because the complete stderr is shorter than the excerpt limit, its full 103 bytes were reconstructed from the retained text and checked against the stream digest. It contains the clone destination announcement followed by the exact `fetch-pack: invalid index-pack output` fatal line. Both pipe EOF and direct-child reaping agree with the recorded command completion; neither proves process-group absence.

The unchanged `hosted_git` owner at `scripts/qualify-work-graph-c5-setup.py:203–244` kills its owned group only while the direct child's return code is still unset. On the normal wait path, the child has already been reaped before the final group-absence observation. This operation therefore provides a **genuine observed failure of the group-absence predicate**, not a census of surviving members or a diagnosis of their states. The direct child's nonzero exit and the false group-absence predicate both prevent `command_received` from becoming true.

No causal claim follows about memory limits, file limits, network transport, transience, or why index-pack failed. No later action is authorized here. Any separate cleanup repair must preserve safe ownership of the process group; simply signaling a numeric PGID after the child has been reaped could address a reusable identity and is not supported by this receiving.

## Explicitly unreached and unqualified

The exact outer result is `REFUSED` at **`standalone_source_preparation`**, with `ValueError` and reason `hosted Git refused or ordinary command custody incomplete`. The full source workflow stopped on the first clone; no later source-preparation command is recorded.

The following are absent and must remain unreached:

- A completed exact standalone f755 checkout, clean/full-object tuple, or independent identity from that checkout.
- The actual-checkout Engine map.
- Complete source capture, its projection/state/object counts, or its digest.
- A capture-bound exception observation, its operands, or its failing path.
- Namespace, producer-contract, and captured-HEAD gates.
- Final Git body/bookend equality and final source-loading bookends.

The new diagnostic wrapper therefore never received a product capture exception. Operation 03's capture-bound cause remains unknown; this operation supplies no new operand evidence for it. Initial source constants in the report are the requested source identity, not proof that the failed clone produced and qualified that source.

The actual result retains `authority: NONE`, `overall_admission: UNQUALIFIED`, false original/session/native/private-input/provider/launcher/policy declarations, zero provider imports, no original awards, and no automatic retry. Original G132 run 44888568054 remains spent. No protected grant, replay, original award, or closure is issued by this receiver.

## Receiving method and handoff

`RECEIVE.py` reads only retained files. It checks the complete raw inventory, source/review bindings, actual provider bodies, artifact and return hashes, context/runtime, Engine and selected pin rows, exact single-command record and stream digests, and all later-field absences. It imports no candidate or product code and invokes no subprocess, Git, network, provider, or controller operation. Its successful data-only receiving run is **`415631/0`**; `MECHANICAL_RECEIVING.json` preserves the 424 checks, exact actual failure fields, and evidence limits.

**No receiving gap remains for this exact failure.** Root may adjudicate and publish this immutable failure evidence. No retry or cause-specific repair is implied by the receiving PASS.
