# Independent review: nonzero G2 receiving summary retention

Recorded UTC: 2026-11-15T13:51:14Z.

Reviewer: `/root/g221_direct_existing_owner_review`. Requested model: inherited GPT-6 Astra Pro, without an override. Actual model: GPT-6 Astra Pro, self-report. Implementation authoring-context reuse: **NO**. The reviewer reused its own previously received public failure evidence and independently reviewed source scopes. Implementation author: `/root/g132_existing_offline_intake`. Root controller: `PRO-EXECUTOR-01`.

## Decision and exact scope

**PASS — bounded engineering source correction for preservation of an existing typed public summary after a nonzero receiver return.** No blocking finding remains in this two-file delta or in its use of the unchanged public consumer. This is an independent source review, not a source/native admission, effect grant, live proof review, accepting operation, or whole-cell award.

Reviewed immutable candidate: `5615fbd71268297d95a909446cdd6b05259f4fce`; tree `72a7ef2628180f240fe20a9d2a02016184c52df4`; sole parent `8165a1edbd057aa59faa16e97a61ad1aabbd1e18`. The worktree was tracked-clean at the final identity readback. Exactly two paths differ from the parent: nine production lines and 111 lines in an existing focused test file, all insertions.

| Changed path | Bytes | SHA256 |
| --- | ---: | --- |
| `qualification/dg16-r5-full-g2/run.py` | 84,859 | `e8576425bcbb260e3d2c21c11e510d51f0549756ab0b8dcc14cfdce7a96de15b` |
| `qualification/dg16-g221-production-integration/test_no_supplementary_export.py` | 13,279 | `343a22b49069de77b123fab54ebf09c2b8fa209d9606cea7bba1650bc4d62898` |

The review addresses the demonstrated loss of permitted diagnostic evidence at the caller boundary. It does not identify or repair the actual failed comparison. The underlying failed relation and its missing witness remain **UNKNOWN**. No missing body from run `43703658937` has been recovered or reconstructed.

## Original requirement and observed defect

Original issue #209 binding comment `5314412493`, Acceptance item 3, requires complete normalized all-settled JOIN to preserve failure, non-verdict, partial and terminal evidence semantics. The retained original is `585012cbc6b47cb332222c2784481567a482c8a5:recovery/contracts/original/issue-209-comments.json`, SHA256 `98a08af52a729ff27a22a88bcf4500f4aa53206cf16086ba0e60446ee9f5e4dd`. The commission at `e4cba42cb5704f00b78d64e43f5da88501c28229:handoff/dg16-dg18-findings-20261115/PRO_UNIFIED_COMMISSION.md`, Section D.5, also requires first-failing-predicate discipline, permitted evidence retention, reuse of unaffected qualification, and justified correction; it prohibits automatic protected retries and UNKNOWN replay. No separate invented failed-leg clause is used.

The actual run's public evidence records receiver return code 1 and the outer refusal `FULL_PAIR_NOT_COMPLETELY_RECEIVED`. The prior adapter saved receiver stdout and stderr privately, then raised that refusal before loading `RECEIVED_PUBLIC.json`; the final public packet consequently retained the previous unreceived operation summary. The exact public packet and source support this boundary diagnosis. The source-based overall-conjunction inference in the prior full report remains explicitly distinguished from a received relation witness. This source review does not promote that inference into actual missing-body evidence.

## Production-path review

The new branch executes only after the receiver command returns and its stdout/stderr have been retained privately. For a nonzero return, it calls the existing `read_pair_summary(output, True, u)`. On a valid result it replaces the existing `PROBE.result` and marks `VALIDATED_UNACCEPTED_NONZERO_RECEIVE`. Existing typed-reader refusals and the listed read/parse error classes leave the previous result unchanged.

The original `need(rc == 0, 'FULL_PAIR_NOT_COMPLETELY_RECEIVED')` still follows immediately. The branch cannot reach after-receive currentness, assign an accepted `PROBE.receiving`, write the live receiving record, prepare a review request, enter the 300-second live hold, or complete the 180-second closing path. The original command, ordinary runtime, maintained source, currentness/native gates, return-code and stderr checks, full-relation equality requirement, raw custody, cleanup, public ceilings, and final failure status are untouched. The uncertain-cleanup exception path is also untouched.

No private stream is moved into public output. `read_pair_summary` uses the existing 49,152-byte checked-file bound and closed `validate_pair_summary` schema. Its optional full proof goes through the unchanged `full_relation.validate_public_proof`: fixed source/policy/population identities and false award flags, bounded counts, digest-only relation locations/projections, and at most two bounded witnesses per scope. Byte witnesses expose lengths, digests and an offset, not private byte contents. A consistent false `all_declared_relations_equal` is expressly valid diagnostic content. Its proof limit remains 16,384 bytes.

## Existing public consumer and bounds

The review inspected the unchanged `emit_bound_public`, `check_cumulative_public`, `public_codec`, `transport_lines`, and `write_public`, not merely the caller tests.

`emit_bound_public` revalidates `PROBE.result`, chooses the received summary when `receiving_status != NOT_RECEIVED`, rereads that exact checked file, and requires equality with the retained result. The existing writer produces one of the received statuses for a received summary. It does not reinterpret the new disposition as acceptance. The PROBE codec has no top-level disposition enum that rejects this new fixed string. Native result-disposition validation concerns the separate nested native projection and is unaffected.

The public codec's shared roots are the native admission, policy adoption and specified nested native fields. The top-level operation result and its disposition are outside those roots, so this change leaves the native string pool and compression unchanged. Finalization still calls the original cumulative bounds and public writer; emission still compares the exact seven saved public files and original manifest and validates transport before emitting any lines. No public or semantic ceiling is raised.

The following conservative arithmetic uses the already retained, decoded actual failed-run public envelope. It substitutes the entire existing maximum permitted summary size, without constructing or claiming the missing receiver body. The old result occupies 15,643 compact semantic bytes; the new disposition is 16 bytes longer. The manifest's PROBE byte-count field remains five decimal digits, and all hash widths remain fixed.

| Bound for that unchanged envelope | Conservative replacement size | Existing limit |
| --- | ---: | ---: |
| PROBE encoded wire | 63,769 B | 65,536 B |
| PROBE expanded semantic document | 68,105 B | 81,920 B |
| Seven-file encoded population | 100,835 B | 262,144 B |
| Seven-file semantic population | 104,548 B | 262,144 B |

These are capacity calculations, not evidence that the missing summary had any particular contents or size. The closed proof shape also fits the existing depth/node bounds; the original document and transport checks remain fail-closed for every actual emission. The existing line/log ceilings remain unchanged. No additional existing-consumer invocation was necessary to resolve the specific compatibility concern, and none was run by this reviewer.

Unchanged supporting source bytes were independently compared with the parent:

| Module | SHA256 |
| --- | --- |
| `host_utility.py` | `02a15dc96ecce23e14a3a84bca880aa536d79fffc4f6d6160835cb4ba97a19b5` |
| `pair_driver.py` | `3bf4d21e6c8da690d319a8294f2f52d525595e0cbd30542204ed05c3bd96530b` |
| `full_relation.py` | `04fe4362385b819363f8785d0ad9a346724937f2e798e25536a7ad67db550499` |
| `policy_control.py` | `8d7c9deca483085c206ddd4372d52052d543b563faf26189a3582e2e3a245d54` |
| `live_control.py` | `2154177c5ad6cc3864407a2f7c0254cb21645d89cb8c45f9cfba247b39e63a88` |
| `native_integration.py` | `c6f2b17e59369a04db2062b79ea2150c54d978fd1c0f18a9b25e094e303bc266` |

## Focused author evidence received

The reviewer read the exact two-file diff, constructed test inputs, command records and raw RED/GREEN stderr, and verified the evidence descriptors in `SOURCE_FREEZE.json`. The new controls use the existing actual public-summary writer and typed reader with explicitly constructed, non-accepting inputs. They exercise a valid false proof and a malformed summary; process/effect calls are stubbed. Both verify the unchanged refusal and absence of later currentness/receiving actions.

Author RED: two controls, exit 1, 0.284374 seconds; valid-summary control demonstrates the former missing result, malformed-summary control passes. Author GREEN: the same two controls, exit 0, 0.326346 seconds. Reported source syntax and diff-whitespace checks also pass. This reviewer did not rerun them or any previous suite, invoke a model/native/provider episode, or launch a protected operation.

| Retained evidence | SHA256 |
| --- | --- |
| `SOURCE_RECORD.md` | `df8fc7c84ab4c15bdec01e7e5f2391996fabee0a6111181e1e8d2c671bb2de43` |
| `SOURCE_FREEZE.json` | `e33a25d188997006af9896a71a65be20a210b4e8539e942c0598d2f4864aa589` |
| `RED.json` | `e283dd9c7afcd9a0249aaa51f1ef61d9cb1372079507ff6ca5e73a06f54e11f5` |
| `RED.stderr` | `a4925483a0f44e5d1a02cafaf92000c44053ee8fc8d4b38b212a0c4eab8b2a66` |
| `GREEN.json` | `0556ffdaa39584142128a00134624798c97cc8086da1fc71827281fbf0fa7a5b` |
| `GREEN.stderr` | `bbff6af25509b255944ccdbf5aef9607e95e22dd11d145150842a86ce13fcf3f` |

The author records' historical `independent_review: PENDING` is preserved; this newly authored report supplies the subsequent decision without rewriting their earlier bytes.

## Pin closure and publication limits

The 19 workflow guards and four original source/native decision bodies still bind the prior `8bb3882c...` adapter. They remain historical and unmodified. Candidate `e8576425...` does not satisfy them. This review therefore supports the intended engineering-only source publication, not use of the old protected workflow or a new accepting execution. It does not silently propagate pins, repair old decision bodies, assert that the old full suite is current, or spend an earlier authority grant. Any later execution needs its genuinely current source/authority binding; none is issued here.

The terminal evidence publication was separately received using the local exact payload and retained provider commit/ref readback, without another artifact acquisition: commit `0b6934066ad38cc74b0ce088f5196aa32a9a645d`, tree `3a76fe399ad0294ed07dc97f3298dfae0a53e0f4`, sole parent `8165a1edbd057aa59faa16e97a61ad1aabbd1e18`, on `engineering/pro-executor-original-completion-20261115`. All 17 additions match the payload and manifest; the original 15 evidence bodies are unchanged. The receipt is `/workspace/scratch/0269e6626329/dg16/.IMPLEMENTAUDIT/runs/pro-execution-restoration-c8fCFS/lanes/g221-live-run43703658937/PUBLICATION_INDEPENDENT_RECEIVING.json`, 4,446 bytes, SHA256 `6e5d35a3b8ae1be09d9986555e905df968aecd0e07448ad820f9f09c7676b1b2`. That publication remains actual failed-run receiving, with no G2/M2/M5 or whole-cell award.

No original public artifact, prior full independent report, prior source/native decision, or Root record was modified by this review. The retained false-proof construction is test evidence only and must not be inserted into the actual historical packet.
