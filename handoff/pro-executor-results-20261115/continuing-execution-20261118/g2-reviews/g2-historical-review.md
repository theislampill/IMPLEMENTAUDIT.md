# Independent factual review: DG16 G2 run 44193941775

## Identity and boundary

- Reviewer: `/root/g2_independent`.
- Review date: 2026-11-18 UTC.
- `authoring_context_reuse: no`.
- Model, truthful host/self-report: **GPT-6 Astra Pro**. The host instructions supply this label; an exact provider deployment or API model identifier is not exposed to this reviewer.
- Independence evidence: the parent reports that the host spawn used `fork_turns=none`. My starting context consisted of the task and governing instructions, rather than the implementation author's transcript. I have not authored or modified the formatter, validator, comparison implementation, workflow, or policy under review. A static reviewer-name check alone would not prove this separation.
- Role: ordinary independent factual reviewer. This report is not an `audit-assess` child-skill disposition, an acceptance decision, a grant of execution authority, a readiness decision, or audit closure. No formal governor route was supplied or claimed.
- Authority ceiling: read-only inspection and local evidence/report creation. No launch, remote mutation, protected operation, authority grant, or M2 acceptance was performed.
- Governing repository instructions inspected: `/workspace/scratch/095d3235c921/implementaudit/AGENTS.md`, checkout HEAD `d8813ea46a06ce0e9f6260d6adccb4ab30cf4445`.

## Finding

**The historical run completed and received the comparison pair, but did not complete the actual live independent-review and root-consumption gate. It cannot receive a retroactive live-review PASS.** The terminal evidence records `ACTUAL_REVIEW_WINDOW_EXPIRED` for `hold`, `EPISODE_INCOMPLETE` for `finalize`, and final status `UNQUALIFIED_OR_INCOMPLETE`. Its live-review state remains `ACTUAL_REVIEW_REQUIRED`.

The actual proof bytes are internally consistent with the original public-proof validator and record equality of the five declared normalized relations. This is bounded evidence about that historical comparison, with substantial explicitly retained limits. It is not a full G2 award, original acceptance, current private custody, or M2 acceptance.

## Exact evidence received

The root supplied the two downloaded archives and the connected GitHub artifact metadata. I independently computed the local archive digests and inspected the actual contained documents. The provider metadata is reported by the root's `github_fetch_workflow_run_artifacts` call; I did not make a second independent provider call.

| Evidence | Artifact identity | Locally computed SHA-256 |
|---|---|---|
| `evidence/g2-44193941775-review.zip` | GitHub artifact `14389896752`, workflow commit `d2f04874c549816141de002f9baec73dbc9d06fd` | `03d0c600d2d13cb675fa422f06c8b49745f55f225476d06c5d15365f8e212c87` |
| `evidence/g2-44193941775-terminal.zip` | GitHub artifact `14393745910`, provider size 15,886 bytes, same workflow commit | `1a45e1aad5b11d1c6277d1cc302e6da7285f1c1cfc0c0c80ca26c73ed390cb8d` |
| `evidence/g2-44193941775-review/REQUEST.json` | Original live request | `98f4da795b82c8e0992e7500b1e266654078cf79080fecb3b9c32d751ee86a2c` |
| `evidence/g2-44193941775-review/PROOF.json` | Original proof, 4,131 bytes | `360876d3c2409463c6b49692634e7a771ae8c91593e809507d980a298e754352` |
| `evidence/g2-44193941775-review/public/ARTIFACT_MANIFEST.json` | Six public members | `56544181191e52e323c7c4338449939b3e0653e064e7d2f75095315fddcbabc4` |
| `evidence/g2-44193941775-terminal/ARTIFACT_MANIFEST.json` | Six terminal public members | `6cddca14670e38db88ddb98e9f94ef86d5cb8759b6b91ed6a8d5a254d2889b8d` |
| `evidence/g2-44193941775-terminal/RESULT.json` | Terminal status | `78cd167d3135f271aad18539903d0cf4f333c6a414b3079f9969c76119105889` |
| `evidence/g2-44193941775-terminal/FAILURE.json` | Terminal failure records | `a6e74d4f87624b8cf99aa0cdaeabab363872e4b02943cb6e6a8df956c69733d9` |
| `evidence/g2-44193941775-terminal/PROBE.json` | Terminal operation and live-review facts | `eeea0fabe949581f2408aef7aa55077883504fc6144284d856783d482290b788` |
| `evidence/g2-44193941775-terminal/CLEANUP.json` | Terminal cleanup facts | `2eb373b24efc4a8a840536640454ac6615c3bb005f1e87c632c8246d43346ded` |
| `evidence/g2-44193941775-terminal/SOURCE.json` | Terminal source bookends | `9a5bca5cea5392ce9af834ed4603c4a00f7cc09ea36687cd7eb1531cae321cb3` |
| `evidence/g2-44193941775-terminal/HOST.json` | Terminal host observations | `60bf3ab27b0f7192f860b66bef344c194c1a305b5c939849ebaad9f8d9132516` |

All paths above are relative to `/workspace/scratch/095d3235c921/`. The review archive is 18,158 bytes and has nine files; the terminal archive is 15,886 bytes and has seven. I checked that each extracted file exactly matches its archive member, with no duplicate file names or additional extracted files. Both public manifests' listed byte counts and SHA-256 values match their files. The original `host_utility.py` public codec successfully decoded every public file in both packets and verified canonical re-encoding. This included the shared-string encoding in `PROBE.json`; conclusions were drawn from decoded facts, not from unresolved `@` or `$` references.

## Original source, not a later validator

The historical request identifies workflow commit `d2f04874c549816141de002f9baec73dbc9d06fd`, source commit `e91df00685c55c193d288ccdb0f8ffe1e16a9957`, and source tree `df8008fd3d25b1d32f75ec80fa45da22e3fc68ca`. I read the relevant source blobs with `git show` at the exact workflow commit.

| Path under `qualification/dg16-r5-full-g2/` | Original SHA-256 |
|---|---|
| `live_control.py` | `444b8d66f6c554fe1df3490b9db944a8bc5f8371b565f9377a07d168adc5e517` |
| `full_relation.py` | `9e079d7656c513fe32dcf21088cf14405eba599a7d184831566d56d6595e557e` |
| `run.py` | `6a20d3bdadd89cba63e2f578e49bdfa0445b1d40566eef01e7c74f630bc0834f` |
| `host_utility.py` | `02a15dc96ecce23e14a3a84bca880aa536d79fffc4f6d6160835cb4ba97a19b5` |
| `pair_driver.py` | `eeeb3d846a1dbbaf88c9dbbf1c52d3eccc1ea19623198761b3ca5eec4def063d` |
| `POLICY.json` | `b756fc8bcb653798d4096d9469c92920c54f9253db6f9396d0ebb9eae95fbea3` |
| `RELATION_INPUTS.json` | `d36d896f5ca67ea8fd510a42dd794f7e9b2e7928020c5d3038cebc93afb83881` |

The full receiver hash agrees with `REQUEST.json.full_receiver_sha256`. The proof descriptor and private-observation descriptor agree between request and proof. All eight module/data descriptors in `RELATION_INPUTS.json` match their actual original-commit blobs. The actual `ROOT_POLICY_ADOPTION.json` and `INDEPENDENT_COLD_REVIEW.json` blobs match the hashes recorded by the policy gate. The public proof was successfully checked with the original `validate_public_proof` and its pure validation helpers, extracted from the exact source. This was an offline validation of supplied evidence; it did not run the comparison or a live job.

The current checkout's `live_control.py` has a different hash, `2154177c5ad6cc3864407a2f7c0254cb21645d89cb8c45f9cfba247b39e63a88`, and requires a 300-second hold. The historical validator requires exactly **3,600 seconds**. A current-checkout validation is not a substitute for validation against the historical receiver.

## What the historical evidence says

### Comparison evidence

The proof names 119 mapped nodes, 91 registered test scripts, 111 static report slots, and 2,068 statically selected tests. Each actual route has 111 reported slots, 193 skips, and zero expected failures. Those numbers are different populations; they do not mean that 2,068 individual tests all passed.

All five declared normalized relations — `whole`, `portal`, `repro`, `pending_durability`, and `pending_loader` — report equality, zero differences, complete empty witness lists, and matching projection hashes. Normalized stdout and stderr also report equality. The original public-proof validator accepts their shapes and consistency.

The raw relation separately records `raw_observables_equal: false`: raw stdout, raw stderr, portal events, and repro events differ. Normalized equality therefore must be described as equality under the separately adopted relation, not literal equality of all raw outputs. The proof preserves 13 finite rules and six narrowings.

The private-observation descriptor is 7,387,782 bytes with SHA-256 `20d4bf913511250a02ec860a10c9a723b7f5045d1885f96f1e7904c15c5bff3f`. That private file and the complete raw captures were not in either public artifact and were not available to this reviewer. I have not independently recomputed normalized projections from their original private bytes.

The public operation reports `RECEIVED_COMPLETE_RAW_PAIR` and historical same-checkout currentness during receiving. The native prerequisite records `RECEIVED_FRESH_NINE_CASE_CURRENT_HOST` and nine case outcomes of `PASS`. These are inspected historical reported facts, not reruns by this reviewer.

The decoded policy-adoption evidence concerns the **policy gate**, with reviewer `/root/g2_accepting_source_receiver`, adoption hash `51436e8018dbff0cb80473176cc8d18a230995175d0eeba848bbaac9b628034d`, and review hash `98bd546afe5196f4f5397137a9fd9d18075fd67b423d20b6ecf02fadbed2422e`. Its existence does not mean the later review of this actual pair was consumed.

### Missing live-review completion

The request was created at **2026-11-18 01:59:27 UTC** and expires exclusively at **2026-11-18 02:59:27 UTC**. Both clocks at the reservation boundary are required by the original `hold` implementation. An offline call to the original validator at the exact expiry and at observed current time refuses with `ACTUAL_REVIEW_WINDOW_EXPIRED`, before considering a payload. No synthetic PASS payload was needed or generated for this check.

The terminal completed-step list ends at `prepare-review`; it does not include a completed `hold`. The terminal records:

- `RESULT.status: UNQUALIFIED_OR_INCOMPLETE`.
- `RESULT.independent_assessment: false`.
- `PROBE.live_review.status: ACTUAL_REVIEW_REQUIRED`.
- `FAILURE.failures`: `hold / ACTUAL_REVIEW_WINDOW_EXPIRED`; `finalize / EPISODE_INCOMPLETE`.
- `native_prerequisite.closing_currentness_verified_before_teardown: false`.
- No consumed control-commit descriptor, independent-review descriptor, root-consumption descriptor, or post-review closing readback in the public live-review record.

Terminal source bookends match, and terminal cleanup records source/runtime unchanged and all step children reaped. This corrects the pre-closing review snapshot, whose `SOURCE.after` was null and cleanup bookend flags were false. However, the original `run.py` updates the source/runtime cleanup facts **before** requiring the episode to be complete. These true cleanup flags do not imply that the subsequent post-review raw-custody and currentness checks occurred.

The terminal explicitly limits custody to `HISTORICAL_THIS_LIVE_JOB_ONLY; exported hashes convey no currentness`. Private outputs were not uploaded; retention is `LIVE_JOB_ONLY; no universal interrupted-stream retention`.

## What can and cannot receive a PASS claim

| Claim | Bounded judgment |
|---|---|
| Supplied archives match their supplied provider digests; public files match manifests; public documents decode canonically; public proof satisfies the original schema | Verified by this review. A PASS label here would be limited to **PL4 structural validation**. |
| Historical proof records equality of the declared normalized relations | Supported as a hash-bound historical receiver record; not independently recomputed from original private captures by this reviewer. |
| Raw outputs are identical | Contradicted by the raw-relation facts. |
| The historical request received and consumed an actual live independent review | Contradicted by terminal status, failures, and live-review state. |
| The historical request can receive a live-review PASS after expiry | Refused by the original validator; would also misstate the required live private-input scope. |
| Full G2, G1, G3, C5, full T14, original acceptance, audit closure, canonical conversion, legacy retirement, test-level authenticity, or unexported fixture-internal-state equivalence | Not awarded by this report. The relevant proof/result flags explicitly withhold these claims. M2 is not established or accepted. |
| A future explicitly synthetic control rehearsal proves actual full G2 | Unsupported. Such a rehearsal can demonstrate its stated control-transport and reservation mechanics only, with its test domain preserved. |

The repository proof-level meanings are taken from `docs/audits/RETENTION.md`: PL4 is structural validation, PL5 is fixture/example demonstration, PL6 is observed live behavior, and PL7 is fresh-executor proof. This review does not upgrade a structural or fixture result to an observed original G2 outcome.

## Exact original live-control contract

The original `live_control.py` is the source for these requirements:

1. The request must still be unexpired, and its `hold_seconds` must equal 3,600. Each control document is bounded to 4,096 bytes; duplicate JSON keys and nonfinite JSON numbers are refused.
2. The selected repository and control branch are fixed. The control path is exactly `qualification/dg16-full-g2-control/<run_id>-1`.
3. The fetched commit must have exactly one parent, the request's workflow commit. Its entire tree delta must be only additions of the expected regular `100644` control blobs under that exact path. A control STOP has one file; a consumption has exactly three.
4. `CONTROL.json` binds the repository, `/root` publisher, designated successor, run/attempt, workflow commit, raw request hash, proof hash, private-observation hash, and the exact byte-count/hash descriptors of the other two files.
5. `INDEPENDENT_REVIEW.json` has the exact schema `dg16.full-correspondence-independent-live-review.v1`, `authority: NONE`, `decision: PASS`, empty `blocking_findings`, and exact scope `ACTUAL_FULL_CORRESPONDENCE_PROOF_WHILE_PRIVATE_INPUTS_REMAIN_LIVE`. It binds request, proof, private observations, source commit/tree, policy, and adoption hashes. The reviewer must match `/root/[a-z0-9_]+` and must not be in the static `CURRENT_AUTHORS` list.
6. `ROOT_CONSUMPTION.json` must be separately rooted in `/root`, bind the exact independent-review bytes and reviewer, use `CONSUME_AT_DECLARED_SCOPE_SUBJECT_TO_CLOSING_READBACK`, be one-shot, and explicitly preserve `automatic_full_G2_award: false` and unchanged source/product limits.
7. The remote branch head must still match after fetching, reading, and validating the files. Both clocks are rechecked immediately before exclusive durable creation of `CONSUMPTION_RESERVED.json`. A previous reservation prevents repeat consumption.

The parser enforces these bindings, not the truth of a reviewer's professional judgment. A fresh reviewer-looking string cannot establish independent authorship; proof of context separation and actual judgment belongs to the review evidence. The schema cannot encode a truthful needs-evidence or rejection verdict as a consumable `INDEPENDENT_REVIEW.json`. A separate findings report is required when the reviewer cannot support its sole allowed PASS disposition.

## Evidence needed for a future genuine delivery

A new actual run needs its own request and proof, provider artifact identity, workflow/source pins, observed current time and remaining live hold, and evidence that the same job retains the private inputs needed by the receiver and closing checks. Historical IDs, private hashes, or proof bytes cannot be recycled as new currentness.

The reviewer must independently inspect the new actual public proof, public facts, relevant original receiver and normalization logic, and the adopted policy at their bound versions. Any contrary evidence, unsupported identity, unresolved comparison discrepancy, unexplained skips, or missing custody assurance must be resolved before the reviewer can issue the original-schema PASS at its exact scope. Direct independent recomputation from private bytes has not occurred in this historical review; a future conclusion must state its actual evidence basis and cannot claim such recomputation unless performed.

The formatter should accept the actual independent review bytes as input, preserve them byte-for-byte, and require a separately supplied root decision. It must never manufacture reviewer judgment, default to PASS, clear findings, infer independence from a name, replace the author's chosen scope, or turn a negative report into consumable JSON. Independently recorded authoring context, model-label provenance, rationale, reviewed packet hashes, and limitations must accompany the review outside the strict three-file control directory. Those companion facts are not fields permitted by the original control schema.

After valid live consumption, the original job still must finish its mandatory closing sequence. In the original `run.py` this includes revalidating the reserved control data, checking the unchanged adoption, re-reading the original private envelope and raw censuses with the original driver, matching `POST_REVIEW_READBACK.json` to the exact proof/private descriptors, verifying unchanged source/runtime, and verifying current continuity again before teardown. Root consumption is expressly subject to that later readback; the reviewer must not claim that this future event has already happened. Even successful closing does not automatically award full G2 or M2.

## Prospective non-protected rehearsal boundary

The exact original review schema has no fixture scope. A toy proof cannot receive a genuine original-scope independent PASS. A truthful test of the `CONSUME` branch is possible only as a conspicuously isolated synthetic protocol-conformance exercise. A review-shaped test vector may contain the required literal PASS as test data, but it must not be presented as an actual full-correspondence verdict.

Minimum controls for that narrower demonstration are a unique rehearsal-only run ID/control path and branch; immutable request/proof explicitly marked `SYNTHETIC` and `NON_ACCEPTANCE`; a conspicuous rehearsal commit description; an independently authored companion fixture assessment; the exact original source hash; a record of any test-only `CONTROL_BRANCH` or `REMOTE` binding adaptation; real elapsed clocks within the original hold; a real three-file commit and readback; and the actual original `hold` reservation receipt with matching bytes and hashes. A local-mirror remote demonstrates mirror reception, rather than actual live GitHub polling. Only the observed transport should be claimed.

Such a test cannot establish private comparison correctness, live original raw retention, protected custody, post-review original closing, full G2, or M2. If use of a synthetic PASS test vector would be mistaken for a real review, the exact original STOP branch is the honest available demonstration instead. No rehearsal vector, delivery, or approval is issued by this historical report.

## Remaining limits

I inspected the supplied public files and exact original source; I did not observe the historical job live, access its lost private state, rerun the full pair, inspect every historical log line, independently authenticate the provider metadata beyond the root's connected-tool report, or test an as-yet-unprovided formatter. No secret values are reproduced here. No credential exposure finding is asserted from these public evidence files.

The next decision remains with the root: preserve this run as historically incomplete; prepare a clearly bounded test if authorized; provide the formatter and immutable new fixture or actual-run packet for independent review; and retain all readiness, publication, launch, acceptance, and closure authority.
