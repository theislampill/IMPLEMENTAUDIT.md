# M09 R3 completed original operation — independent receiving

## Disposition

**PASS_RECEIVED_FULL_M09_AUTHORITY_DISCRIMINATOR_ADVISORY.** No remaining receiving gap was found in this exact completed operation. Independent reconstruction from the frozen requests and retained file bytes confirms all eight original invariants, all five exact mutant out-of-scope effects, and all three mutant specificity controls. This conclusion does not rely on the driver's provisional status or on accepting the external oracle's PASS/FAIL labels.

Reviewer: `/root/independent_review`. Authority: **NONE**. This is ordinary advisory receiving, not a formal internal assessment route, execution authorization, family award, lifecycle transition, or closure. Root retains adjudication and publication. Root rebound this review after the reviewer context boundary to G0043 receipt `33c5296d4d9bf5ae370780b3d9895a8ce1b825cd`, currentness receipt `be2c2b/0`.

## Exact evidence received

| Object | Bytes / members | SHA256 |
|---|---:|---|
| R3 `SEAL.json` | 20,772 bytes; 86 payloads / 1,954,077 bytes | `25d14085c698ed9809dfbc062f9b24d390077327b536a4ff1560473e87a59e90` |
| Actual `EXECUTION_MANIFEST.json` | 207,325 bytes; 944 payloads / 11,449,918 bytes | `c026cc8d372843119ff4dd26e4b591d9da4cfaac5200afb4c7c2226eab64d93f` |
| Root `ROOT_EXECUTION_ADMISSION.json` | 63,602 bytes | `647d9068d93124619072dc61270e7a84cda22cabbf82c0fe950bdd525564ad2a` |
| Frozen case requests and byte inputs | 15,011 bytes | `2a9f91f088bf355278571da5b6205d012a160366f518f402015373c08fe931ae` |
| Frozen external oracle | 10,855 bytes | `42e3f6e7b54562ee882b839f0e3d656e30ec69c02ffc266e5882e4ad94552ebc` |
| Exact R3 runner | 18,074 bytes | `3b83f026cd87d81e81f7b2012ab861cb9cf1dd01c1b6bd98af84ff3d0950bef8` |

Packet root: `/workspace/scratch/097486cde2dd/dg17-full-family-r3`.

Actual operation: `DG17_M09_SCOPE_CONSUMER_ORIGINAL_20261121_02_R3`, retained under that packet's `execution-01`. The execution-start record binds the exact packet seal and exact Root admission. Root's native initial receipt is `27b072`, session `58262`; the terminal receipt is **`10cced/0`**, with the expected pending-independent-receiving status and `award: false`.

All 86 sealed payloads and all 944 execution members were independently hashed. The execution inventory has no missing or extra regular files except its own manifest, and no symlinks or unsupported file objects. The complete inventories were rehashed again at the end of receiving. No STOP or baseline-failure record exists in this operation.

Earlier R3 preexecution review remains immutable at `/workspace/scratch/097486cde2dd/dg17-m09-r3-independent-review/SEAL.json`, digest `8523655984ec6cd72145690fa2fb860c230435e4ae18647b28ea849bcfd00aad`. The earlier failed R2 execution manifest still has digest `4ac883a973496e3c86b90c47a72197066fc15aed65d6df213e0d9e6e1bb1e93f`; its independent failure-receiving seal still has digest `31bdf2a64c06d2c1ce66789f8ab7f072bdab632a95b3cf900f8f3ad52ff7025d`. Those historical failures and reviews were not replayed or rewritten.

## Independent reconstruction of all eight paired witnesses

Each row below is based on the complete received workplane, exact helper exit and raw output, and retained transaction evidence where a transaction was created. Every path shown is relative to the disposable subject. Every unmentioned file, including `README.md` and the unrelated dirty bystanders, is byte-identical to the frozen snapshot. Destination absence is checked as part of the full expected file population.

| Frozen witness | Original actual result | Mutant actual result | Decisive complete post-state |
|---|---|---|---|
| `owned-residue-delete` | Exit 0, COMMITTED | Exit 0, COMMITTED | Only `dg17-work/task/result-cache.bin` is absent. Both unrelated user files are unchanged. |
| `foreign-source-delete` | Exit 64, exact scope refusal; no transaction | Exit 0, COMMITTED | Mutant alone deletes the exact 57-byte `dg17-work/user/notes.md`; all other bytes remain unchanged. |
| `heldout-name-looks-disposable` | Exit 64, exact scope refusal; no transaction | Exit 0, COMMITTED | Mutant alone deletes the 57-byte protected `dg17-work/cache/retired-output.bin`. Its presence in both scope lists does not authorize the original. |
| `heldout-opaque-replace` | Exit 64, exact scope refusal; no transaction | Exit 0, COMMITTED | Mutant alone replaces `dg17-work/x7/v19.dat` with the exact frozen 57-byte candidate, including its NUL byte. No other path changes. |
| `foreign-move-destination` | Exit 64; source remains and destination stays absent | Exit 0, COMMITTED | Source becomes absent; `dg17-work/user/new-artifact.dat` contains the exact 45-byte source preimage. The destination is absent from the allowlist. |
| `explicitly-excluded-destination` | Exit 64; source remains and destination stays absent | Exit 0, COMMITTED | Source becomes absent; `dg17-work/user/excluded-artifact.dat` contains that exact 45-byte preimage. Explicit exclusion still wins in the original despite allowlist inclusion. |
| `owned-residue-relocate` | Exit 0, COMMITTED | Exit 0, COMMITTED | Both variants remove the source and create `dg17-work/task/ordered-result.bin` with the exact 45-byte preimage. |
| `truncated-preimage-control` | Exit 64, REJECTED_NO_MUTATION / PREIMAGE_DRIFT | Same | The seven-byte prefix is not accepted as the full 45-byte source. Both variants preserve the entire workplane, report no actual effects, and create no transaction. |

The source preimage moved in the three move witnesses is SHA256 `15ad6f90edae4e3a50a132570e7cd69d18a6f0bc653fbbb08bd53b2d8dc30c06`. The unrelated 57-byte user content is `a02f7e17ee30d99a2ce676e4c489b9eab3202e733d127e0ac47cb9f635352107`. The opaque replacement candidate is `53b4fc473b2fa8b4664b705480f5f9836f519f69708d856b3fa77d7854be649b`. Receiving compared full bytes, not only these hashes.

This is the complete frozen M09 authority-consumer family mapping accepted during preexecution review: owned residue is distinguished from unrelated dirty work, source and both destination exclusion forms are exercised, renamed and opaque held-outs discriminate without prose matching, and the unchanged preimage guard remains effective. No partial family credit is proposed by this receiver. These eight constructed witnesses are not eight additional original case awards.

## Source, fixed-input pairing, and actual processes

The full source intake remains **23 files / 983,360 bytes**, pinned to commit `51416b2f156b341c4a5f09029e2c6ceb5b30b1e7`, tree `9c3913ceaa95f3f36b0377fe2dba4a302afcba89`. That population includes source context and tests. Each materialized executable package contains the exact **18-file** implementaudit subtree; the original subtree totals **688,266 bytes**. Both complete package inventories were compared directly with the sealed source. The only mutant difference is the declared replacement of the scope-refusal line at `scripts/validate-phase.sh:102` with its frozen comment. The original and mutant validator hashes remain respectively `07b2e04ba9aefffc572ac9cf60ecddf88654a26590aaa045dadf464da7bc7dab` and `8e693bef6a99feb95aa6150ebbd0565cc7e5cda8c91c5ab3620e73da6871879c`.

All eight fixtures have distinct actual v2 claim IDs, exact claimed subject/common-directory/run paths, no controller, and exact frozen phase requests. The only phase substitution is the four prescribed occurrences of the actual claimed run root. Preimage and candidate files match the frozen bytes. Snapshot input inventories and final retained inputs agree exactly. The binary Git v3 indexes were parsed as data, with their checksums verified; all staged protected-file blob identities match the frozen staged bytes. Captured `AM` status agrees with the independently checked staged-versus-working bytes. Snapshot and final Git metadata agree byte-for-byte.

The **112 direct captures** comprise eight successive ten-command fixture setups, followed by eight original helper/oracle pairs and then eight mutant helper/oracle pairs. Setup accounts for **72 Git commands and eight ordinary claim commands**. Every argv, cwd, contiguous sequence number, exit, raw stdout/stderr hash, and start/finish order was checked. All setup commands exited 0. All eight originals, including their separate oracle processes, completed before any mutant helper began. There is one helper and one external oracle invocation per variant/case, with no recorded timeout or retry.

The sixteen actual helper outcomes are **nine COMMITTED exits 0**, **five scope refusals exiting 64**, and **two exact preimage refusals exiting 64**. The separate oracle is the fixed frozen file, invoked without a variant argument and with identical per-case paths for both variants. Its actual exits are zero for all originals and the three mutant controls, and one for the five mutant invariant violations. These captures corroborate the receiver's independently reconstructed byte/status result.

## Authority, transaction effects, and durable evidence

For every decoded helper result, receiving independently recomputed the authority binding from the actual claim, frozen phase owner/baseline, exact operation, and literal scope. Claimed source pre-identities and complete post-identities agree with the independently received bytes and absences. Candidate identities agree with the frozen replacement or move bytes.

All nine committed transactions have exact durable authority records, complete durable result records, and released lock-owner custody. Every recorded actual effect has a contiguous sequence, `repo` scope, an applied outcome, and an operation admitted by its exact planned-effect path. Effects are bounded to the exact operation targets, their directory fsyncs, and disposable run/lock bookkeeping. The final target effect agrees with the received target byte or absence. Planned-effect digests were independently recomputed.

Every durable result agrees with emitted helper JSON on all fields except the necessarily earlier actual-effect prefix. The prefix agrees exactly; each emitted result adds precisely the six captured result-publication effects after its saved prefix. Successful transactions retain only `authority.json`, `result.json`, and released-lock owner records. No final journal, journal temporary file, stage, backup, or result temporary file remains. The final mutant subjects agree with their saved workplanes and transaction archives and contain no retained active path-lock owner. Original archives were received before the runner restored each shared snapshot for its mutant.

The code paths supporting this interpretation remain the previously reviewed complete canonical consumer, including `run_m09.py` setup/paired restoration and capture, `validate-phase.sh` authority derivation, and `apply-observed-mutation.sh` result persistence/finalization. Receiving did not substitute a model of product execution: it compared the actual retained effects and byte state against independently reconstructed expectations.

## Evidence limits and reproducibility

- Captured device, inode, and link-count fields are historical observations. They are not asserted to be fresh identity proof for the copied archives or for earlier restored subjects.
- Direct-child captures establish orderly completion of the recorded commands. They do not establish a process-group or descendant-wide absence census, and receiving makes no such claim.
- Successful finalization removed journal files. Their recorded effects and retained durable results were checked; unavailable intermediate journal contents are not claimed to have been independently recovered.
- This operation demonstrates the constructed ordinary mechanical authority consumer. It grants no model-cognition, native L4/L3 lifecycle, protected-host qualification, separate original-case, terminal-clause, or whole-DG17 conclusion. Denominators remain 36 original cases / 14 mutation families / 17 terminal clauses.
- The receiver executed only its own retained-data parser. It imported no product or oracle code and performed no product, original, mutant, oracle, Git, provider, or controller operation. The packet and completed operation were left unchanged.

`RECEIVE.py` is the independently authored data-only receiver. `MECHANICAL_RECEIVING.json` records all sixteen complete expected/received post-state maps, per-case claim bindings, exact process census, authority/result checks, and limitations. Its final successful execution was **`282c18/0`**. An earlier receiver-local assertion mixed the 23-file intake with the 18-file runtime subtree; that receiver bookkeeping assumption was corrected before the successful read-only pass. No candidate or frozen expectation changed.

**Root action boundary:** this sealed advisory evidence is ready for Root's adjudication. The receiver makes no award or publication decision.
