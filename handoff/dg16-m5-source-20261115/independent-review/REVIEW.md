# Distinct review of the current M5 source binding

## Disposition

**PASS at the bounded source review scope.** The frozen candidate is suitable for Root's already authorized guarded source publication, subject to Root's actual exact-branch absence/create-only check and readback of the published identity. No blocking source discrepancy was found. This is not a hosted-route result, original M5/Q04/Q05 acceptance, G221 identity join, M6 receiving, native discovery, release, or closure.

Reviewer: `/root/dg18_engineering`. Author: `/root/dg18_independent_review`. The reviewer did not author the candidate or the binding machinery. Root delegated this work under G0008 receipt `fda5007ee43c62168481f23d511d083d6ab51be9`; the reviewer created no controller and changed no ledger or remote state.

## Exact subject

| Item | Identity |
|---|---|
| Candidate commit | `21c53ac61f6db57f0bb8ddfdabeb254420e109c2` |
| Candidate tree | `298bc72039ccf0ec6ed52e85594fe832818e1de1` |
| Candidate parent | `07a57141b74b5e7861a3145174582347837d075c` |
| Original published runner | `9493cb25ec976aebb056191ec4eafa086d6b44d6` |
| Selected product | `205aeab7c93299b0666b261485ab5658d8e183de` |
| Selected product tree | `9ffbaf95080092bf4a45b8772a97ed16068544a7` |
| Prospective branch | `engineering/pro-executor-dg16-m5-source-20261115` |
| Candidate manifest SHA256 | `1068764f35a15d9610e8cf01dda9ea85861546e33da844d17839aac39a40a75c` |
| External author freeze receipt SHA256 | `e0f50c967114c8da787361a8a8c49f88f53348728ddceacbb8df94a10ecb7d9e` |
| Author qualification JSON SHA256 | `3cb17a15003c0b5db81e7d5422bee1067937f989491efdf4380fa4ff182a3cba` |

The candidate was clean at entry and exit. All 64 manifest members, totaling 2,286,337 bytes, match their SHA256 values, byte counts, Git modes, filesystem modes, and exact candidate Git blobs. Including the manifest itself, the parent-to-candidate diff is exactly 65 additive files. No existing product file is changed. `git diff --check` passes.

The reviewer read all six originals directly from the immutable original Git commit and matched them to the retained original-source copies. All six generated current files also match the pre-outage checkpoint pins. This independently establishes the source relationship without treating recovered prose or historical scratch paths as the original files.

The complete selected product manifest contains 1,766 files and 167,023,692 bytes, SHA256 `e912e90f2a8c3e40a93e0f1381dc7ecb387b1685106b1a1f31c0fd50d66c4743`. Every selected product file was independently compared with its Git blob, content hash, and mode; HEAD/tree and clean status match the selection. The candidate's newer base is not substituted for this product.

## Source differences and pin closure

The reviewer independently compared all 93 top-level functions/classes across the four Python modules. The permitted top-level changes are the source commit/tree, manifest digest, dependent module hashes, and exact engineering branch. Three function bodies change only their derived source-population literals: `run.py::public_project`, and `host_support.py::read_manifest` / `verify_source`. All 16 installed-runtime functions and all 28 host-utility functions/classes are unchanged. The complete workflow differs only in its display name, two branch bindings, selected product ref, and 17 adapter digest literals.

| Component | Current SHA256 |
|---|---|
| Workflow | `874b654791f963eb457eceea382c1e8d64a17cda0d1ebb10f06b5cc10d7a186c` |
| `run.py` | `08a0e604b47a88634c2422eb1f8dab36e00000c86173823afb05756c8cfe2c2e` |
| `installed_runtime.py` | `e419839f1c2eb396ef13812971a2eaa4b9498cc91d42a84663a8387bb165b957` |
| `host_support.py` | `702029cbdf0b6e3d84e993e449c822286194c3c7addd482204188e7a1259f08c` |
| `host_utility.py` | `429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c` |

The actual module loader and complete source verifier passed, as did a fresh generator `--check` invocation. The generator's check mode does not rewrite the candidate. A tampered module and a tampered manifest were independently refused. The exact original initializer, installer, claim/author/inspect/activate, ordered STATE/ROADMAP reads, normal resume/currentness, separate-process receiver, closing readback, and cleanup implementations are preserved.

## Workflow and host admission

The single workflow admits only a push to the exact engineering branch in `theislampill/IMPLEMENTAUDIT.md`, with `created == true`, `deleted == false`, and attempt one. It does not add dispatch, schedule, pull-request, or automatic retry routes. Concurrency leaves an active predecessor running. Permissions remain `contents: read`.

Pinned checkout actions select the actual workflow commit into `packet` and the exact selected product into `qualified-source`, with persisted credentials, safe-directory modification, submodules, and LFS disabled. All 17 command bodies compare the actual adapter digest and invoke physical `/usr/bin/python3 -I -S -B`; each Bash body passed syntax checking. The existing 15 operation steps, finalizer, emitter, and conditional upload remain ordered. The finalizer/emitter retain `always()`, while upload requires the successful emitter's explicit eligibility output.

The unchanged host gates require actual Linux/POSIX x86_64, a non-root user, Ubuntu 26.04, Python 3.14.4, root-owned nonwritable tool custody, and actual boot identity. The actual earlier G220 HOST wire records that OS/Python/image profile at run 43640583300, job 132587057176, UID 1001, image `ubuntu26 / 20261111.82.6`. **G220 remains failed.** Its wire is feasibility evidence only. It did not independently observe M5's `/usr/bin/env`; the future run must satisfy that unchanged live check itself.

The reviewer reproduced both actionlint outcomes with the pinned 1.7.12 binary, SHA256 `c872d6db8c6bf83a8eaa704fc93999f027d55dffbc63b8a6abdccb47df5f4cd4`. The default invocation exits 1 with the sole catalog diagnostic that `ubuntu-26.04` is unknown. Filtering only `^label "ubuntu-26[.]04" is unknown[.]` exits 0 with empty stdout/stderr. The runtime label and host requirements remain unchanged, and the raw diagnostic is retained. This does not promise future runner availability.

Timing remains the original 45-minute job ceiling, 2,400-second adapter interval, 180-second finalization reserve, and 600-second setup/build ceilings. Signal handling, remaining-deadline calculation, owned-child cleanup, pending-step preservation, source/tool/runtime bookends, and no-replay checks are unchanged. Timing is reported at its original interval; checkout and artifact transport are outside it, with no elapsed-time subtraction or performance-threshold claim.

## Independent focused execution

`review_candidate.py` completed successfully at `2026-11-15T06:18:48.882698+00:00`. Thirteen selected reviewed harness controls passed, with zero failures, errors, or skips. They address the concrete changed-binding risks: actual hash-loader/source verification, current package parsing, checksum and source drift refusal, workflow structure and 17 Bash bodies, complete and partial public output, same-process receiver refusal, expired time, over-reserve package size, build replay, module tamper, and manifest tamper.

Three additional reviewer checks passed: the exact 587,824-byte usable package boundary; the exact 2,400-second interval boundary; and the complete current-source cross-document conjunction with four received route rows and both source bookends. Those are explicitly synthetic local checks, not hosted evidence. The selected complete output has nine public files totaling 16,378 bytes and 19,720 envelope bytes, inside the unchanged limits.

The author's retained record independently binds 58 distinct passing controls, zero failures/errors/skips, its actual command/exit code, current harness hash, and full stdout/stderr. The reviewer did not rerun all 58 or the historical 27 canonical controls. No product entrypoint, installer, controller, provisioning operation, or native/model operation was executed by this review.

## Packages and output boundaries

The existing archive parser accepted the newly built fixture bodies and refused adverse checksum/source cases. The two roles remain canonical plugin and standalone compatibility, with 75 and 72 archive files, complete inventories and exact selected-source parity. The unchanged per-role cap is 589,824 bytes, reserve 2,000 bytes, usable limit 587,824 bytes, and revision-four owner approval SHA256 `e4af32dc219e8c041d62170b960cdb465f0cdfebdb7e414d0f45b7726cc31488`.

| New fixture | Bytes | SHA256 | Remaining after reserve |
|---|---:|---|---:|
| Plugin | 584,971 | `a43f018d4d3cc6d6257eeacfd8b5b834588410564ac33b0c8022d01a0ca71e58` | 2,853 |
| Standalone | 580,360 | `d1b89ec4113b0c57d925e2f5aeec16c1baa471985b918e6fc3e54e808fad7f1e` | 7,464 |
| Checksums | 195 | `111b0ce101919b0d383d2e867599566d42be5e1f9532a13c797c6d4547eb3247` | — |

The successful output population remains RESULT, HOST, SOURCE, PACKAGES, ROUTES, PHASES, FAILURE, CLEANUP, and ARTIFACT_MANIFEST. A bounded unqualified fallback can be smaller. Every uploaded path is a named public file; private command outputs, original private diagnostics, and private package bodies are excluded. Public transport validates the allowlist, byte/hash manifest, regular-file readback, finite JSON values, 65,536-byte file bound, 262,144-byte aggregate/envelope bounds, and 1,048,576-byte envelope-log aggregate. The original result leaves all governed phases open and reports no original acceptance or native discovery.

## History, failures, and remaining work

The pre-outage `Checks.run` shadowing failure occurred before tests ran. The incorrect expected manifest assumption, interrupted correction, initial actionlint argument error, label-catalog diagnostic, and diff-whitespace preservation correction remain explicit. The lossless G220 log wrapper is a new serialization of surviving decoded bytes; it is not described as an original raw HTTP response.

The historical 27-control receiving was completed before the outage. Its observed distinct receipt SHA256 `88010959d4a869bdc4940fdf1632ef06e78c0fded6ac06d12af134858ccab62c` remains a historical record in prior tool-side conversation. **The old 914-file packet, sealed bundle, and A/B raw bodies are not recovered by this candidate or review.** The new fixture's equal hashes do not recreate that execution history or make it G221 output. Historical earned four-route credit at run 42232703790 remains at its original producer and scope.

Root must perform the actual branch-absence/create-only publication and read back the resulting remote commit/tree. Hosted execution and independent receiving remain pending. The companion `HOSTED_RECEIVING_PLAN.json` describes the original bounded receiving checks and preserves the no-retry/no-private-body boundary. A successful source run still requires exact package/source joining with G221 and applicable M6/original receiving before any original M5 decision.

All review writes are isolated under `/workspace/scratch/0269e6626329/m5-review`. The candidate and selected product remained clean and byte-identical to their frozen inputs. There were no remote effects, protected operations, controller/ledger changes, new package builds, artifact reacquisitions, or original acceptance claims.
