# Independent G2 receiving diagnosis

Reviewer: `/root/g2_receiving`. Authority: **NONE**. This report is evidence and a bounded diagnosis; it does not register canonical findings, accept original requirements, authorize an operation, or close a gate.

## Result

The exact first observed receiving refusal is `need(rc==0,'FULL_PAIR_NOT_COMPLETELY_RECEIVED')` in `qualification/dg16-r5-full-g2/run.py:912` at workflow commit `8165a1edbd057aa59faa16e97a61ad1aabbd1e18`. The receiver returned 1 after completing its receiving path. The retained evidence and unchanged driver support the narrow inference that `full_proof['all_declared_relations_equal']` was false. **The individual normalized relation and its difference witness were not retained and cannot be identified from the available packet.**

The demonstrated diagnostic-retention defect already has its minimal source correction in published commit `fb1e78769cf4932741e1c2c9664c02d14413fb24`. No duplicate repair is recommended. No further correction to the unknown underlying relation is justified by the received bytes.

## Read confirmation and exact evidence

I read the actual-run checkout's `AGENTS.md`, the supplied full `PRO_UNIFIED_COMMISSION.md`, the relevant receiving owners, the actual decoded public packet, and the later published source correction and independent review. The latest task direction governs: Claude=ZERO, Codex=ZERO, no owner-PC tasks. No source edit, test-suite replay, protected operation, commit, publication, or acceptance was performed by this reviewer.

Run `43703658937`, attempt 1, job `132779993512`, used host branch `pro/dg16-r5-full-g2-direct-host-21-20261115`. Workflow commit/tree are `8165a1edbd057aa59faa16e97a61ad1aabbd1e18` / `9f6063112426c605e722cdec4172670df6394e0a`. The maintained subject is separately identified as commit/tree `205aeab7c93299b0666b261485ab5658d8e183de` / `9ffbaf95080092bf4a45b8772a97ed16068544a7`.

The 14,572-byte artifact ZIP has SHA-256 `55a2e6bfece398f2c3fffdf3ca91dbef7f4f3ce11229f4e7223138ef34c11086`. I checked all seven members, totaling 67,310 bytes, with the actual `host_utility.public_codec` and `transport_lines` owners. The manifest, original bounds, ZIP contents, and seven public log records agree. All seven files and the ZIP also match the retained publication byte-for-byte. The supplied log equals the published log plus one trailing LF; both descriptors are preserved in `RECEIPT.json`, with no change to either input.

The retained provider readback binds the same artifact digest, run, branch, and workflow commit and records no review artifact. This reviewer received the supplied and committed provider evidence; a fresh provider acquisition was not made. `RECEIPT.json` contains all source/evidence descriptors and exact checks. `decoded/` contains faithful decoding of the original public documents only.

## Earned evidence preserved at its actual scope

| Retained observation | Supported scope |
| --- | --- |
| Nine current-host native cases; `RECEIVED_CURRENT_CHANGED_NATIVE_PREDICATES`; pair eligibility true | Historical prerequisite receiving for this job, VM, controller, and source. Final native closing before teardown remains false; no transfer of currentness. |
| Legacy exit 0, elapsed 5,452,203 ms | Complete whole-process legacy execution. Its 119 node records remain `UNSETTLED`; no synthetic node PASS. |
| DAG exit 0, elapsed 5,362,678 ms; all 119 node records PASS | Complete DAG execution for the actual map. |
| 119 mapped nodes, 91 physical/registered tests; exact registry reassembly true | Actual registry population and reassembly. The original 48 requirements, 20 cases, 117 original nodes, and 12 terminal clauses are separate denominators. |
| Source before/after equal; 1,766 files / 167,023,692 bytes; initialized runtime unchanged; children reaped | Recorded source/runtime/process bookends at their historical scope. |
| `UNQUALIFIED_OR_INCOMPLETE`; review steps skipped; original acceptance and full G2 false | No M2/G2 or whole-cell award. Pair execution does not establish adopted correspondence or final live review. |

## Exact causal boundary

The actual receiver command has return code 1, zero stderr, complete streams, no timeout, no output overflow, and no internal failure. Its causal observation reaches `RECEIVE_COMPLETE` after `RECEIVE_CLOSING`, with `failure: null`. Its 81-byte stdout descriptor is SHA-256 `8fb735caf5379e08b2c3eb801fdc6f8cd27e2aa672fd2678621161d8223891d7`, exactly matching the source's deterministic public status line for `RECEIVED_COMPLETE_RAW_PAIR`.

`pair_driver.py:490` returns 0 only when `complete` and `full_proof['all_declared_relations_equal']` are true. That source and these observations support the overall-equality inference. They do not expose the missing proof body or identify a particular scope. Four raw checks are false (`same_stdout`, `same_stderr`, `same_portal_events`, `same_repro_events`); those raw differences are inputs to the adopted normalization and do not themselves identify the normalized failure.

The old outer caller wrote the receiver streams privately, refused the nonzero return at line 912, and never read the already-produced received summary. Consequently the exported operation remains `VALIDATED_UNRECEIVED` / `NOT_RECEIVED`. Finalization then reported `EPISODE_INCOMPLETE`. This secondary refusal is not a separate first cause.

## Findings and correction disposition

### G2-RCV-01 — High: permitted receiving diagnostic lost; source correction already published

**Owner/source:** `run.py`, receive caller, actual-run lines 911–913. **Reproduction:** actual receiver return 1 reaches the refusal before `read_pair_summary(output, True, u)`. **Implication:** the permitted typed summary and normalized witness are absent from the final public packet.

**Correction:** retain the existing typed received summary on nonzero return, mark it unaccepted, and keep the original refusal. The published nine-line correction does exactly this. Actual adapter SHA-256 is `8bb3882cd6390b480c3109c9a40d23f6ff2f2e48d73d97381a5b49ad38734b58`; corrected adapter SHA-256 is `e8576425bcbb260e3d2c21c11e510d51f0549756ab0b8dcc14cfdce7a96de15b`.

**Verification:** the committed source matches the prior reviewed candidate descriptors; all eight retained source-freeze evidence descriptors match. Existing retained RED/GREEN records cover valid false-proof retention and malformed-summary refusal. Their two-control GREEN exits 0; I did not replay those already-qualified controls. The original refusal, source/currentness checks, public bounds, and acceptance path remain unchanged by the nine-line delta.

### G2-RCV-02 — High: underlying normalized difference unavailable

**Owner/source:** `full_relation.py` complete comparison, consumed by `pair_driver.py:490`. **Reproduction:** the completed receiving state and return 1 establish the bounded inference above. **Implication:** neither exact cause nor a source correction for it is supported.

**Correction:** no speculative relation patch. Preserve the successful actual subscopes and the unresolved difference. `CLEANUP.json` states `private_outputs_uploaded=false` and `LIVE_JOB_ONLY`; the only artifact contains the seven public files. The private captures, `FULL_RELATION_PRIVATE.json`, and missing `FULL_RELATION_PROOF.json` cannot be recovered or regenerated as historical evidence from hashes. The source-retention correction cannot retroactively repair this omission.

**Verification:** exact artifact population, decoded fields, source control flow, and retained absent review-artifact listing were checked. No private historical evidence was reconstructed.

### G2-RCV-03 — Medium: published engineering correction lacks fresh execution binding

**Owner/source:** historical workflow/source/native decision bindings. **Reproduction:** the current publication still contains 19 workflow guards for the old adapter and the same four old decision bodies. **Implication:** the corrected adapter is engineering source, not a runnable fresh admission.

**Correction:** only if a later operation is independently authorized, bind genuinely current reviewed source and authority. Preserve historical approvals and do not reuse historical grants. **Verification:** the 19 occurrences and byte equality of all four decision bodies were checked against the actual-run source.

## Essential source pins

All paths below are under `qualification/dg16-r5-full-g2/` and remain unchanged between the actual run and corrected publication unless stated above.

| Member | SHA-256 |
| --- | --- |
| `pair_driver.py` | `3bf4d21e6c8da690d319a8294f2f52d525595e0cbd30542204ed05c3bd96530b` |
| `full_relation.py` | `04fe4362385b819363f8785d0ad9a346724937f2e798e25536a7ad67db550499` |
| `host_utility.py` | `02a15dc96ecce23e14a3a84bca880aa536d79fffc4f6d6160835cb4ba97a19b5` |
| `POLICY.json` | `21afa7726556a8ba7814ba6f3a133a0fbfadc3b9e93a83a65b7f843b518786b1` |
| `RELATION_INPUTS.json` | `41bdfe0fb7ee119b5fd1fdc0ee1564c99977d80981b80414d5afa595a476a014` |

## Return to controller

The immediate source recommendation is to reuse the already-published retention correction, with no duplicate patch. The minimal unresolved blocker is the unavailable actual normalized relation/witness. This evidence does not authorize an accepting replay or supply acceptance. For any separately authorized later operation, the follow-up obligation is to retain the actual typed result and failed scope/witness before teardown, then assess those received bytes. The reviewer remains available for a bounded review of any evidence-supported repair.
