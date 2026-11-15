# Independent actual G221 prelaunch host observation receiving

Report state: FINAL

Disposition: PASS_OBSERVATION_RECEIVING_ONLY.

Authority: NONE. This report receives one actual ordinary prelaunch observation. It grants no protected launch, native/model operation, same-job earned qualification, currentness, future G221 acceptance, publication, merge, release, or closure authority.

## Actual outcome

The actual provider run, its sole job, and all six expected job steps completed successfully. The unique runtime observation is `SELECTED_TUPLE_MATCH_OBSERVED`, with no first refusal or closing refusal and successful closing reads of all ten executed source members. Independent receiving reproduced the complete actual tuple through the unchanged original `current_host.target_host` and `evidence_io.encode`, matching exactly the second original `SELECTED_HOSTS` entry.

The newly downloaded artifact's exact ZIP bytes match both the provider digest and the upload log. Its `OBSERVATION.json` is byte-identical to the unique actual log record after base64 decoding; the canonical JSON, final LF, digest, and sidecar all agree. No failed receiving predicate remains.

## Receiver and independence

- Receiver: `/root/g221_host_inventory_review`, distinct from the source author and Root publisher.
- Requested model: GPT-6 Astra Pro. Actual host/developer self-identification: GPT-6 Astra Pro; no separate runtime model attestation is exposed.
- Inheritance: continuing dispatched child; this receiver did not select a model override. Parent fork/model parameters are not independently visible.
- The same agent previously reviewed this wrapper's source. That source-only report is deliberately used as the immutable review binding and remains unchanged; this receiving activity is distinct from source review and does not enlarge its authority.
- This receiver independently retrieved run/job/ref/commit/tree metadata, job logs, and the one new artifact. Root did not fetch the log or download the artifact. Root later reported its own matching terminal run-API read; the receiver's independent terminal and artifact checks had already been performed.
- The assigned receiving resource was read before acquisition. Writes are confined to the declared new evidence directory and this report. No source, index, HEAD, branch, Root state, publication-action record, or earlier evidence was modified.

## Exact provider and source identities

| Item | Actual received identity |
|---|---|
| Repository | `theislampill/IMPLEMENTAUDIT.md` (provider repository ID `1243475954`) |
| Ref | `refs/heads/engineering/pro-executor-g221-host-inventory-20261115` |
| Remote execution commit | `e08007f7ebefa5e27a0a264b2f7630dee4e7cba4` |
| Sole remote parent | `060902121a45b180853e630891caa5e6c9d2f704` |
| Published tree | `8aa5f85404c894a1ecc556ecedac8ad40986e293` |
| Exact local carrier with the same tree | `b49d09fb42f1a3e4b7bec6fed3894d5d7c13698b` |
| Independently reviewed source candidate | `cd1a84fbcb39650864c4b8460309025424e2d565` |
| Reviewed source tree | `3531df3b34d5008f78030b0e40308d3da48ad8bf` |
| Frozen source-review SHA-256 | `a2f3398867557db71c35d6ce503f9a7768efa60b858d81615486c68e8fef89f2` |
| Workflow | `.github/workflows/dg16-g221-host-inventory.yml` |
| Provider workflow ID | `418981049` |
| Run / attempt / event | `43694426207` / `1` / `push` |
| Job | `132751711186`, name `observe` |
| Provider runner | `1000006032`, `GitHub Actions 1000006032`, group `GitHub Actions`, label `ubuntu-26.04` |
| Run created / updated | `2026-11-15T08:25:20Z` / `2026-11-15T08:25:30Z` |
| Actual job interval | `2026-11-15T08:25:22Z`–`2026-11-15T08:25:29Z` |
| Actual observation log timestamp | `2026-11-15T08:25:26.8517777Z` |
| Artifact | `14153163002`, `dg16-g221-prelaunch-host-inventory-43694426207-1` |
| Artifact created / expires | `2026-11-15T08:25:27Z` / `2026-11-22T08:25:27Z` |

Provider references: [run](https://github.com/theislampill/IMPLEMENTAUDIT.md/actions/runs/43694426207), [job](https://github.com/theislampill/IMPLEMENTAUDIT.md/actions/runs/43694426207/job/132751711186), and [execution commit](https://github.com/theislampill/IMPLEMENTAUDIT.md/commit/e08007f7ebefa5e27a0a264b2f7630dee4e7cba4). These public URLs are identifiers; the locally retained exact responses supply this receiving record.

The current provider ref, run, job, artifact workflow-run metadata, actual observation provider fields, and checkout log all name the same execution commit and branch. The log records `G221_PUSH_CREATED: true` and `G221_PUSH_DELETED: false`. Run and job metadata both specify attempt 1. The job log independently records the pinned checkout and upload action revisions from the reviewed workflow. Provider job metadata shows only the six expected checkout/observe/upload/cleanup steps, all successful.

## Complete actual selected host

| Host field | Actual observation |
|---|---|
| OS | Ubuntu, `VERSION_ID=26.04` |
| Architecture | `x86_64` |
| ImageOS | `ubuntu26` |
| ImageVersion | `20261111.196.1` |
| Kernel | `7.0.0-1019-azure` |
| Python version | `[3, 14, 4]` |
| UID | `1001` |
| Credentials | `uid=1001`, `euid=1001`, `suid=1001`, `gid=1001`, `egid=1001`, `sgid=1001` |
| Boot-identity SHA-256 | `94860c626b9fa532258487605c004b90ee18ca85f8bfa4a4b210ce554d3715ab` |

| Tool | Requested path | Canonical path | Bytes | SHA-256 |
|---|---|---|---:|---|
| bwrap | `/usr/bin/bwrap` | `/usr/bin/bwrap` | 80424 | `a85b0ff8664c52ab923e0daf7e20cbc394272cd3831cc492ab144105d8091361` |
| bash | `/usr/bin/bash` | `/usr/bin/bash` | 1540520 | `450c68376d14e5040d36cce58605c35b2211d244f3079297440dc9d602ee4994` |
| git | `/usr/bin/git` | `/usr/bin/git` | 4771424 | `8fb7c4c2a0e5ec847626098c2a375ff01d6a9e5f81352e3ae56f30b41ec850cd` |
| python3 | `/usr/bin/python3` | `/usr/bin/python3.14` | 7468968 | `be9a2a5eada8c89c1c399fdfb8397179e877c20d8db0739c802f726d4d0e69fd` |

For each of the four tools, the actual record has `available=true`, `root_owned_nonwritable_chain=true`, and `setid_or_file_capabilities=false`. The tool-path map agrees with these canonical paths. No credential or bwrap field was filled with an invented default. The bwrap descriptor is a byte/custody observation; the observer did not execute bwrap.

The actual selected-tuple SHA-256 is `335fcf27cd85dcb0048883129acaf858a79ad4c2a0dcbe42efa5476b88b5ae2c`. The original two-candidate population SHA-256 is `5f079c8b22fb560d86737f152cd1a1b1f7719361659768f5c0a07096aef4ae09`. Independent canonical comparison produced exactly one match, candidate index 1 (the second original entry). Runner-image log lines independently agree with `ubuntu-26.04` and image version `20261111.196.1`.

## Byte transport and retained evidence

The artifact list's actual `total_count` is 1. One provider artifact-download invocation obtained this new artifact; one GET of its returned permitted temporary file URL materialized the archive with HTTP 200. No second provider artifact GET, historical artifact download, rerun, or retry occurred. The temporary signed URL and opaque file-access reference are omitted from retained transfer data; `08-artifact-download-tool-result.json` contains a sanitized nonsecret descriptor. The exact public archive and observation bytes are retained losslessly.

| Received object | Bytes | SHA-256 |
|---|---:|---|
| Actual artifact ZIP | 2443 | `5f39d5891fd7ef2408cdf743c485fa51fac04111be453d7d29baefd3ebd95d8f` |
| `OBSERVATION.json` | 6347 | `5f0037498fbf1a17d4234e8fc87b506ad8c9ebbc69d478581859834c664e65c5` |
| `OBSERVATION.sha256` | 83 | `6c9ede7fcf79caba928b9ae2690dfd5550037929cda85383a8e610f6ab6b5974` |
| Connector-decoded job log, retained as UTF-8 including its leading BOM | 26920 | `a3cb55566ba3015db7b8d989de5a8cc607ea72ec0b7d7cc1b6cb485ffb89ecd0` |

The ZIP has exactly two ordinary unencrypted file members, `OBSERVATION.json` and `OBSERVATION.sha256`. The archive digest matches the provider artifact metadata and the job's upload-digest line. The actual marker was selected by an anchored timestamp-plus-marker pattern requiring literal lowercase SHA-256 and base64 fields; the printed workflow source does not satisfy that pattern. Exactly one runtime marker matched.

The decoded log body equals the artifact body byte-for-byte, parses to the canonical compact ASCII JSON with exactly its final LF, and hashes to the log's stated SHA-256. The sidecar names `OBSERVATION.json` and binds the same exact bytes. Observation and artifact timestamps fall within the actual provider job interval.

Evidence is enumerated in `g221-host-inventory-actual-receiving/EVIDENCE_MANIFEST.json`. It binds the retained connector responses, exact returned JSON content strings, decoded log text, ZIP, extracted members, actual marker, receiving program, result, action/command outcomes, and this final report. The manifest excludes itself to avoid a circular digest. Raw provider JSON here means the connector-returned UTF-8 content strings, retained exactly as delivered. The log connector exposes decoded text, not the original HTTP wire bytes; no claim is made about unavailable pre-decoding log bytes.

## Receiving checks and source join

`15-receive-evidence.py` completed once with exit 0 and 81 successful receiving predicates over the actual captured data. This was evidence receiving, not a repeated source test suite or a new host observation. Its exact command outcome is retained in `18-receiving-command-result.json`, and its complete predicate/command record is `17-RECEIVING_RESULT.json`.

The source join was independently checked as follows:

1. The provider Git commit names the exact sole base parent and published tree. Reconstructing the Git root-tree bytes from the provider response reproduces the published tree SHA and equals the local carrier's raw tree object.
2. All 21 candidate files are byte- and Git-mode-identical between the reviewed candidate and carrier. The only carrier additions are the exact frozen source review, raw reviewed candidate commit object, and publication join. The copied raw commit reproduces the reviewed candidate's Git SHA; the copied review equals the original frozen report and its agreed SHA-256.
3. All ten actual observation source descriptors—observer, workflow, and eight owner modules—match the carrier Git objects. All eight owner modules also equal their base-commit bytes and expected source pins. The observation's base commit/tree and successful closing-read field agree with these bindings.
4. Only the three already bound pure modules `evidence_io.py`, `native_profile.py`, and `current_host.py` were loaded for actual data receiving. Their original `target_host` and `encode` functions consumed the emitted host and reproduced the exact selected tuple and candidate-population digest. No inventory, `credentials()`, `validate_request`, native loader, protected preflight, provisioner, bank, CLI, or host operation was called by this receiving program.

The earlier local unhosted `OS_IMAGE_REFUSED` remains preserved in its original evidence. It is not the outcome of this separate hosted observation, and no historical artifact was retrieved or treated as current host evidence.

## Scope and remaining limits

The received claim is this actual runner/image's complete selected-host tuple during the job interval above. It does not assert that a later allocated runner has the same tuple or that this observation remains current indefinitely. The actual observation explicitly leaves every one of these fields false: `same_job_earned_qualification`, `currentness`, `future_g221_acceptance`, and `effect_grant`. Independent receiving preserves those values.

This resolves the missing prelaunch full-tuple observation at its stated scope, independently of M5 and without spending a recipient or protected G221 episode. It does not replace a fresh recipient, original prelaunch gates, owner admission, a future job's own earned qualification/currentness, or terminal protected receiving. No protected/native/model operation, source test rerun, host repair, key/decryption access, grant, acceptance, or automatic retry occurred in this receiving task.

First failing predicate: none. Missing artifact/source/tuple joins: none. No further provider read or optional test is needed for this bounded receiving result.

PASS
