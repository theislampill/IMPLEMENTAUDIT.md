# G2 bounded causal trace of the actual terminal failure

## Disposition

**PASS — the comparison-to-failure control flow is explained by the retained actual evidence and unchanged, pinned source. GAP — the underlying contents responsible for the four `whole` differences cannot be causally resolved from the permissible retained public evidence.** No repair, normalization change, retry, original M2 acceptance, or closure follows from this report.

This is the bounded follow-up requested by Root after terminal receiving of run **43796080658, attempt 1**, at workflow source **acd060f7e0b989480b790d1db6ee257eb79be5c9**, product source **205aeab7c93299b0666b261485ab5658d8e183de**, product tree **9ffbaf95080092bf4a45b8772a97ed16068544a7**. It supplements the completed terminal receipt; it does not replace or revise that receipt.

Reviewer: `/root/independent_receiving`, the distinct receiver, not the source author or executor. Model selection was inherited without a reviewer override; this report makes no separately attested provider-model claim. Authority: none.

## Evidence and method

The reviewer read the decoded, already-received actual public proof and the existing comparison code as data. The reviewer used standard-library parsing and SHA-256 checks for evidence identity, without importing or executing the target modules. No tests, target execution, artifact body download, private reconstruction, candidate-path hashing, hash inversion, source edit, normalization edit, remote mutation, review/control payload, or retry occurred. The systematic-debugging skill was applied only to this evidence investigation phase.

Retained evidence under `/workspace/scratch/48c1b1d4cf7d/independent-receiving/`:

| Evidence | Bytes | SHA-256 |
|---|---:|---|
| `G2_TERMINAL_RECEIVING.md` | 11,424 | `13363ad14af2ac7a758e32eb7b2a18f4940249830b09b8042b6270f14887edab` |
| `G2_TERMINAL_PUBLIC_DATA_RECEIVING.json` | 122,759 | `ed3b6f52211ff31cb187ce91d4ff6ebee52f3a603b2e6e6421ea29ecaca09402` |
| `G2_TERMINAL_EVIDENCE_JOINS.json` | 9,346 | `395bf87b922a79854f9ccb202bde7487f9d2ff2dcfcbc94e021f39cca41faad1` |

Those records retain the seven exact public wire files and their actual job-log/provider joins. The original terminal archive was 15,712 bytes, SHA-256 `7b1056758b5077b010a30064e0eb40a6f7059b08f494982855b438ff4781e4ad`. The original job log was 122,887 bytes, SHA-256 `f6c1eb4bb318cdac869ccfd4ca8c8d4f788e7534dd0b1fe530e6fb5211e18687`. No duplicate archive acquisition was needed for this trace.

Source directory: `/workspace/scratch/7fbb79f74aa4/recovery/g2-fresh-preparation/qualification/dg16-r5-full-g2/`.

| Source used for the trace | Bytes | SHA-256 |
|---|---:|---|
| `full_relation.py` | 30,551 | `04fe4362385b819363f8785d0ad9a346724937f2e798e25536a7ad67db550499` |
| `full_output_relation.py` | 24,126 | `1328f4e1987afaeda665f7392cc7424f9441ece5acf017c265c732b1a3f4f711` |
| `finite_relation.py` | 39,925 | `2e4973ca429ad560b25bf71572714e13d6590939b06fa2171b0836176be79ee9` |
| `full_stdout.py` | 13,158 | `fc97581971b37ebd6620d5dc5144e26c4a6e35303ba2868f658f21acb3198f88` |
| `pair_driver.py` | 48,451 | `77ca44aa123167c4dbc5b6d35ba66d587e25f8e192db0bc8224b014f690bf174` |
| `run.py` | 84,859 | `c93bf11715e40ed51b92f9463ed5c08710d500685384abc890043465f03e950a` |
| `RELATION_INPUTS.json` | 1,311 | `41bdfe0fb7ee119b5fd1fdc0ee1564c99977d80981b80414d5afa595a476a014` |
| `POLICY.json` | 22,159 | `21afa7726556a8ba7814ba6f3a133a0fbfadc3b9e93a83a65b7f843b518786b1` |

The current bytes and sizes of all eight module/data members named in `RELATION_INPUTS.json` matched that exact input manifest. The inspected relation code is therefore bound to the input/policy identities in the actual proof. The other dependency bodies were not newly investigated beyond their identity checks unless needed for the trace. Relevant source locations below refer to these fixed files.

## What the actual proof establishes

The actual `PROBE.json.result.full_correspondence` reports:

| Relation | Equal | Difference count | Exported witnesses |
|---|---|---:|---|
| `whole` | false | 4 | First two only; both `VALUE`; incomplete |
| `portal` | true | 0 | None required |
| `repro` | true | 0 | None required |
| `pending_durability` | true | 0 | None required |
| `pending_loader` | true | 0 | None required |

The full conjunction is false. Both subject verifier routes exited zero. The proof records 111 actual report slots for each route, 193 skips for each, zero expected failures, 49 portal events and 19 repro events per route, and true same-job raw receiving, raw-census bookends, and source/runtime bookends. These retain their exact declared consistency scope; they do not establish unexported test internals or original acceptance.

The `whole` projection digests are `75b0d5cc4fe05067361aeb666652bed562d1a6340cbc9ea817c43c56c93d858a` and `b201130c2fe0f283ca89b101235c3ce91cd4a47c4e1c72cc6ae70591246b47f0`. The only two exported witness locations are SHA-256 commitments `4985477570aa4572468a9c3cba1e855e1388d6c584ca87ddea9e44e9e951ae70` and `834e24f5c25a08798f6e558eae0adc6d40a324afbb496cf369d0bde84f502ee1`. Neither exports its field path or values. The two other differences have no exported witness. This trace did not attempt to recover the committed paths or values.

The public raw comparison separately says raw stdout and stderr differ, as do raw portal/repro envelopes; its other listed raw checks agree. Raw inequality alone does not establish which differences survive the adopted relation. The normalized portal/repro comparisons actually agree.

## Resolved control flow

1. **All five projections were constructed and compared.** `full_relation.py:281–355` reads the actual sealed capsules, requires maintained same-job receiving, constructs `whole`, portal, repro and both pending projections, compares them, checks source/runtime/capture stability, and writes a public proof even when the resulting conjunction is false. The actual complete proof and `RECEIVE_COMPLETE` observation show that this route reached the comparison result; the supplementary causal observation remains non-authoritative progress evidence.

2. **The complete raw pair did not satisfy the full comparison.** `pair_driver.py:457–490` defines raw-pair completeness separately, retains `RECEIVED_COMPLETE_RAW_PAIR` and the full proof, writes the public summary, and returns zero only when the raw pair is complete **and** `all_declared_relations_equal` is true. With the actual false conjunction it returns one. The actual capture of `receive-separate-maintained-sealed-receiving` has exit one, complete streams, no timeout and no capture-internal failure. This reconciles the nested raw-pair receipt with the outer failure without treating the raw-pair status as overall acceptance.

3. **The episode correctly stopped before independent review.** `run.py:896–935` preserves a valid summary from a nonzero receiver as `VALIDATED_UNACCEPTED_NONZERO_RECEIVE`, then refuses at `need(rc == 0, 'FULL_PAIR_NOT_COMPLETELY_RECEIVED')`. That is the actual failure code and disposition. The all-equal guard also exists before review preparation. Actual review preparation, upload and hold steps were skipped; no nine-file request or 300-second live review was entered.

4. **Finalization preserved incompleteness.** `run.py:1089–1114` requires all original steps and no failure before post-review custody checks. Actual finalization reports `EPISODE_INCOMPLETE`. It did not create an independent review, Root consumption or closing proof. Ordinary final-currentness success and the separate native `closing_currentness_verified_before_teardown: false` remain distinct, as recorded in terminal receiving.

Thus the immediate reason for the nonzero receiver and failed episode is established. This chain does not expose the cause of the differing projection contents.

## What “four differences” means in this code

`full_relation.py:141–193` uses a typed recursive comparison. Equal-shaped dictionaries recurse through sorted keys; equal-length sequences recurse through indices. A divergent scalar, byte blob, type, field population or sequence population contributes one count at the point of divergence. It preserves only the first two witness records. `witnesses_complete` is true only when the count is at most two.

Consequently, the actual first two `VALUE` witnesses establish same-type scalar inequality at two traversed locations. They are not direct byte-blob witnesses: byte witnesses would have kind `BYTES` and include byte counts and first differing offsets. The kinds and locations of the remaining two differences are not exported. The count is a projection mismatch count; it cannot serve as a test-failure count or independent root-cause count.

`full_relation.py:231–278` compares a `whole` object containing the projected result, mapping, command bytes, normalized stdout, normalized stderr and retained outer files. It replaces the validated route-specific fields and elapsed time with fixed relation markers, and replaces the result's stream hashes with hashes of the normalized streams. The normalized stream bytes also remain separate compared fields.

**Conditional code behavior, not an actual-cause finding:** when a normalized stream differs and its derived hash differs, that one stream contributes a scalar hash mismatch and a byte mismatch. Two differing normalized streams could therefore account for four projection mismatches. The actual exported witness commitments do not identify their paths, so this report does not assert that this is the actual four-difference allocation. Other surviving projected fields cannot be selected or excluded solely from the count and two hidden locations.

## Parser and normalization boundaries

The operative `full_output_relation.py:353–396` definition overrides the earlier same-named definition in that module. It checks the source-bound report population, actual frozen environment, declared class skips, progress, identities and successful result counts. It replaces only each declared unittest elapsed-time operand with `<DECLARED_UNITTEST_DIAGNOSTIC_SECONDS>`. Other stderr bytes survive. The earlier report-slot/parser refusal is not the terminal failure of this run: both report transformations returned and the full comparison proof was emitted with 111 actual slots per route.

`full_stdout.py:172–203`, with its named helpers and `finite_relation.py:406–420`, rewrites only declared, validated source/output roles and exact progress operands. It retains other stdout bytes. The proof's successful construction supports passage through those guards at their defined scope. It does not establish that the two resulting stdout streams or stderr streams are equal.

These facts narrow the failure to a completed comparison result under the adopted relation. They do not distinguish an unmodeled incidental output difference, a meaningful behavior/output difference, or a comparison/projection defect. No one of those causal classes is demonstrated by the public record, and none is promoted to a repair rationale.

## Evidence limit and resulting scope

The actual public summary states `LIVE_JOB_ONLY_RECEIVE_BEFORE_TEARDOWN_NO_CUSTODY_TRANSFER`. It exports a descriptor for 7,387,746 bytes of private observations, SHA-256 `8da6c6df0dfad75f8187457545b703cc210f4eb9e1ec5a0038077c87c827ca1c`, not those observations or raw captures. The complete normalized projections and differing output bytes are not in the seven-file public packet. `full_relation.py:328–355` confirms the bounded public projection and private-observation separation. The job is terminal, so an ordinary post-teardown read cannot recover the actual live private custody.

The permitted evidence therefore resolves **where and why acceptance stopped**, but cannot identify **which private values differed or why they differed**. A demonstrated underlying cause would require permissible actual evidence of those differences and their producing path; this report neither supplies nor authorizes its reconstruction or a new operation.

Final bounded result: the positive complete-command/raw-receiving and four equal-relation facts remain recorded at their original scope. The failed `whole` conjunction, absent actual independent review/Root consumption/closing proof, and original M2/full-G2 gap remain. No G1, G3, C5, full T14, canonical conversion, legacy retirement, native capability, or audit closure is awarded. Historical G220 evidence is not promoted. The separate C11 interruption receipt and all completed terminal receipts remain unchanged.
