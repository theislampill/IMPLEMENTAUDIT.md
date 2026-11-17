# DG16 full25 bounded Andon diagnosis

**Return to:** /root  
**Diagnostic authority:** NONE  
**Entry:** direct bounded audit-andon cord-pull; no governed lifecycle state registered  
**Subject:** run 44073780378, attempt 1; launch b41e2d7100008cdb2f2fcd77b1543a25ad7b9140; product 7b1424420f8616d163a7ef1826999f2392840648 / tree 136af0838a63be674fcdf8a65cf80dd4bedb9ea1

## Decision

The authentic terminal artifact establishes a completed pair with failed whole correspondence, not a demonstrated repair. Its four whole-projection differences are **the two unequal normalized streams and their two derived hash fields**. Four is not a count of independently diagnosed defects or differing byte positions.

The smallest source-grounded next discriminator is the existing D48-C02 cell in `tests/distributed-runtime-contract.test.sh`. The exact product source contains an uncaptured fresh initialization-token diagnostic on that path. It lies between report 33 and report 34, where the first stderr difference was localized. This warrants a narrowly scoped producer investigation and, once its actual output is received, a test-owned diagnostic correction. It does not establish that the observed first byte at raw offset 93079 came from that call, and it does not explain the stdout difference at normalized offset 178528.

No whole rerun, source test, host launch, source modification, comparator change, canonical-state mutation, acceptance grant, external write, child dispatch, or G132 action was performed in this diagnosis.

The local repository's checked-out c37a35c was not treated as product7b. Local exact-object inspection found the product object unavailable; an initial automatic lazy read was refused before retrieval. Subsequent local reads disabled lazy fetch. Exact product and launch files were then acquired through supported read-only GitHub GET/file operations. All 26 saved source snapshots independently match their returned Git blob SHA-1 identities; their SHA-256 descriptors are in VERIFIED_SOURCE_SNAPSHOTS.json. These are diagnostic copies, not a checkout or reconstructed operational custody.

## Verified original evidence

The original ZIP at `/workspace/scratch/211aae41ab24/recovered/dg16_full25/artifact.zip` is 16,613 bytes with SHA-256 `6a24a72de176cfd43f17ebf80b8bbdf97a6a40746ff700eee4a35a4e46d33b3c`. Every one of the six data members matches both the ZIP manifest and the extracted original file. Original PROBE.json is 37,373 bytes, SHA-256 `a7c2a762a4a7854054a892a0a826639d7eabfceb59c497b31797cbe8a0cf0228`.

I independently decoded the original `dg16.public-document-wire.v1` table references. That deterministic decoding equals the separately labelled recovered `decoded-PROBE.json`; the decoded copy was not used as a substitute for original-byte verification. The derivation is recorded in ORIGINAL_VERIFICATION.json.

The [provider job](https://github.com/theislampill/IMPLEMENTAUDIT.md/actions/runs/44073780378/job/134006397196) reports the pair step succeeded, receiving failed, and prepare-review, review upload, and live hold were skipped. This agrees with the original artifact:
- Both whole-process exits are zero: legacy 3,747,366 ms and DAG 3,741,556 ms.
- 119 mapped nodes and 91 registered tests, with exact registry reassembly.
- DAG has 119 PASS terminal node records. Legacy node records remain UNSETTLED with `UNAVAILABLE_WHOLE_PROCESS_ONLY`; whole-process success must not be inflated into a legacy per-node trace.
- Both report sequences contain 111 report slots, with 193 reported skips per route. Static selected-method population is 2,068. The artifact expressly declines a test-level authenticity claim.
- Pending durability, pending loader, portal, and reproduction projections are equal.
- `all_declared_relations_equal=false`; both normalized stdout and normalized stderr differ.
- Inner raw capture receiving is `RECEIVED_COMPLETE_RAW_PAIR`. Outer episode receiving is `NOT_RECEIVED`, with `VALIDATED_UNACCEPTED_NONZERO_RECEIVE`.
- Failure codes are `FULL_PAIR_NOT_COMPLETELY_RECEIVED` at receive and `EPISODE_INCOMPLETE` at finalize.
- Private captures were `LIVE_JOB_ONLY`, were not uploaded, and are no longer available. Exported hashes do not transfer live custody or currentness.

The exact launch `run.py`, lines 913–931, deliberately retains the validated nonzero receiver diagnostic before refusing, so inner raw-pair completeness is not a contradiction of outer failure. The live review gate additionally requires actual full equality.

## What the four differences mean

The exact launch `full_relation.py` compares a whole projection containing `result`, `stdout`, and `stderr`. At line 400 it replaces the two result digest fields with hashes of the normalized streams. Its recursive comparison counts one unequal byte-string leaf regardless of how many bytes differ.

I independently recomputed the two exposed witness locations and the typed value digests:

| Whole-projection leaf | Location SHA-256 |
|---|---|
| result.stderr_sha256 | 4985477570aa4572468a9c3cba1e855e1388d6c584ca87ddea9e44e9e951ae70 |
| result.stdout_sha256 | 834e24f5c25a08798f6e558eae0adc6d40a324afbb496cf369d0bde84f502ee1 |

Each witness's left/right typed digest exactly matches the normalized stream SHA-256 string in the original artifact. The other two differing leaves are the separately witnessed stdout and stderr bytes. Thus the four-leaf count is fully accounted for without inventing two additional causes.

| Stream | Equal normalized lengths | First differing normalized offset | Available source attribution |
|---|---:|---:|---|
| stderr | 193,469 bytes per route | 94,190 | Raw offset 93,079; BEFORE_REPORT 34, after report 33 |
| stdout | 197,386 bytes per route | 178,528 | No source/command interval in the exported artifact |

A single byte-string witness does not show that only one byte, line, test, or producer differs.

## Report 34 is an interval boundary

The exact launch REPORT_SLOTS.json identifies:
- Report 33: `tests/cognition-pending-write-cases.py`, invoked at line 285 of `tests/internal-skill-routing.test.sh`, five tests.
- Report 34: `tests/work-graph-operation-cases.py`, invoked at line 10 of `tests/native-work-graph.test.sh`, five tests.

The latter source is exactly 9,516 bytes, SHA-256 `086a58488f39f2b538cc4d614c7032e9c1c86706b54c8240ac3bcce544e1ee18`. I fetched its exact product7b content and verified both its Git blob identity and its SHA-256 against the artifact's descriptor.

The diagnostic code explicitly states `VALIDATED_REPORT_INTERVAL_NOT_EMITTER`. Between these report headers, canonical execution includes the remainder of internal-skill-routing, fifteen complete wrapper scripts, the initial native-work-graph-cases program, and the operation-window test's progress before its summary. In particular, `tests/distributed-runtime-contract.test.sh` lies in that interval. REPORT34_DISCRIMINATOR.json records the exact intervening wrapper list.

The operation-window test's child stderr is captured in per-call files and asserted internally. Its name in the report descriptor alone is not evidence that it emitted the mismatching bytes. Changing that test based solely on the descriptor would be unjustified.

## Concrete exact-source defect and causal limit

[Exact product distributed-runtime-contract.test.sh](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/7b1424420f8616d163a7ef1826999f2392840648/tests/distributed-runtime-contract.test.sh), lines 226–227, calls:

```bash
run_rel="$(cd "$case_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs \
  bash "$claim_owner" --controller d48-c02 "${case_id,,}")" || return 1
```

The substitution captures stdout only. The enclosing `prepared="$(prepare_fencing_case ...)"` also captures stdout only. The three-case D48-C02 loop and its default aggregate preserve stderr.

The exact product source chain is:
1. `claim-run.sh` line 585 obtains a 32-hex claim ID from 16 bytes of `/dev/urandom`.
2. Its `controller_io bind` branch, line 278, invokes `rotation_io initialization-prepare`.
3. `claim-run-rotation.py` lines 4513–4514 builds `refs/implementaudit/controller-initializations/<controller>/<claim_id>`.
4. Line 4584 returns that fresh reference plus the blob OID.
5. Line 4797 prints the initialization-pending token to stderr.
6. The D48 test does not capture or validate that emitted line before it enters whole stderr.

This is a source-proven volatile diagnostic path in the exact product and report interval. It is a strong, narrow candidate for the observed stderr failure. The public artifact cannot authenticate its literal bytes at raw 93079; no 128-byte span content survived. Its span hashes cannot recover the unknown claim IDs/OIDs, prove the exact emitter, or establish complete output equality after a correction.

The stdout residual is still unlocalized. This D48 diagnostic path alone is not an explanation of normalized stdout offset 178528.

The product7b commit's earlier fixes concerned a different continuity race diagnostic and a different protected-effect summary. Their accepted focused evidence remains at its own scope; full25 is fresh evidence that the full relation still fails. No old full24/private byte was substituted here.

## Smallest justified next action

**Recommended actual discriminator:** on a suitable ordinary host using the exact product7b source and required ordinary prerequisites, run the existing maintained selector:

```bash
bash tests/distributed-runtime-contract.test.sh --cell D48-C02
```

This selector invokes the three fencing cases and the existing `distributed_generation_fence.py` companion. Preserve complete stdout, stderr, exit, source/runtime identity, and cleanup. The relevant observation is the actual initialization-token diagnostic joined to each disposable case's actual `.claimed` claim ID and freshly read initialization ref/OID. One bounded observation can identify the emitter; any repeated relation test must be limited to that changed producer and needed controls, not the whole suite.

**Smallest prospective source correction:** in `prepare_fencing_case`, capture the claim call's full stderr in the existing disposable fixture, validate the exact expected initialization line against that fresh claim and actual Git ref/OID before checkpointing, and preserve every additional diagnostic. After all existing assertions succeed, expose only deterministic test-owned summaries. Keep the real claim operation, author/activate/resume/currentness checks, protected mutation assertions, exit handling, and comparator predicates unchanged. Merely discarding stderr or teaching the comparator to ignore arbitrary tokens would remove evidence and is not the recommended correction.

A demonstrated producer correction requires actual retained output and affected semantic controls. It cannot be awarded from the present public hashes or source inspection. Even after that local correction is demonstrated, stdout remains a separate missing discriminator. Do not commission another complete pair until each known residual has a decision-useful observation and justified response.

A future actual full pair must still receive full original captures/transitive outputs under the adopted relation and live custody, then independent live proof review, separate Root consumption, and post-review closing rechecks. A terminal hash artifact cannot retroactively supply skipped live stages.

## Exact original M2/G2 predicate still missing

The original48 disposition at the recovered checkpoint preserves these exact original texts:

**R35-V03:** “Run legacy and DAG on the same exact identified candidate and complete mapped population; retain raw outputs and compare exact accepted normalization/evidence/currentness semantics. A passing subset, changed candidate, or overlay-only result has a lower explicit scope.”

**R35-V02** additionally requires every obligation to map exactly once with input identity, dependency/order, environment/toolchain, writer/resource constraint, stdout/stderr/exit normalization, evidence output/layer, and invalidator.

**R35-V04** expressly states: “A test asserting only zero exit or matched population counts is insufficient.”

Its M2 receiving condition is exactly: “Actual whole equality, independent live public-proof review, separate Root consumption and closing same-job custody.”

Full25 satisfies the actual complete-pair computation and mapping evidence at the artifact's scope. It fails actual whole equality and never reaches the independent live review and separate Root consumption, so it also has no post-review same-job closing conjunction. These are the missing M2/G2 predicates. This does not erase the completed comparison inputs or retroactively invalidate the separately accepted M4/L04 natural-transition episode.

The checkpoint's M2 `FULL25_ACTUAL_COMPLETE_PAIR_IN_PROGRESS` label is a historical pre-terminal snapshot; Root may reconcile it to this actual terminal outcome. This diagnostic did not modify that matrix.

Source identity for this original requirement read:
- Recovered `DG16_ORIGINAL48_CURRENT_DISPOSITION.json`: 184,828 bytes, SHA-256 `e42027bb96960cb26c9f14c89870b64f72228cae29dd3427b59195bfa9128643`; original-source binding names `ORIGINAL48_CURRENT_MAP_NOV06.json`, commit `585012cbc6b47cb332222c2784481567a482c8a5`, SHA-256 `2128ad1092e194176f84bac358e460c6a46e5a01acfad863bbe564d61b54479f`.
- Actual retained issue209 JSON: 57,092 bytes, SHA-256 `219532dc6019637ac4d5902ce33d342989e9d97eaadc9c165f935cf7e4c0c6a0`. The base issue establishes complete/current/decision-usable JOINs and parent rereading; the exact verifier/M2 formulation above comes from the original48 matrix rather than being misattributed to the base issue body.

R35-V05 preserves unaffected qualified scope and rejects an unexplained perpetual whole-graph rerun. R35-Q02 requires inspecting retained completed operations before a rerun decision. G132 `UNKNOWN_NO_REPLAY` is separate and remains untouched.

## Classification, escalation, and learning

**Classification:** completed computation with failed semantic correspondence and incomplete accepting episode; the receiving refusal is the correct fail-closed response.

**Local source disposition:** the exact D48 test has a concrete uncaptured volatile-diagnostic path. Its correction belongs to test-owned output handling with exact assertions, not production claim semantics or broader normalization.

**Systemic diagnostic disposition:** the exported stderr report interval is useful but insufficient for exact emitter attribution, and stdout has no exported producer location. Loss of live private spans limits retrospective diagnosis; hashes are not recoverable text. The repeated whole-run cost therefore should be controlled by focused producer evidence before requalification, with retained raw focused output and explicit source binding.

**Escalation recommendation:** return to Root for the ordinary authorized focused discriminator and any justified narrow correction. No new authority grant is implied. No escalation into protected G132 or revision of the original acceptance contract is justified.

**Follow-up evidence obligation:** actual source-bound producer output; unchanged semantic assertions and adverse controls for any capture correction; separate stdout localization; then only the applicable original full correspondence and live consuming/closing sequence. This report grants no PASS, original award, currentness, release, closure, or audit completion.
