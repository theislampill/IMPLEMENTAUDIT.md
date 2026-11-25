# DG16 M6 original-48 ledger, v2 (working)

**Authority: NONE. Every status here is a working disposition. Final M6 dispositions remain 0/48.**

Base: published draft `1c6c1f0` (V04 award recorded at `809ca1b`), revised per Root receiving `d8c22d3`. Each row quotes the original statement and binding (up to 25 words) from `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json` original48[i]. Current ordinary comparison subject: frozen `2450417a` / tree `b14577983c5e0ab05225250491efe7363945742c`. Operation subjects stay distinct: M2 `51416b2f`, M4 `05371833`, L04 `7e2b00b3`, G132 `b393a905`, V03 successor `2e72a912`.

## Summary

* Rows: 48. Limbs: 130. Independently receivable portable limbs: 54.
* Working dispositions: WORKING_AWARDED_AND_RECONFIRMED_AT_SCOPE 2; WORKING_AWARDED_AT_SCOPE 5; WORKING_BLOCKED_LIVE_G1 1; WORKING_BLOCKED_LIVE_G3 1; WORKING_HISTORICAL_PRESERVED_PENDING_ROOT_RECORD 1; WORKING_OPEN_CONDITIONAL_NOT_SELECTED 8; WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE 27; WORKING_OPEN_ROOT_RULING 2; WORKING_RECONFIRMED_AT_SCOPE 1.
* AWARDED/RECONFIRMED is used only where a Root decision names the row: V01 (e67142c1, cdba51c, fba28b3); V02 (bd5e065); V03 (e67142c1); V04 (809ca1b); Q02 (1fc726b9); Q04 and Q05 (cdba51c, fba28b3); L04 (585012cb L04_ROOT_DECISION and 6940d94e M4_ROOT_RECEIVING).
* The 18 rows that shared an L04/G3 dependency are split. Each now cites its own M4 Root receiving remainder (6940d94e scoped_row_deltas) and its own portable assertion lines on 2450417a.

## Portable limbs Opus/DG16 executor can run now on 2450417a

One pre-declared ordinary WSL occurrence under the owner standing rule (b677fef) covers every `tests/native-work-graph-cases.py` limb: clean detached checkout of 2450417a with the tree asserted, then `PYTHONDONTWRITEBYTECODE=1 python3 tests/native-work-graph-cases.py <new-dir>`, expecting exit 0 and `native-work-graph.test: ok`. The compiler, the test file and the registry are byte-identical to 71b6315c, where A4 passed all 119 nodes. The run adds an assertion-level receipt on the frozen subject.

| Row | Limb | Proposed check |
|---|---|---|
| R35-P01 | P01.a live base/head/tree/dirty state, issue #209 and four binding amendments, authority | On a clean detached 2450417a checkout record `git rev-parse HEAD HEAD^{tree}`, `git status --porcelain=v2 --untracked-files=all` (expect empty), `gh issue view 209 --json body,comments` read-only with the four binding-comment ids from 585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json binding_comments, and the Root authority line from CONTINUATION.json root. |
| R35-P01 | P01.b donor lineage and concurrent-writer census | `git log --format='%H %an %s' 51416b2f..2450417a` with per-commit owner classification (DG16/DG17/DG18), plus the current branch-head census from CONTINUATION.json branch_heads_at_receiving re-read against `git ls-remote origin`. |
| R35-P02 | P02.a per-delta owner, actual gap, smallest change, discriminator, rollback for DG16 deltas in 2450417a | For each of 5c7634b9, 01c67ee1, d60798ea, ea827457 and the C5 V20 hunks of c7c59245: `git show --stat`, the semantic owner path, the Root finding that motivated it (bd5e065 stale-input, e2c0183c TypeError finding), the named test, and `git revert --no-commit` dry-run on a disposable worktree as rollback evidence. |
| R35-P02 | P02.b preserved failing semantic preimage per delta (absence of an edge is not runtime RED) | On disposable checkouts of 71b6315c and e2c0183c run the named V04 bookend controls from tests/work-graph-verifier-cases.py and retain the failing output; on 2450417a the same controls pass. |
| R35-N01 | N01.a constructed acquisition/derivation from STATE/ROADMAP/plan/phase/task specs with stable node identities (P) | Shared nwg run; check assertions L428-434. |
| R35-N01 | N01.b ADDITIONAL OBLIGATION: an additional ready/dependent/conflicting native obligation with supplied scalar counts unchanged must change the compiled graph/disposition | Shared nwg run; check assertions L486-496. Then report, without editing source, whether any 2450417a test holds a scalar count fixed (grep total_cells/population in tests/). If none exists, Root decides whether node-list form discharges the scalar-count wording. |
| R35-N02 | N02.a blank/missing native source and missing/unknown read-set entries fail closed | Shared nwg run; check assertions L444-467, L506-510. |
| R35-N02 | N02.b CONFLICTING-SOURCE controls | Shared nwg run; check assertions L189-193, L398-410, L480-490. |
| R35-N02 | N02.c unknown owner/schema explicit; duplicate and stale state | Shared nwg run; check assertions L498-504, L520-523. same checkout: `bash tests/work-graph-compiler.test.sh`; expect exit 0; cite L185-195. |
| R35-N02 | N02.d no omission or BLOCKED relabel to close arithmetic | Shared nwg run; check assertions L152-176, L431. |
| R35-N03 | N03.a one normalized versioned schema binds edges, read/write/acceptance/resource/authority, effect, vocabulary, candidate/effect identity | Shared nwg run; check assertions L444-467, L565-576. |
| R35-N03 | N03.b integer/canonical-JSON and schema compatibility | same checkout: `bash tests/work-graph-compiler.test.sh`; expect exit 0; cite L136-200. |
| R35-N04 | N04.a input/graph/dispatch/result traceable by identity; changed bytes invalidate affected use only | Shared nwg run; check assertions L437-442, L468-478, L671-676. |
| R35-N04 | N04.b reused labels with changed bytes rejected | Shared nwg run; check assertions L312-316, L480-484, L735-745. |
| R35-N05 | N05.a zero/one/few cells and few-ready cases keep the no-compiler cheap path | Shared nwg run; check assertions L786-789. |
| R35-N05 | N05.b serial consumption still rechecks drift/currentness | Shared nwg run; check assertions L321-338. |
| R35-D01 | D01.a exactly one DONE/ACTIVE/READY/BLOCKED membership per cell | Shared nwg run; check assertions L431-434. |
| R35-D01 | D01.b correct scalar equation over incomplete census invalid | Shared nwg run; check assertions L486-490. |
| R35-D01 | D01.c completion preserves independently active work | Shared nwg run; check assertions L179-187. |
| R35-D02 | D02.a READY derived from predecessor/JOIN/authority/resource/independence/reversibility/currentness | Shared nwg run; check assertions L152-176, L431-434. |
| R35-D02 | D02.b paired identical nodes with one live prerequisite open/closed; only permitted arm eligible | Shared nwg run; check assertions L578-597. |
| R35-D03 | D03.a roster, ACTIVE occupancy, 0 vs absent vs positive ceiling, reserve; dispatch bounded without forced occupancy | Shared nwg run; check assertions L112-150, L527-541. Retain the per-case observed.json files written under slot-capacity/. |
| R35-D04 | D04.a shared semantic owner serializes across distinct files; read/read not a conflict; independent preimages overlap | Shared nwg run; check assertions L543-563. |
| R35-D05 | D05.a JOIN binds consumer, required set, schema, graph identity; missing/duplicate/unknown/stale/falsely terminal cannot satisfy | Shared nwg run; check assertions L599-622. |
| R35-D06 | D06.a RETURNED-RESULT NORMALIZATION: PARTIAL/NONVERDICT/UNKNOWN/PENDING/INTERRUPTED never satisfy; contradictory PASS envelope refused; FAIL settles FAIL | Shared nwg run; check assertions L623-629, L668-670. |
| R35-D06 | D06.b arrival order, subprocess exit or PASS-like prose cannot create acceptance | Shared nwg run; check assertions L615, L627-629. |
| R35-D06 | D06.c correlated/common-source duplicates do not create independence | Shared nwg run; check assertions L630-665. |
| R35-D06 | D06.d transport-failure envelope | Same 2450417a checkout: `PYTHONDONTWRITEBYTECODE=1 python3 tests/work-graph-completion-cases.py`; expect exit 0. Record the test_failures_and_interruption_preserve_independent_preparation subtest for TRANSPORT_FAILURE (L166-175) and which owner it loads. |
| R35-D07 | D07.a graph change during JOIN forces recompute; suppressed recomputation refused (P semantics) | Shared nwg run; check assertions L321-338, L398-410, L671-676. |
| R35-D08 | D08.a unchanged reminder does not redispatch; material input/context/event changes reconsider | Shared nwg run; check assertions L284-339, L756-759. |
| R35-D09 | D09.a logical-delivery identity holds duplicate effect; independent work stays available; no global mutex (P discriminator) | Shared nwg run; check assertions L565-576. |
| R35-D10 | D10.a R0035 placement uses locality and context cost; prompt-only permission is not containment (portable) | Shared nwg run; check assertions L526-529, L565-571. |
| R35-D11 | D11.a sole governor, exact four child skills, unique audit-andon, L1-L5 authority (no-regression) | Same 2450417a checkout: `bash tests/internal-skill-routing.test.sh && bash tests/internal-skill-topology.test.sh && bash tests/skill-layout-contract.test.sh && python3 tests/audit-andon-return-cases.py`; expect exit 0 for each. Cite the DG17 T3 reconfirmation as corroboration only. |
| R35-D11 | D11.b no child result, clean JOIN or cord pull grants READY/authority/PASS/closure | Shared nwg run; check assertions L606-615. |
| R35-V01 | V01.c applicability to frozen 2450417a | `git diff --stat 379581a8 2450417a -- scripts/verify-package.sh tests/ scripts/` and `git rev-parse 71b6315c:scripts/verify-package.sh 2450417a:scripts/verify-package.sh` (expect equal). Then hand a packet with the population-affecting diff to Root. |
| R35-V02 | V02.b applicability 71b6315c -> 2450417a | `git diff 71b6315c 2450417a -- scripts/work-graph-verifier-task.py` with each hunk classified as property emission, mapping, or bookend validation only. Hand the classification to Root. |
| R35-V05 | V05.a graph-level selective invalidation preserves unaffected qualified evidence | Shared nwg run; check assertions L437-442, L586-597, L671-676. |
| R35-V06 | V06.a held-out topology, graph change during JOIN, interruption, duplicates, common source, shared writer, unknown owner | Shared nwg run; check assertions L520-523, L543-549, L616, L630-684. |
| R35-V07 | V07.a legacy route retained until equivalence; no conversion or retirement | On 2450417a confirm both routes are present and unchanged: `git ls-tree 2450417a scripts/verify-package.sh scripts/run-work-graph-verifier.sh` and blob equality with 71b6315c. Report only; no conversion. |
| R35-R01 | R01.a node touching blocked R0033 scope not READY; independent node stays eligible (P mapping) | Shared nwg run; check assertions L578-586. |
| R35-R02 | R02.a pair current/stale satisfaction receipt on the same node; stale cannot unblock; change forces recompute | Shared nwg run; check assertions L586-603. |
| R35-R05 | R05.a ordinary serial/no-DAG work keeps the cheap path (P boundary) | Shared nwg run; check assertions L786-789. |
| R35-R06 | R06.a observation never establishes effect, dependency, authority, JOIN, PASS or closure (P boundary) | Shared nwg run; check assertions L606-615, L713-721. |
| R35-L01 | L01.a recursive selector traverses ancestry to named root; omitted ancestor/sibling refused even if resealed (P) | Shared nwg run; check assertions L678-684, L764-775. |
| R35-L02 | L02.a completed inputs keep useful preparation successor; separate admission/effect edges; block only exact effect (P) | Shared nwg run; check assertions L152-176, L721-732. |
| R35-L03 | L03.a OUTWARD/FORWARD directions, accepted scope/residuals, bounded future consumer (P) | Shared nwg run; check assertions L684-713. |
| R35-L05 | L05.a MATCHED NEGATIVE: identical facts, no dispatch, checker-clean, fails at runtime conformance | Shared nwg run; check assertions L714-721. |
| R35-L05 | L05.b further negatives: omitted ancestor/sibling; blank root/scope; stale/mixed event; correlated returns; whole parent from partial JOIN | Shared nwg run; check assertions L304-311, L506-510, L630-632, L666-667, L761-775. |
| R35-L06 | L06.a shared-writer, missing-input, capacity, authority blocks preserved; unchanged event no redispatch | Shared nwg run; check assertions L152-176, L284-300, L527-549. |
| R35-Q01 | Q01.b list of changed evaluators/schemas/expected answers/pins since original | `git log --format='%h %s' 51416b2f..2450417a -- tests/ scripts/work-graph-verifier-task.py scripts/qualify-work-graph-verifier*.py fixtures/` with each changed oracle or expected answer tabulated against the fact it derives from. |
| R35-Q02 | Q02.b literal `bash scripts/verify-package.sh` on frozen 2450417a | First inspect the retained 2450417a occurrences (DG17 hosted 45544010026/138969111263 step list; W4/W4b) for a literal invocation. If none exists, pre-declare one ordinary WSL run on a clean 2450417a checkout: `bash scripts/verify-package.sh`. Retain exit, stdout/stderr hashes and classify any failure as runtime RED, acceptance-artifact RED, missing evidence or harness. |
| R35-Q03 | Q03.a shared owners unmodified in the independent slice, or exact integration patches | `git diff --name-status 51416b2f 2450417a`, classified by owner (governor/child/continuity/host/effect, central registry/workflows, builders/installers/manifests, helper maps, portal/index, DG16 graph source/schema/fixtures). Flag every shared-owner path with its DG17 composing commit. |
| R35-Q04 | Q04.b archives and cost on 2450417a | Assemble an applicability packet: the 2450417a archive hashes and sizes from the DG17 receipts, compared with the v4 cap 589824 and reserve 2000 per role (CONTINUATION shared_final_package_candidate.m5_original_budget). Name any leg that is missing. |
| R35-Q05 | Q05.b layer disposition on 2450417a | A table mapping each Q05 layer to its 2450417a evidence locator (source commit, generated inventory, archive hash, isolated install receipt, hosted job 45544010026). Native and public legs are marked as exact pending gates. |

## Rows needing a Root ruling or decision

R35-D01, R35-D02, R35-D03, R35-D04, R35-D05, R35-D06, R35-D07, R35-D08, R35-D09, R35-H01, R35-L01, R35-L02, R35-L04, R35-L06, R35-L07, R35-N01, R35-N02, R35-N03, R35-N04, R35-P01, R35-Q06, R35-Q07, R35-Q08, R35-R01, R35-R02, R35-R03, R35-R04, R35-R05, R35-R06, R35-R07, R35-V04, R35-V05, R35-V06, R35-V07

Sequenced items: **V03**: Luna prepares the launch-ready GO packet, then Root decides, then Opus runs the single 2e72a912 comparison, then the live reviewer and Root close. **Q07**: Root selects the final candidate, then Opus self-reviews, then a fresh non-author cold review, then Root receives the exact CI. **Q08**: nine field limbs are carried (statuses, patches, missing input, commands, verified-on-base, checksum, rollback, draft PR, no-effect).

## Unresolved citations

* R35-P01 P01.d preserve accepted #235–#243 work and custody failures: UNRESOLVED CITATION: no locator for the accepted #235–#243 work or custody failures was found in the inspected sources.
* R35-L07 L07.a triad relation graph guard; TC07 liveness distinctions; TC06 consumer preservation: UNRESOLVED CITATION: no TC06 or TC07 control was found in the 2450417a tests (git grep TC07/TC06 found nothing).
* R35-Q01 Q01.a retained original R53-DAG-* coverage and failing predecessors: UNRESOLVED CITATION: no R53-DAG-* identifiers were found in 2450417a (git grep found nothing). The original coverage locator is unknown.

## Rows

### R35-H01 — WORKING_HISTORICAL_PRESERVED_PENDING_ROOT_RECORD

> Preserve H's exact qualified commit/tree, 104/104 scope, initial 108-vs-104 assertion and three deep-Windows-path failures. Historical acceptance neither becomes successor equivalence nor gets revoked by reopening.
>
> Binding: HIST; applicability comparison, not replay. [H, E]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[0] (id=R35-H01) requirement_exact / original_scope_and_binding_exact`

* **H01.a historical H acceptance: commit/tree, 104/104, initial 108-vs-104 assertion, three deep-Windows-path failures**. Subject `71a7101ade904f5482cbc25c5154e1eadea0c7be` / tree `cc9771854689337d839c2a2e37040dc3ac2caa0d`. Applicability: HIST: applicability comparison only, no replay. Subject is H's own commit/tree, distinct from 2450417a. First unresolved: No Root decision names R35-H01; the only locators are the authority-NONE Nov06 map and the issue amendment. Actor: **Root**.
  * `585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[criterion_id=R35-H01] (authority NONE; operation refs and residual only) retained_evidence_at_scope 'Exact 71a/cc977, 104/104 and failed predecessors remain historical acceptance.'`
  * `585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json amendments[id=issuecomment5312882718] status HISTORICAL_ACCEPTANCE_PRESERVED`
* **H01.b no successor equivalence and no revocation by reopening**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: Comparison against frozen 2450417a: the ledger asserts no equivalence of 2450417a to H. First unresolved: Root has not recorded that H acceptance is carried unchanged into M6 without equivalence. Actor: **Root**.
  * `703f19ae91df7fd8e28211d4033a60445ce231ba:handoff/pro-executor-results-20261115/continuing-execution-20261120-19/dg16-m2/ROOT_ADJUDICATION.json (run 44666584405, job 136057233704, exact 51416 scope) limits/prior_evidence_preserved (no successor transfer)`
  * `disc d8c22d3:CONTINUATION.json active_qualification.owner_recovery_20261124.M6_draft_receiving (RECEIVE_FIRST_POPULATED_DRAFT__REVISE_FOR_FINAL_DISPOSITIONS; final 0/48)`

_No replay is needed. Working disposition only. Working disposition only; final M6 dispositions remain 0/48._

### R35-P01 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Bind live base/head/tree/dirty state, full issue/amendments, authority, donor lineage and concurrent-writer census. Distinguish local reconstruction from real Git/native identity. Preserve accepted #235–#243 work and custody …
>
> Binding: P; task writer. Missing native controller evidence is a named gate, not permission to mint it. [B, E]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[1] (id=R35-P01) requirement_exact / original_scope_and_binding_exact`

* **P01.a live base/head/tree/dirty state, issue #209 and four binding amendments, authority**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: Ordinary read-only binding on 2450417a; M2 (51416) and M4 (05371833) observations remain at their own subjects. First unresolved: No binding receipt exists on 2450417a (M2 and M4 bindings are on other subjects). Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `disc 0242f9d2:Root freeze of 2450417a/b1457798 (CONTINUATION active_qualification.2450417a_hosted_freeze)`
  * `703f19ae91df7fd8e28211d4033a60445ce231ba:handoff/pro-executor-results-20261115/continuing-execution-20261120-19/dg16-m2/ROOT_ADJUDICATION.json (run 44666584405, job 136057233704, exact 51416 scope) original_linked_rows includes R35-P01 (no automatic_whole_row_awards)`
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-P01] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false)`
* **P01.b donor lineage and concurrent-writer census**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: Ordinary census at the 2450417a freeze; DG17 composed 2450417a (parent 9bcb39c2). First unresolved: No complete lineage/concurrent-writer census bound to 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `disc d8c22d3:CONTINUATION.json branch_heads_at_receiving / staffing`
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-P01] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false) remaining 'full lineage/concurrent-writer scopes remain as recorded'`
* **P01.c local reconstruction vs real Git/native identity; missing native controller is a named gate**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: Portable refusal on 2450417a is receivable; real native controller identity was observed only at M4. First unresolved: Root has not ruled whether the M4 controller observation plus the 2450417a refusal discharge the native-identity distinction. Actor: **Root**.
  * `2450417a:tests/native-work-graph-cases.py L779-784 (blob 098c1320, byte-identical at 71b6315c) (--native-run refuses 'continuity': no native controller in checkout)`
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-P01] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false) (native controller observed at M4 subject 05371833 only)`
* **P01.d preserve accepted #235–#243 work and custody failures**. Subject `n/a` / tree `n/a`. Applicability: Applies to historical PR/issue records #235–#243. First unresolved: UNRESOLVED CITATION: no locator for the accepted #235–#243 work or custody failures was found in the inspected sources. Actor: **Opus/DG16 executor**.
  * `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[1] (id=R35-P01) requirement_exact / original_scope_and_binding_exact`
* **P01.e per-operation custody for M1 (G1) and M3 (G3)**. Subject `b393a9057c249335e6cdf4ccbb898d192b0830b8` / tree `72850420c768ff5c5f4a8e9a406a564873434c23`. Applicability: Live; G132 source b393a905 is the operation subject, distinct from 2450417a. First unresolved: No eligible host and no G3 window or grant. Actor: **Root**.
  * `disc d8c22d3:CONTINUATION.json active_qualification.owner_recovery_20261124.g132_measurement state SPENT_STOP (45544754821; image 20261116.133.1; Git differed; bwrap absent)`
  * `disc d8c22d3:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.owner_recovery_20261124.G3 'Planning rendezvous only; no live window or grant.'`
  * `disc 7a1d498d:discussions/DG16-DG17-reader-bindings.md '## Root receiving of the sender inputs, prospective host decision and W4b' (offline host engineering authorized; no operational adoption)`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-P02 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Bind each change to existing semantic owner, actual gap, smallest change, discriminator and rollback. Preserve a failing semantic preimage; absence of a proposed file/test/registry edge …
>
> Binding: P; R0035. Shared owner hunks stay separate. [B, N, E]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[2] (id=R35-P02) requirement_exact / original_scope_and_binding_exact`

* **P02.a per-delta owner, actual gap, smallest change, discriminator, rollback for DG16 deltas in 2450417a**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: Each delta is in the 2450417a ancestry; shared-owner hunks must be listed separately. First unresolved: No consolidated per-delta owner/gap/discriminator/rollback table is bound to 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `src 5c7634b9 'Emit v4 all-obligation verifier task properties (R35-V02)'`
  * `src 01c67ee1`
  * `src d60798ea 'Rederive read-population bookends before ESTABLISHED'`
  * `src ea827457 'Classify malformed read-population bookends instead of raising' (= 2450417a)`
  * `src c7c59245 DG16 single delivery (V02 + V04 + C5 V20)`
* **P02.b preserved failing semantic preimage per delta (absence of an edge is not runtime RED)**. Subject `71b6315c5a9437b31ed9df1dd9ec63f3aa44726f` / tree `6491fd78220a77bafc1d912cae8024cfc14b2213`. Applicability: The preimages are on 71b6315c and e2c0183c, not 2450417a. First unresolved: The retained failing preimage bytes are not cited per delta. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `disc bd5e065:discussions/DG16-DG17-reader-bindings.md '## Root consolidated acceptance on 71b6315c…' (stale inner digest accepted as ESTABLISHED on 71b6315c)`
  * `disc d8c22d3:reader-bindings '## Root decision on the joined e2c0183c source' (JSON array/object status raised TypeError)`
* **P02.c M1 reference: the prospective G132 source change**. Subject `b393a9057c249335e6cdf4ccbb898d192b0830b8` / tree `72850420c768ff5c5f4a8e9a406a564873434c23`. Applicability: Applies to the G132 source line, not 2450417a. First unresolved: The prospective measured .133.1 profile change is not yet drafted or reviewed. Actor: **Opus/DG16 executor**.
  * `disc 7a1d498d:discussions/DG16-DG17-reader-bindings.md '## Root receiving of the sender inputs, prospective host decision and W4b' (offline host engineering authorized; no operational adoption)`
  * `disc d8c22d3:CONTINUATION.json active_qualification.owner_recovery_20261124.g132_measurement state SPENT_STOP (45544754821; image 20261116.133.1; Git differed; bwrap absent)`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-N01 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Derive the native population from bound STATE/ROADMAP, controller/epoch/receipt where available, plan/phase/task specifications and stable node identities. Counterexample: an additional ready/dependent/conflicting native obligation leaves supplied scalar …
>
> Binding: P for constructed acquisition/derivation controls; NATIVE for genuine preimage acquisition. R0038 may supply facts, never native or compiler authority. [N, E]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[3] (id=R35-N01) requirement_exact / original_scope_and_binding_exact`

* **N01.a constructed acquisition/derivation from STATE/ROADMAP/plan/phase/task specs with stable node identities (P)**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P binding; constructed controls are its declared scope. First unresolved: No assertion-level receipt on 2450417a; A4 node PASS is on 71b6315c (byte-identical blobs). Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L55-105 (fixture/write_run) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L428-434 (acquisition CONSTRUCTED_FILESYSTEM; node count equals population) (blob 098c1320, byte-identical at 71b6315c)`
  * `disc d8c22d3:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.v20.DG16_V02 (A4 on 71b6315c: 119 nodes passed; registry scripts/verify-package.sh L767-L769 runs work-graph-compiler/native-work-graph/work-graph-verifier tests; registry blob cc4d076f identical at 2450417a)`
* **N01.b ADDITIONAL OBLIGATION: an additional ready/dependent/conflicting native obligation with supplied scalar counts unchanged must change the compiled graph/disposition**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. The counterexample must hold the supplied scalar counts unchanged; the native fixture state carries a node list, not a scalar total. First unresolved: No located control holds a supplied scalar count unchanged while an extra native obligation is present: L486-490 holds the STATE node list, and WGC L189-191 changes the scalar. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L486-496 (OMITTED obligation: STATE list unchanged -> refuse 'population'; declared -> node count +1 and digest changes) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/work-graph-compiler.test.sh L189-191 (v1 projection: count mismatch refused 'frontier count') (blob 76dbce99, byte-identical at 71b6315c)`
* **N01.c genuine native preimage acquisition (NATIVE)**. Subject `05371833d30e81815475d0d00aa107b6be5fbba3` / tree `d5a35d88ae08df60a48ad758ffc2fe5482de6083`. Applicability: NATIVE; observed only at the M4 operation subject. First unresolved: No authentic whole-parent/M3 population; G3 has no window or grant. Actor: **Root**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-N01] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false) delta 'Seven-node native population acquired…'; remaining 'Whole-parent census and authentic M3 population remain outside this slice.'`
  * `disc d8c22d3:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.owner_recovery_20261124.G3 'Planning rendezvous only; no live window or grant.'`

_Scalar-count obligation kept as its own limb (N01.b). Working disposition only; final M6 dispositions remain 0/48._

### R35-N02 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Exhaustive census fails closed on missing, duplicate, unknown, stale or contradictory native state; do not omit it or relabel it BLOCKED to close arithmetic. Unknown …
>
> Binding: P; R0035/compiler. [B, N]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[4] (id=R35-N02) requirement_exact / original_scope_and_binding_exact`

* **N02.a blank/missing native source and missing/unknown read-set entries fail closed**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P; R0035/compiler is the whole binding. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L444-467 (read_set pop/MISSING/UNKNOWN/null sha/CALLER_SATISFIED refuse 'binding'; MISSING_INPUT explicit) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L506-510 (blank root/original_scope refuse 'non-empty') (blob 098c1320, byte-identical at 71b6315c)`
* **N02.b CONFLICTING-SOURCE controls**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. Root named this limb as receivable apart from G3. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L486-490 (spec obligation absent from STATE census refuses 'population') (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L189-193 (DONE contradicts open required) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L398-410 (input or STATE changed during intake refuses) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L480-484 (rehashed tampered READY refuses 'source-derived') (blob 098c1320, byte-identical at 71b6315c)`
* **N02.c unknown owner/schema explicit; duplicate and stale state**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No duplicate-node control on the native (read_native_run_v1) path was located; duplicate is covered only in the v1 projection. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L498-504 (unknown task metadata, symlink refuse) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L520-523 (unknown_owner refuse 'member') (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/work-graph-compiler.test.sh L185-195 (unknown state, duplicate cell id refused in v1 projection) (blob 76dbce99, byte-identical at 71b6315c)`
* **N02.d no omission or BLOCKED relabel to close arithmetic**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L152-177 (missing input -> BLOCKED with reason MISSING_INPUT; C2/SIB preserved) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L431 (blob 098c1320, byte-identical at 71b6315c)`
* **N02.e exhaustive whole-campaign native census (Nov06 M3 ref)**. Subject `05371833d30e81815475d0d00aa107b6be5fbba3` / tree `d5a35d88ae08df60a48ad758ffc2fe5482de6083`. Applicability: Binding is P only; M3 comes from the authority-NONE Nov06 map. First unresolved: Root has not ruled whether a live census is required beyond the P binding. Actor: **Root**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-N02] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false) remaining 'No new missing/duplicate/unknown/stale-source negative execution or exhaustive whole-campaign census.'`
  * `585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[criterion_id=R35-N02] (authority NONE; operation refs and residual only)`
  * `disc d8c22d3:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.owner_recovery_20261124.G3 'Planning rendezvous only; no live window or grant.'`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-N03 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> One normalized versioned schema binds dependency/JOIN edges, semantic read/write/acceptance/resource/authority sets, effect/reversibility/authorization, node/result vocabulary, candidate/tree/worktree and external-effect identity. Preserve integer/canonical-JSON and schema compatibility.
>
> Binding: P; R0035 graph contract; caller assertions do not authenticate facts. [B, N, E]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[5] (id=R35-N03) requirement_exact / original_scope_and_binding_exact`

* **N03.a one normalized versioned schema binds edges, read/write/acceptance/resource/authority, effect, vocabulary, candidate/effect identity**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P graph contract; caller assertions cannot authenticate facts. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L41-53 (node schema fields) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L565-576 (effect/logical_delivery identity) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:skills/implementaudit/scripts/compile-work-graph.py L3374-3441 (result vocabulary and field set) (blob e4b70503, byte-identical at 71b6315c)`
* **N03.b integer/canonical-JSON and schema compatibility**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: Root has not ruled whether these portable compatibility controls answer the M4 remaining 'No broad schema compatibility'. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:skills/implementaudit/scripts/compile-work-graph.py L459 (non-negative integer required) (blob e4b70503, byte-identical at 71b6315c)`
  * `2450417a:tests/work-graph-compiler.test.sh L136-200 (blob 76dbce99, byte-identical at 71b6315c)`
* **N03.c actual normalized native schema at a live episode**. Subject `05371833d30e81815475d0d00aa107b6be5fbba3` / tree `d5a35d88ae08df60a48ad758ffc2fe5482de6083`. Applicability: Observed at M4 only. First unresolved: Live limb from Nov06 M3 ref only; Root ruling needed. Actor: **Root**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-N03] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false)`
  * `disc d8c22d3:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.owner_recovery_20261124.G3 'Planning rendezvous only; no live window or grant.'`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-N04 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Input, graph, dependencies, writer/resources, dispatch, result and invalidators remain traceable by exact identity. Source/schema/registry/dependency/writer/resource/evidence/currentness changes invalidate affected use. Reused labels with changed bytes are rejected.
>
> Binding: P; R0035 consumes existing currentness/fencing owners. [N; original H01]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[6] (id=R35-N04) requirement_exact / original_scope_and_binding_exact`

* **N04.a input/graph/dispatch/result traceable by identity; changed bytes invalidate affected use only**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L437-442 (input change invalidates PREP, preserves SIB) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L468-478 (mode change invalidates) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L671-676 (RECOMPUTE_REQUIRED) (blob 098c1320, byte-identical at 71b6315c)`
* **N04.b reused labels with changed bytes rejected**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L480-484 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L312-316 (forged resealed source_graph refuses) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L735-745 (binding mismatch on foreign or changed input) (blob 098c1320, byte-identical at 71b6315c)`
* **N04.c schema/registry/resource change counterexample**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No graph-level schema- or registry-change invalidation control was located in nwg/wgc. Actor: **Opus/DG16 executor**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-N04] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false) remaining 'No new changed-source/schema/registry/resource invalidation counterexample'`
  * `disc d8c22d3:handoff/astra-dg16-dg18/DG16_V01_V03_ROOT_ADJUDICATION.json decisions[R35-V01].why (registry add/remove rebuilds population)`
* **N04.d live currentness/fencing owners consumed (Nov06 M3 ref)**. Subject `05371833d30e81815475d0d00aa107b6be5fbba3` / tree `d5a35d88ae08df60a48ad758ffc2fe5482de6083`. Applicability: Observed at M4. First unresolved: Root ruling on whether M3 is required beyond P. Actor: **Root**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-N04] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false)`
  * `disc d8c22d3:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.owner_recovery_20261124.G3 'Planning rendezvous only; no live window or grant.'`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-N05 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Zero/one/fewer-than-three cells, one ready cell, strict chain, limited host/ceiling, unknown independence/authority, irreversible effects or unfavorable coordination value preserve serial/no-compiler cheap paths. Serial consumption still rechecks …
>
> Binding: P; R0022 ancestry and R0035 composition. No mandatory graph artifact, agent count or utilization target. [B, N, E]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[7] (id=R35-N05) requirement_exact / original_scope_and_binding_exact`

* **N05.a zero/one/few cells and few-ready cases keep the no-compiler cheap path**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P; no mandatory graph artifact. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L786-789 (cheap_path_v1) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:skills/implementaudit/scripts/compile-work-graph.py L3301-3307 (census contradiction refused) (blob e4b70503, byte-identical at 71b6315c)`
* **N05.b serial consumption still rechecks drift/currentness**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L321-338 (history cannot suppress changed input/context/event) (blob 098c1320, byte-identical at 71b6315c)`
* **N05.c cheap path never waives a consequential JOIN; strict chain, limited ceiling, unknown independence/authority, irreversible effect**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No located control shows that the cheap path keeps a consequential JOIN, or covers strict-chain and irreversible-effect inputs. Actor: **Opus/DG16 executor**.
  * `2450417a:skills/implementaudit/scripts/compile-work-graph.py L3301-3307 (blob e4b70503, byte-identical at 71b6315c)`

_No M-operation reference. Working disposition only; final M6 dispositions remain 0/48._

### R35-D01 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Closed native population satisfies exactly one DONE/ACTIVE/READY/BLOCKED membership per cell. A correct scalar equation over an incomplete native census is still invalid. Completion of one …
>
> Binding: P; R0035 with R0022. Original N08/H02. [B, N]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[8] (id=R35-D01) requirement_exact / original_scope_and_binding_exact`

* **D01.a exactly one DONE/ACTIVE/READY/BLOCKED membership per cell**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L431-434 (blob 098c1320, byte-identical at 71b6315c)`
* **D01.b correct scalar equation over incomplete census invalid**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L486-490 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/work-graph-compiler.test.sh L189-191 (blob 76dbce99, byte-identical at 71b6315c)`
* **D01.c completion preserves independently active work**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L179-187 (ACTIVE custody retained) (blob 098c1320, byte-identical at 71b6315c)`
* **D01.d live closed native population (Nov06 M3 ref)**. Subject `05371833d30e81815475d0d00aa107b6be5fbba3` / tree `d5a35d88ae08df60a48ad758ffc2fe5482de6083`. Applicability: Binding P; live only via the Nov06 ref. First unresolved: Root ruling on whether a live census is required. Actor: **Root**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-D01] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false) remaining 'No whole-campaign census; one container READY is not a second executed cell.'`
  * `disc d8c22d3:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.owner_recovery_20261124.G3 'Planning rendezvous only; no live window or grant.'`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-D02 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> READY derives from actual predecessor, JOIN, authority, write/acceptance/resource, independence, reversibility and currentness closure. Pair identical nodes with one live prerequisite open/closed; only the permitted arm …
>
> Binding: P; R0035. [B]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[9] (id=R35-D02) requirement_exact / original_scope_and_binding_exact`

* **D02.a READY derived from predecessor/JOIN/authority/resource/independence/reversibility/currentness**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: Binding is P only ([B]). First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L431-434 (ADMIT BLOCKED, PREP READY, QUALIFY BLOCKED) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L152-176 (blob 098c1320, byte-identical at 71b6315c)`
* **D02.b paired identical nodes with one live prerequisite open/closed; only permitted arm eligible**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L578-597 (same SIB: route BLOCKED/stale vs SATISFIED) (blob 098c1320, byte-identical at 71b6315c)`
* **D02.c native paired prerequisite (Nov06 M3 ref)**. Subject `05371833d30e81815475d0d00aa107b6be5fbba3` / tree `d5a35d88ae08df60a48ad758ffc2fe5482de6083`. Applicability: Binding is P only; this limb exists only through the authority-NONE Nov06 ref. First unresolved: Root ruling on whether this limb applies. Actor: **Root**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-D02] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false) remaining 'No new paired open/closed native prerequisite family'`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-D03 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Capacity uses actual host/operator roster, occupied ACTIVE work, `0` versus absent versus positive ceiling, rollback margin and value. Dispatch stays bounded, without erasing safe useful …
>
> Binding: P; graph selection consumes real evidence; NATIVE if actual host capacity is claimed. Original N07/B01/B02. [B, E, L]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[10] (id=R35-D03) requirement_exact / original_scope_and_binding_exact`

* **D03.a roster, ACTIVE occupancy, 0 vs absent vs positive ceiling, reserve; dispatch bounded without forced occupancy**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L112-150 (slot_capacity_controls, 12 cases) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L527-541 (ceilings 0/1/None; host_capacity 1) (blob 098c1320, byte-identical at 71b6315c)`
* **D03.b no actual host-capacity claim (NATIVE only if claimed)**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: No native capacity is claimed. First unresolved: Root has not recorded that no native capacity claim is made. Actor: **Root**.
  * `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[10] (id=R35-D03) requirement_exact / original_scope_and_binding_exact`

_No M-operation reference. Working disposition only; final M6 dispositions remain 0/48._

### R35-D04 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Shared semantic owner/acceptance/resource/effect serializes even across distinct files or lane names. Genuinely independent preimages can overlap; a shared eventual product alone does not create a …
>
> Binding: P; R0035 decisions. Actual safe delegated execution is R0036/host integration. Original P02/N03. [B, L]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[11] (id=R35-D04) requirement_exact / original_scope_and_binding_exact`

* **D04.a shared semantic owner serializes across distinct files; read/read not a conflict; independent preimages overlap**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L543-563 (CONFLICT deferral; read/read eligible; ACTIVE writer blocks) (blob 098c1320, byte-identical at 71b6315c)`
* **D04.b actual safe delegated execution (R0036/host integration)**. Subject `05371833d30e81815475d0d00aa107b6be5fbba3` / tree `d5a35d88ae08df60a48ad758ffc2fe5482de6083`. Applicability: Integration/live. First unresolved: No live two-cell overlap; G3 has no window or grant. Actor: **Root**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-D04] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false) remaining 'No two-cell shared semantic writer, concurrent overlap or isolation discriminator.'`
  * `disc d8c22d3:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.owner_recovery_20261124.G3 'Planning rendezvous only; no live window or grant.'`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-D05 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Every consequential JOIN binds consumer, exact required cell/lane set, result schema/statuses, dispatch/consumption graph identity, source/evidence/candidate, independence, sole writer and recompute trigger. Missing/duplicate/unknown/stale/falsely terminal inputs cannot …
>
> Binding: P; R0035 JOIN, R0036 lane-envelope interface. Original N01/A01/A02. [B, N]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[12] (id=R35-D05) requirement_exact / original_scope_and_binding_exact`

* **D05.a JOIN binds consumer, required set, schema, graph identity; missing/duplicate/unknown/stale/falsely terminal cannot satisfy**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L599-622 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:skills/implementaudit/scripts/compile-work-graph.py L3374-3427 (unknown JOIN consumer, dispatch mismatch, contradictory terminal PENDING) (blob e4b70503, byte-identical at 71b6315c)`
* **D05.b optional omission declared before dispatch with evidence ceiling**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No located control shows that an undeclared optional omission is refused. Actor: **Opus/DG16 executor**.
  * `2450417a:tests/native-work-graph-cases.py L652-658 (optional C2) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:skills/implementaudit/scripts/compile-work-graph.py L3441-3466 (omitted_optional reported) (blob e4b70503, byte-identical at 71b6315c)`
* **D05.c whole consequential live JOIN**. Subject `05371833d30e81815475d0d00aa107b6be5fbba3` / tree `d5a35d88ae08df60a48ad758ffc2fe5482de6083`. Applicability: Live (Q06/G3). First unresolved: No G3 window or grant. Actor: **Root**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-D05] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false) remaining 'Whole consequential JOIN is not satisfied'`
  * `disc d8c22d3:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.owner_recovery_20261124.G3 'Planning rendezvous only; no live window or grant.'`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-D06 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Parent normalizes terminal, nonterminal, PARTIAL, UNKNOWN, NONVERDICT, transport failure and contradictory success envelopes. All required results settle; arrival order, subprocess exit or PASS-like prose cannot …
>
> Binding: P; R0035 consumes existing R0031/R0036 vocabulary. Original N05/N06. [B, N]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[13] (id=R35-D06) requirement_exact / original_scope_and_binding_exact`

* **D06.a RETURNED-RESULT NORMALIZATION: PARTIAL/NONVERDICT/UNKNOWN/PENDING/INTERRUPTED never satisfy; contradictory PASS envelope refused; FAIL settles FAIL**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P; Root named this limb as receivable apart from G3. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L623-629 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L668-670 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:skills/implementaudit/scripts/compile-work-graph.py L3423-3427 (contradictory PASS / terminal PENDING) (blob e4b70503, byte-identical at 71b6315c)`
* **D06.b arrival order, subprocess exit or PASS-like prose cannot create acceptance**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No located control covers PASS-like prose. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L615 (partial arrival PENDING) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L628-629 (exit_code 1 with PASS refused) (blob 098c1320, byte-identical at 71b6315c)`
* **D06.c correlated/common-source duplicates do not create independence**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L630-665 (shared key, common read, transitive and optional sources -> NONVERDICT; disjoint closure SATISFIED) (blob 098c1320, byte-identical at 71b6315c)`
* **D06.d transport-failure envelope**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: The located TRANSPORT_FAILURE control exercises the completion-contract consumer (scripts/work-graph-completion.py), not reconcile_native_results_v1. Root has not ruled whether that consumer counts as the parent normalizer. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:skills/implementaudit/scripts/compile-work-graph.py L3400 (TRANSPORT_FAILURE in status set) and L3441-3442 (settles FAIL) (blob e4b70503, byte-identical at 71b6315c)`
  * `2450417a:tests/work-graph-completion-cases.py L166-175 (TRANSPORT_FAILURE never SATISFIED; independent preparation preserved; completion contract owner)`
* **D06.e live normalization of real returns (Nov06 M3 ref)**. Subject `05371833d30e81815475d0d00aa107b6be5fbba3` / tree `d5a35d88ae08df60a48ad758ffc2fe5482de6083`. Applicability: That M4 remainder is a portable family (D06.a-c); the binding is P. First unresolved: Root ruling on whether D06.a-c discharge the M4 remainder. Actor: **Root**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-D06] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false) remaining 'No new PARTIAL/UNKNOWN/NONVERDICT/failure/common-cause negative family.'`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-D07 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Before consequential consumption, reread current affected live owner/source, reconcile authority, fence stale results, recompute dependencies/JOIN/conflicts/capacity/eligibility, consume via sole current writer, then expose new frontier. Test …
>
> Binding: P semantics plus I/NATIVE for actual governor intake/consumption. Original N02/N04/H01. [B, N]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[14] (id=R35-D07) requirement_exact / original_scope_and_binding_exact`

* **D07.a graph change during JOIN forces recompute; suppressed recomputation refused (P semantics)**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P semantics. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L671-676 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L321-338 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L398-410 (blob 098c1320, byte-identical at 71b6315c)`
* **D07.b actual governor intake/consumption via sole current writer (I/NATIVE)**. Subject `05371833d30e81815475d0d00aa107b6be5fbba3` / tree `d5a35d88ae08df60a48ad758ffc2fe5482de6083`. Applicability: I/NATIVE. First unresolved: No G3 window or grant. Actor: **Root**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-D07] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false) remaining 'No full changed-graph-during-JOIN or suppressed-recompute native pair; M3 remains open.'`
  * `disc d8c22d3:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.owner_recovery_20261124.G3 'Planning rendezvous only; no live window or grant.'`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-D08 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Material completion/blockage/drift/authorization/resource/continuity events trigger reconsideration; an unchanged event/reminder does not redispatch accepted work. L4/interruption fences affected results without inferring other ACTIVE=0; partial useful results retain …
>
> Binding: P; R0035 interfaces with governor/R0037, not loop ownership. Original B03/H02/H03/H04. [B, L]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[15] (id=R35-D08) requirement_exact / original_scope_and_binding_exact`

* **D08.a unchanged reminder does not redispatch; material input/context/event changes reconsider**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L284-339 (reminder_controls) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L756-759 (blob 098c1320, byte-identical at 71b6315c)`
* **D08.b interruption fences only affected results; partial results keep scope**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P; the V04 award supplies verifier-level interruption evidence on 2450417a. First unresolved: No located control for compaction, authorization or resource event families. Actor: **Opus/DG16 executor**.
  * `2450417a:tests/native-work-graph-cases.py L623-627 (INTERRUPTED) (blob 098c1320, byte-identical at 71b6315c)`
  * `disc 809ca1b:CONTINUATION.json 2450417a_hosted_freeze.V04 scope (W3 actual partial interrupted NONVERDICT/BLOCKED)`
* **D08.c governor/R0037 loop interface (Nov06 M3 ref)**. Subject `05371833d30e81815475d0d00aa107b6be5fbba3` / tree `d5a35d88ae08df60a48ad758ffc2fe5482de6083`. Applicability: Interface only. First unresolved: Root ruling on whether this limb applies. Actor: **Root**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-D08] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false)`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-D09 — WORKING_OPEN_CONDITIONAL_NOT_SELECTED

> Conflict and retry admission recognize logical-delivery identity and pending/unknown effects across transaction IDs. Matching route-independent labels cannot authorize a duplicate send/effect. Independent unrelated effects/read-only work …
>
> Binding: P for discriminator/graph consumer, I/NATIVE for R0030 effect and R003A attribution inputs. [B reconciliation; current triad TC03]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[16] (id=R35-D09) requirement_exact / original_scope_and_binding_exact`

* **D09.a logical-delivery identity holds duplicate effect; independent work stays available; no global mutex (P discriminator)**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L565-576 (UNKNOWN same-logical-delivery -> LOGICAL_DELIVERY_HELD; PREP still selected) (blob 098c1320, byte-identical at 71b6315c)`
* **D09.b R0030 effect and R003A attribution inputs (I/NATIVE; conditional C5)**. Subject `n/a` / tree `n/a`. Applicability: Conditional C5; no protected UNKNOWN or exactly-once claim is selected. First unresolved: Root has not ruled that C5 is not triggered for D09. Actor: **Root**.
  * `585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[criterion_id=R35-D09] (authority NONE; operation refs and residual only)`
  * `703f19ae91df7fd8e28211d4033a60445ce231ba:handoff/pro-executor-results-20261115/continuing-execution-20261120-19/dg16-m2/ROOT_ADJUDICATION.json (run 44666584405, job 136057233704, exact 51416 scope) not_awarded includes C5`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-D10 — WORKING_BLOCKED_LIVE_G1

> Context-aware placement uses actual locality, governor/child context cost and return-compression usefulness; effect-capability admission is enforceable at the actual executor. Prompt-only read-only is not containment. Keep …
>
> Binding: R0035 placement; I with R0036/host effect owners; NATIVE for physical containment and overlap. [B reconciliation]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[17] (id=R35-D10) requirement_exact / original_scope_and_binding_exact`

* **D10.a R0035 placement uses locality and context cost; prompt-only permission is not containment (portable)**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P for R0035 placement. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L526-529 (placements) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L565-571 (EFFECT_EXECUTOR_UNAVAILABLE) (blob 098c1320, byte-identical at 71b6315c)`
* **D10.b effect admission enforceable at the actual executor; physical containment (NATIVE, M1)**. Subject `b393a9057c249335e6cdf4ccbb898d192b0830b8` / tree `72850420c768ff5c5f4a8e9a406a564873434c23`. Applicability: Live G1 on the G132 source line. First unresolved: No eligible host. The prospective .133.1 profile and pinned provisioning change are not drafted. Actor: **Opus/DG16 executor**.
  * `disc d8c22d3:CONTINUATION.json active_qualification.owner_recovery_20261124.g132_measurement state SPENT_STOP (45544754821; image 20261116.133.1; Git differed; bwrap absent)`
  * `disc 7a1d498d:discussions/DG16-DG17-reader-bindings.md '## Root receiving of the sender inputs, prospective host decision and W4b' (offline host engineering authorized; no operational adoption)`
  * `disc d8c22d3:CONTINUATION.json owner_recovery_20261124.host (enforceable containment required, not image-preinstalled bwrap)`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-D11 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Sole governor, exact four child skills, one child per derivation/return/re-derivation, unique direct `audit-andon`, and L1–L5 authority survive. A skill, child result, clean JOIN, direct cord …
>
> Binding: P no-regression; I if any shared owner changes. Original A01/A02/A03. [B, A]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[18] (id=R35-D11) requirement_exact / original_scope_and_binding_exact`

* **D11.a sole governor, exact four child skills, unique audit-andon, L1-L5 authority (no-regression)**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: DG17 T3 belongs to another cell, so it is supporting evidence only and does not award D11. First unresolved: No DG16 receipt binds D11 to 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `disc d8c22d3:CONTINUATION.json 2450417a_hosted_freeze.compatible_DG17_reconfirmations (DG17 T3 on 2450417a: sole governor plus four children; DG17 scope)`
  * `disc d8c22d3:handoff/astra-dg16-dg18/BB781F62_ORIGINAL_AWARDS.json decisions[T3] (bb781f62)`
* **D11.b no child result, clean JOIN or cord pull grants READY/authority/PASS/closure**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L606-615 (JOIN authority NONE) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:skills/implementaudit/scripts/compile-work-graph.py L3466 (lifecycle_credit NONE) (blob e4b70503, byte-identical at 71b6315c)`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-V01 — WORKING_RECONFIRMED_AT_SCOPE

> Derive the complete live verifier obligation population from actual canonical source/registry, including prelude/inline checks and final/build/currentness semantics. No fixed 104 or later observed count; new/removed/reordered …
>
> Binding: P mapping; central registry I. [N; actual verify-package]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[19] (id=R35-V01) requirement_exact / original_scope_and_binding_exact`

* **V01.a complete live verifier obligation population at exact source scope**. Subject `51416b2f156b341c4a5f09029e2c6ceb5b30b1e7` / tree `9c3913ceaa95f3f36b0377fe2dba4a302afcba89`. Applicability: Awarded at the 51416 scope. First unresolved: None at that scope. Actor: **Root**.
  * `disc d8c22d3:handoff/astra-dg16-dg18/DG16_V01_V03_ROOT_ADJUDICATION.json decisions[R35-V01] ACCEPT_AT_EXACT_CURRENT_SOURCE_POPULATION_SCOPE (src e67142c1)`
  * `disc d8c22d3:handoff/astra-dg16-dg18/ROOT_RECEIVING_02.json new_original_awards`
  * `703f19ae91df7fd8e28211d4033a60445ce231ba:handoff/pro-executor-results-20261115/continuing-execution-20261120-19/dg16-m2/ROOT_ADJUDICATION.json (run 44666584405, job 136057233704, exact 51416 scope)`
* **V01.b reconfirmations at b30ef328 and 379581a8**. Subject `b30ef328c9a22f68ab420c84dc87e849fd4e4599` / tree `d79487990b4fcad5fac823c76c48406822732f13`. Applicability: Reconfirmed on b30ef328 and on 379581a8. First unresolved: None at those scopes. Actor: **Root**.
  * `disc cdba51c5:CONTINUATION.json active_qualification.v18.root_A2_and_M5.V01`
  * `disc fba28b30:CONTINUATION.json active_qualification.v19.DG16_A3_B2_M5_R2 (379581a8/4379d1f3)`
* **V01.c applicability to frozen 2450417a**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: Ordinary comparison: the registry is unchanged from 71b6315c, where A4 covered 119 nodes. First unresolved: Root has not bound V01 to 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `disc d8c22d3:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.v20.DG16_V02 (A4 on 71b6315c: 119 nodes passed; registry scripts/verify-package.sh L767-L769 runs work-graph-compiler/native-work-graph/work-graph-verifier tests; registry blob cc4d076f identical at 2450417a)`
  * `src: scripts/verify-package.sh blob cc4d076f identical 71b6315c and 2450417a`

_Root names this row. The M6 disposition is still working, not final. Working disposition only; final M6 dispositions remain 0/48._

### R35-V02 — WORKING_AWARDED_AT_SCOPE

> Every property/obligation maps exactly once to one node or composed JOIN with input identity, dependency/order, environment/toolchain, writer/resource constraint, stdout/stderr/exit normalization, evidence output/layer and invalidator. Coverage …
>
> Binding: P compiler-specific map; consumer acceptance I. [N]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[20] (id=R35-V02) requirement_exact / original_scope_and_binding_exact`

* **V02.a exactly-once property/obligation map at canonical no-argument registry scope**. Subject `71b6315c5a9437b31ed9df1dd9ec63f3aa44726f` / tree `6491fd78220a77bafc1d912cae8024cfc14b2213`. Applicability: Awarded on 71b6315c; three argument-mode rows are inapplicable. First unresolved: None at that scope. Actor: **Root**.
  * `disc bd5e0655:CONTINUATION.json active_qualification.v20.DG16_V02 AWARD_ORIGINAL_R35_V02_AT_CANONICAL_NO_ARGUMENT_REGISTRY_SCOPE (699 rows; 696 PASS; 3 argument-mode inapplicable)`
* **V02.b applicability 71b6315c -> 2450417a**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: Ordinary comparison: two of the changed paths are verifier-task owner files. First unresolved: No classification yet shows whether d60798ea or ea827457 touch the property emitter or the mapping. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `src `git diff --name-only 71b6315c 2450417a`: 8 paths incl. scripts/work-graph-verifier-task.py, tests/work-graph-verifier-cases.py (V04 bookend corrections)`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-V03 — WORKING_AWARDED_AT_SCOPE

> Run legacy and DAG on the same exact identified candidate and complete mapped population; retain raw outputs and compare exact accepted normalization/evidence/currentness semantics. A passing …
>
> Binding: P executable qualification; I if mapping needs reserved hooks. [N, E]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[21] (id=R35-V03) requirement_exact / original_scope_and_binding_exact`

* **V03.a legacy and DAG on same candidate, full mapped population, five normalized relations**. Subject `51416b2f156b341c4a5f09029e2c6ceb5b30b1e7` / tree `9c3913ceaa95f3f36b0377fe2dba4a302afcba89`. Applicability: Awarded at the 51416 scope. Raw stdout/stderr/portal/repro equality is false and is retained. First unresolved: None at that scope. Actor: **Root**.
  * `disc d8c22d3:handoff/astra-dg16-dg18/DG16_V01_V03_ROOT_ADJUDICATION.json decisions[R35-V03] ACCEPT_AT_EXACT_PORTABLE_EXECUTABLE_CORRESPONDENCE_SCOPE (run 44666584405)`
  * `703f19ae91df7fd8e28211d4033a60445ce231ba:handoff/pro-executor-results-20261115/continuing-execution-20261120-19/dg16-m2/ROOT_ADJUDICATION.json (run 44666584405, job 136057233704, exact 51416 scope) full_relations_equal; raw equality false`
* **V03.b successor comparison on frozen 2e72a912 (review7 policy)**. Subject `2e72a912136607e464e953c71fc8e2b44d047d92` / tree `192970f5103fc46d3c303a93d775eb83c04d2734`. Applicability: Subject 2e72a912 is distinct from 2450417a. Using it for M6 would need a later Root applicability decision. First unresolved: SEQUENCE: (1) Luna prepares one launch-ready GO packet (official-origin, ancestry and new-ref checks; ZIP access; confirmed live reviewer /root/cold2e72 and Root availability with closing-readback time) -> (2) Root decision (GO or no-GO) -> (3) Opus pushes the single comparison -> (4) the live reviewer and Root close in the same job -> (5) Root decides V03 at successor scope. Step 1 is not done. Actor: **Luna**.
  * `disc bd5e0655:CONTINUATION.json census_successor.DG16_V02_V03_V04_20261124.V03.review7 ADOPT_POLICY_ONE_PROSPECTIVE_EPISODE; launch NOT_AUTHORIZED_BY_THIS_ADOPTION`
  * `disc d8c22d3:handoff/astra-dg16-dg18/v03-2e72-r2-adoption/ROOT_POLICY_ADOPTION.json (sha256 7bdb723d…)`
  * `disc dd11482:reader-bindings 'V03 r2 run commit staged and unpublished, launch preflight PASS'`
* **V03.c b30ef328 P3 raw inequality**. Subject `b30ef328c9a22f68ab420c84dc87e849fd4e4599` / tree `d79487990b4fcad5fac823c76c48406822732f13`. Applicability: Retained adverse evidence. First unresolved: None; retain as recorded. Actor: **Root**.
  * `disc:reader-bindings L1211 (preserve observed raw inequality; after-the-fact volatile rule does not qualify P3)`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-V04 — WORKING_AWARDED_AT_SCOPE

> Missing/duplicate/unknown/reordered/stale/falsely settled obligations fail closed. Include nonzero, partial/nonverdict and interrupted cases; preserve legacy fail-fast observables when translating to all-settled results. A test asserting only zero …
>
> Binding: P controls with fixed oracle/normalization; I for canonical semantics acceptance. [N]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[22] (id=R35-V04) requirement_exact / original_scope_and_binding_exact`

* **V04.a fail-closed obligations incl. nonzero, partial/nonverdict, interrupted; legacy fail-fast observables**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: Awarded on 2450417a. Retained result-consumer limits: 'W4 P4 per-case exceptions unavailable after W3 archive-mode failure. No underlying run repeated. No M6 final disposition.' First unresolved: None at that scope. Actor: **Root**.
  * `disc 809ca1bc:CONTINUATION.json active_qualification.2450417a_hosted_freeze.V04 AWARD_ORIGINAL_R35_V04_AT_CANONICAL_COMPARISON_AND_SETTLEMENT_SCOPE (reviewer /root/w3_original_receiving; W4 47cf35ba; W4b 5901e002)`
  * `disc 809ca1bc:reader-bindings '## Root decisions on original V04 and exact-source T10'`
* **V04.b M6 binding of the award**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: Same subject as the current comparison work. First unresolved: Root has not recorded the M6 disposition. Actor: **Root**.
  * `disc d8c22d3:CONTINUATION.json active_qualification.owner_recovery_20261124.M6_draft_receiving (RECEIVE_FIRST_POPULATED_DRAFT__REVISE_FOR_FINAL_DISPOSITIONS; final 0/48)`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-V05 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Selective invalidation reruns the affected valid dependency/consumer scope exactly, preserving unaffected qualified evidence without stale/common-cause reuse. Graph/schema/registry drift rebuilds/requalifies the map conservatively; it does not …
>
> Binding: P; R0035 mapping with R0032 acceptance. [N, E]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[23] (id=R35-V05) requirement_exact / original_scope_and_binding_exact`

* **V05.a graph-level selective invalidation preserves unaffected qualified evidence**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L437-442 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L586-597 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L672-676 (blob 098c1320, byte-identical at 71b6315c)`
* **V05.b verifier-level selective rerun of affected scope without stale/common-cause reuse; drift rebuilds map**. Subject `51416b2f156b341c4a5f09029e2c6ceb5b30b1e7` / tree `9c3913ceaa95f3f36b0377fe2dba4a302afcba89`. Applicability: The M2 leg (full correspondence) is met at 51416; the selective-rerun predicate is separate. First unresolved: No executed selective verifier rerun preserving unaffected qualified evidence was located. Actor: **Root**.
  * `703f19ae91df7fd8e28211d4033a60445ce231ba:handoff/pro-executor-results-20261115/continuing-execution-20261120-19/dg16-m2/ROOT_ADJUDICATION.json (run 44666584405, job 136057233704, exact 51416 scope)`
  * `disc d8c22d3:DG16_V01_V03_ROOT_ADJUDICATION.json decisions[R35-V01].why (rebuild on add/remove/reorder)`
  * `585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[criterion_id=R35-V05] (authority NONE; operation refs and residual only) (Nov06 G2 residual predates M2 at 703f19ae)`
* **V05.c actual new generation and stale old return (M3)**. Subject `n/a` / tree `n/a`. Applicability: Live. First unresolved: No G3 window or grant. Actor: **Root**.
  * `disc d8c22d3:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.owner_recovery_20261124.G3 'Planning rendezvous only; no live window or grant.'`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-V06 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Held-out topology, concurrent graph change during JOIN, interrupted node, duplicate evidence, common source, shared semantic writer, unknown owner/schema, undeclared order and global-state coupling alter the …
>
> Binding: P qualification; NATIVE only for claimed host behavior. [N]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[24] (id=R35-V06) requirement_exact / original_scope_and_binding_exact`

* **V06.a held-out topology, graph change during JOIN, interruption, duplicates, common source, shared writer, unknown owner**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P qualification. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L678-684 (held-out transition) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L671-676 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L616 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L630-665 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L543-549 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L520-523 (blob 098c1320, byte-identical at 71b6315c)`
* **V06.b undeclared order and global-state coupling**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No undeclared-order or global-state-coupling control was located. Actor: **Opus/DG16 executor**.
  * `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[24] (id=R35-V06) requirement_exact / original_scope_and_binding_exact`
* **V06.c environment/resource isolation recorded (NATIVE only if host behavior claimed, M1)**. Subject `b393a9057c249335e6cdf4ccbb898d192b0830b8` / tree `72850420c768ff5c5f4a8e9a406a564873434c23`. Applicability: Live only if a host claim is made. First unresolved: Root has not ruled whether any host-behavior claim is made. If one is, it needs G1. Actor: **Root**.
  * `disc d8c22d3:CONTINUATION.json active_qualification.owner_recovery_20261124.g132_measurement state SPENT_STOP (45544754821; image 20261116.133.1; Git differed; bwrap absent)`
  * `disc 7a1d498d:discussions/DG16-DG17-reader-bindings.md '## Root receiving of the sender inputs, prospective host decision and W4b' (offline host engineering authorized; no operational adoption)`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-V07 — WORKING_OPEN_CONDITIONAL_NOT_SELECTED

> Preserve legacy route until equivalence passes; separately review/switch/read back canonical local/CI/package/install/public consumers; only then consider retirement under R0022/R0032 with rollback and remaining-consumer accounting. Before switch …
>
> Binding: P prepares exact patches; I/REVIEW/OWNER perform conversion; OWNER performs retirement. Neither is authorized now. [N, E]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[25] (id=R35-V07) requirement_exact / original_scope_and_binding_exact`

* **V07.a legacy route retained until equivalence; no conversion or retirement**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: Conditional C2/C3; neither is authorized now. First unresolved: Root has not recorded retention as the working disposition. Actor: **Root**. *(portable, executable now)*
  * `disc d8c22d3:DG16_V01_V03_ROOT_ADJUDICATION.json conversion_or_retirement=false`
  * `703f19ae91df7fd8e28211d4033a60445ce231ba:handoff/pro-executor-results-20261115/continuing-execution-20261120-19/dg16-m2/ROOT_ADJUDICATION.json (run 44666584405, job 136057233704, exact 51416 scope) not_awarded includes canonical conversion, legacy retirement`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-R01 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Consume current R0033 obligation and blocking-scope facts. A node consuming/mutating that scope is not READY, cannot dispatch or satisfy JOIN; a mechanically independent node that …
>
> Binding: P mapping; R0033 owns obligation/scope; R0038 projection only. [R]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[26] (id=R35-R01) requirement_exact / original_scope_and_binding_exact`

* **R01.a node touching blocked R0033 scope not READY; independent node stays eligible (P mapping)**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P mapping. The test labels it a proposed typed consumer, not an adopted producer interface. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L578-586 (blob 098c1320, byte-identical at 71b6315c)`
* **R01.b authentic current R0033 obligation/scope facts consumed**. Subject `05371833d30e81815475d0d00aa107b6be5fbba3` / tree `d5a35d88ae08df60a48ad758ffc2fe5482de6083`. Applicability: R0033 owns the facts; this is not G3-specific. First unresolved: No authentic R0033 producer interface is adopted. Actor: **Root**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-R01] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false) remaining 'route_facts is empty: no new active R0033 route-obligation native consumer discriminator.'`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-R02 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Changed obligation state/generation, binding generation, continuity generation, scope or satisfaction receipt forces affected recomputation. A stale satisfaction receipt cannot unblock. Pair current/stale receipt with the …
>
> Binding: P consumer; I/NATIVE for authentic producer/currentness. [R, E]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[27] (id=R35-R02) requirement_exact / original_scope_and_binding_exact`

* **R02.a pair current/stale satisfaction receipt on the same node; stale cannot unblock; change forces recompute**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P consumer. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L586-597 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L598-603 (ROUTE_PRODUCER_UNAVAILABLE) (blob 098c1320, byte-identical at 71b6315c)`
* **R02.b authentic producer/currentness (I/NATIVE)**. Subject `05371833d30e81815475d0d00aa107b6be5fbba3` / tree `d5a35d88ae08df60a48ad758ffc2fe5482de6083`. Applicability: I/NATIVE. First unresolved: No authentic route producer is adopted. Actor: **Root**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-R02] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false) remaining 'No new changed route-obligation generation or stale satisfaction receipt native pair.'`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-R03 — WORKING_OPEN_CONDITIONAL_NOT_SELECTED

> An interlock requires all nine prerequisites: stable current node/graph; exact R003A host session/object; delegated R0036 executor/task mapping; current route facts; current dependency/authority/writer/resources; bounded authorized effect …
>
> Binding: P comparator only if admitted owner/failure exists; I/NATIVE for missing prerequisite. Do not silently default any field to current/trusted. [R, E]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[28] (id=R35-R03) requirement_exact / original_scope_and_binding_exact`

* **R03.a all nine interlock prerequisites; none defaults to current/trusted**. Subject `n/a` / tree `n/a`. Applicability: Conditional C1 native interlock; no prevention claim is selected. The P comparator applies only if an admitted owner exists, and none does. First unresolved: Root has not ruled that C1 is not triggered. Actor: **Root**.
  * `585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[criterion_id=R35-R03] (authority NONE; operation refs and residual only)`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-R04 — WORKING_OPEN_CONDITIONAL_NOT_SELECTED

> For the qualified bound action, matching current request may allow; stale graph/binding/route generation, foreign task/executor, changed custody, wrong effect class, open currentness/authority or contradictory mapping …
>
> Binding: P comparator/control; NATIVE prevention only after covered trusted hook qualification. [R]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[29] (id=R35-R04) requirement_exact / original_scope_and_binding_exact`

* **R04.a allow matching current request, deny stale/foreign/changed/contradictory; preserve bounded actions**. Subject `n/a` / tree `n/a`. Applicability: Conditional C1 native interlock; no prevention claim is selected. First unresolved: Root has not ruled that C1 is not triggered. No comparator control was located on 2450417a. Actor: **Root**.
  * `585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[criterion_id=R35-R04] (authority NONE; operation refs and residual only)`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-R05 — WORKING_OPEN_CONDITIONAL_NOT_SELECTED

> Unbound arbitrary tools stay outside this conditional interlock. Unsupported host path or disabled/untrusted/timed-out hook is unavailable, not prevention. Ordinary serial/no-DAG work keeps cheap path. Target …
>
> Binding: P boundary controls; NATIVE activation/coverage. [R]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[30] (id=R35-R05) requirement_exact / original_scope_and_binding_exact`

* **R05.a ordinary serial/no-DAG work keeps the cheap path (P boundary)**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: Conditional C1 native interlock; no prevention claim is selected. This boundary no-regression control is independent of activation. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L786-789 (blob 098c1320, byte-identical at 71b6315c)`
* **R05.b unbound tools outside; unavailable/untrusted hook is not prevention (NATIVE activation)**. Subject `n/a` / tree `n/a`. Applicability: Conditional C1 native interlock; no prevention claim is selected. First unresolved: Root has not ruled that C1 is not triggered. Actor: **Root**.
  * `585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[criterion_id=R35-R05] (authority NONE; operation refs and residual only)`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-R06 — WORKING_OPEN_CONDITIONAL_NOT_SELECTED

> Neither pre-event allow nor post-event observation establishes intended world effect, dependency satisfaction, authority, mutation permission, currentness, route satisfaction, JOIN, PASS or closure. PostToolUse cannot cure …
>
> Binding: P/R0035 boundary plus R0038 observation interface. [R]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[31] (id=R35-R06) requirement_exact / original_scope_and_binding_exact`

* **R06.a observation never establishes effect, dependency, authority, JOIN, PASS or closure (P boundary)**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: Conditional C1 native interlock; no prevention claim is selected. P boundary. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L719-721 (source-consistent no-dispatch rejected 'missing execution') (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L606-615 (JOIN authority NONE) (blob 098c1320, byte-identical at 71b6315c)`
* **R06.b PostToolUse cannot cure failed precondition (R0038 interface)**. Subject `n/a` / tree `n/a`. Applicability: Conditional C1 native interlock; no prevention claim is selected. First unresolved: Root has not ruled that C1 is not triggered. Actor: **Root**.
  * `585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[criterion_id=R35-R06] (authority NONE; operation refs and residual only)`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-R07 — WORKING_OPEN_CONDITIONAL_NOT_SELECTED

> Interlock rollback removes only admitted adapter/route edge while preserving unchanged graph/lane/obligation/governor checks. Retirement considers coverage, exact mapping, equivalent host-native enforcement and protected-effect cost. No generic …
>
> Binding: P prepares; I/OWNER effects. [R, E]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[32] (id=R35-R07) requirement_exact / original_scope_and_binding_exact`

* **R07.a interlock rollback/retirement (P prepares; I/OWNER effects)**. Subject `n/a` / tree `n/a`. Applicability: Conditional C1 native interlock; no prevention claim is selected. C3 is also conditional. First unresolved: Root has not ruled that C1/C3 are not triggered. Actor: **Root**.
  * `585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[criterion_id=R35-R07] (authority NONE; operation refs and residual only)`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-L01 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> At accepted material RETURN/JOIN or re-derivation, traverse applicable ancestry to an explicitly named same-campaign root and reconsider applicable siblings/future prerequisites at every ancestor. Bind consuming …
>
> Binding: P recursive compiler/selector; I/NATIVE actual event/native campaign. [L]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[33] (id=R35-L01) requirement_exact / original_scope_and_binding_exact`

* **L01.a recursive selector traverses ancestry to named root; omitted ancestor/sibling refused even if resealed (P)**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P recursive compiler/selector. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L678-684 (ancestors C2/PH/ROOT) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L764-775 (blob 098c1320, byte-identical at 71b6315c)`
* **L01.b actual event / native campaign ancestry (I/NATIVE)**. Subject `05371833d30e81815475d0d00aa107b6be5fbba3` / tree `d5a35d88ae08df60a48ad758ffc2fe5482de6083`. Applicability: I/NATIVE. The historical L04 window2 subject 7e2b00b3 is separate. First unresolved: Root has not ruled whether the M4 or L04 ancestry evidence covers L01. Neither decision awards L01. Actor: **Root**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-L01] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false) remaining 'Whole-campaign ancestry and census are not established'`
  * `585012cb:recovery/contracts/evidence/L04_ROOT_DECISION.json (historical window2, 2026-11-09; other_rows_awarded=[]) accepting_positive.ancestor_and_future_JOIN (L04 shape only)`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-L02 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Completed comparison inputs retain an independently useful preparation successor whenever its actual prerequisites are satisfied. Represent receiving selection, material assessment, admission, source writing and external …
>
> Binding: P R0035 decisions; I with actual consumers. [L, R]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[34] (id=R35-L02) requirement_exact / original_scope_and_binding_exact`

* **L02.a completed inputs keep useful preparation successor; separate admission/effect edges; block only exact effect (P)**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L55-79 (ADMIT vs PREP edges) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L721-732 (PREP/SIB consumed; ADMIT BLOCKED) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L152-176 (blob 098c1320, byte-identical at 71b6315c)`
* **L02.b actual consumers (I)**. Subject `05371833d30e81815475d0d00aa107b6be5fbba3` / tree `d5a35d88ae08df60a48ad758ffc2fe5482de6083`. Applicability: I, observed at M4. First unresolved: Root has not ruled whether the M4 delta discharges the I limb. Actor: **Root**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-L02] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false) delta 'Independent useful exact-candidate review genuinely proceeds… exact G132 effect remains blocked.'`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-L03 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Preserve INWARD decomposition, OUTWARD sibling progress, FORWARD future prerequisite preparation, BACKWARD accepted partial/full JOIN, reconciliation/re-derivation and immediate reconsideration. Keep accepted scope/residuals and pending output's bounded …
>
> Binding: P; R0037 owns loop semantics; R0036 execution. [L, E]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[35] (id=R35-L03) requirement_exact / original_scope_and_binding_exact`

* **L03.a OUTWARD/FORWARD directions, accepted scope/residuals, bounded future consumer (P)**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L684-713 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L67 (future_consumer) (blob 098c1320, byte-identical at 71b6315c)`
* **L03.b INWARD decomposition, BACKWARD partial/full JOIN, reconciliation, no unbounded queue**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P with R0037 loop semantics. First unresolved: No INWARD or BACKWARD control was located in nwg (the edges use only FORWARD/OUTWARD). Actor: **Opus/DG16 executor**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-L03] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false) remaining 'INWARD is empty; no complete recursive-cycle or whole JOIN award.'`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-L04 — WORKING_AWARDED_AT_SCOPE

> Held-out positive has completed comparison inputs, genuinely blocked admission/effect, independent useful preparation with met actual prerequisites, and an ancestor future qualification/JOIN prerequisite. Show actual selected …
>
> Binding: P simulated/portable test consumer can qualify its declared scope; NATIVE remains for one natural material campaign transition. [L, E]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[36] (id=R35-L04) requirement_exact / original_scope_and_binding_exact`

* **L04.a historical held-out natural behavioral witness (window2, 2026-09-11)**. Subject `7e2b00b3a2a16fc6033a5eabe4fc795f6249366f` / tree `6d3f972a424583f9d3d56d8bfd9ae11cf36ecf6e`. Applicability: Historical actor/runtime scope. It does not claim the November code ran in September. First unresolved: None at that scope. Actor: **Root**.
  * `585012cb:recovery/contracts/evidence/L04_ROOT_DECISION.json (historical window2, 2026-11-09; other_rows_awarded=[]) decision ACCEPT_R35_L04_ORIGINAL_HELD_OUT_NATURAL_BEHAVIORAL_WITNESS`
* **L04.b original M4 native natural transition at declared episode**. Subject `05371833d30e81815475d0d00aa107b6be5fbba3` / tree `d5a35d88ae08df60a48ad758ffc2fe5482de6083`. Applicability: Operation subject 05371833, distinct from 2450417a. First unresolved: None at that scope. Actor: **Root**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-L04] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false); top-level decision ACCEPT_ORIGINAL_M4_L04_NATIVE_NATURAL_TRANSITION_AT_DECLARED_EPISODE, criterion R35-L04`
* **L04.c M6 carry-forward**. Subject `n/a` / tree `n/a`. Applicability: It is not in named_current_row_awards_this_phase, by time scope. First unresolved: Root has not recorded the M6 disposition. Actor: **Root**.
  * `disc d8c22d3:CONTINUATION.json active_qualification.owner_recovery_20261124.M6_draft_receiving (RECEIVE_FIRST_POPULATED_DRAFT__REVISE_FOR_FINAL_DISPOSITIONS; final 0/48)`
  * `disc d8c22d3:reader-bindings 'The current-phase award list has a different time scope.'`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-L05 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Matched negative keeps identical source-consistency facts but has no dispatch and no valid edge-specific deferral; it fails despite checker-clean input. Further negatives keep direction labels …
>
> Binding: P controls with fixed behavior oracle; no historical miss gains retroactive credit. [L]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[37] (id=R35-L05) requirement_exact / original_scope_and_binding_exact`

* **L05.a MATCHED NEGATIVE: identical facts, no dispatch, checker-clean, fails at runtime conformance**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P controls with fixed oracle. Root named this limb as receivable apart from G3. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L714-721 (blob 098c1320, byte-identical at 71b6315c)`
* **L05.b further negatives: omitted ancestor/sibling; blank root/scope; stale/mixed event; correlated returns; whole parent from partial JOIN**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L764-775 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L506-510 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L761-763, 304-311 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L630-632 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L666-667 (blob 098c1320, byte-identical at 71b6315c)`
* **L05.c blanket-block of preparation negative**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No explicit negative was located in which blanket-blocking preparation is itself refused. Only positive anti-blanket selections exist. Actor: **Opus/DG16 executor**.
  * `2450417a:tests/native-work-graph-cases.py L152-176 (SIB still selected) (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L565-576 (PREP still selected while SIB held) (blob 098c1320, byte-identical at 71b6315c)`
* **L05.d no retroactive credit for historical misses**. Subject `7e2b00b3a2a16fc6033a5eabe4fc795f6249366f` / tree `6d3f972a424583f9d3d56d8bfd9ae11cf36ecf6e`. Applicability: Historical negatives stay at their own scope. First unresolved: None. Retain as recorded. Actor: **Root**.
  * `585012cb:recovery/contracts/evidence/L04_ROOT_DECISION.json (historical window2, 2026-11-09; other_rows_awarded=[]) negative_scope RECEIVE_ACTUAL_HISTORICAL_OMISSION_AND_ACCEPTED_DIAGNOSTIC_AT_THEIR_SCOPES`
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-L05] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false) remaining 'No new matched-negative execution or retroactive credit.'`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-L06 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Preserve valid shared-writer, unknown-independence, missing-input, real-capacity, authority and exact-boundary blocks. Unchanged event yields no redispatch. Scope mandatory compaction handling to its actual boundary without erasing …
>
> Binding: P graph selection; I with governor/currentness owner. [L]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[38] (id=R35-L06) requirement_exact / original_scope_and_binding_exact`

* **L06.a shared-writer, missing-input, capacity, authority blocks preserved; unchanged event no redispatch**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P graph selection. First unresolved: No assertion-level receipt on 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `2450417a:tests/native-work-graph-cases.py L543-549 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L152-176 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L527-541 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L431-434 (blob 098c1320, byte-identical at 71b6315c)`
  * `2450417a:tests/native-work-graph-cases.py L284-300 (blob 098c1320, byte-identical at 71b6315c)`
* **L06.b unknown-independence block and compaction boundary**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No unknown-independence or compaction-boundary control was located. Actor: **Opus/DG16 executor**.
  * `2450417a:tests/native-work-graph-cases.py L41-53 (independence field) (blob 098c1320, byte-identical at 71b6315c)`
* **L06.c governor/currentness owner integration (I)**. Subject `05371833d30e81815475d0d00aa107b6be5fbba3` / tree `d5a35d88ae08df60a48ad758ffc2fe5482de6083`. Applicability: I. First unresolved: Root has not ruled whether the M4 delta discharges the I limb. Actor: **Root**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-L06] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false)`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-L07 — WORKING_OPEN_CONDITIONAL_NOT_SELECTED

> Triad relation graph is guarded evidence, not cells or precedence. TC07 distinguishes reachable exit, soundness, deadlock freedom and inevitable completion using actual joint config/resources/peers/environment/observation scope/progress …
>
> Binding: P scoped graph guard; R0037/R0039/R0022/R0032 receiving/retirement owners as applicable; stronger native/global claim remains unproved. [L; current TC06/TC07 rows]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[39] (id=R35-L07) requirement_exact / original_scope_and_binding_exact`

* **L07.a triad relation graph guard; TC07 liveness distinctions; TC06 consumer preservation**. Subject `n/a` / tree `n/a`. Applicability: P scoped guard. C3/C4 are conditional, and the stronger global claim stays unproved. First unresolved: UNRESOLVED CITATION: no TC06 or TC07 control was found in the 2450417a tests (git grep TC07/TC06 found nothing). Actor: **Opus/DG16 executor**.
  * `585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[criterion_id=R35-L07] (authority NONE; operation refs and residual only)`
  * `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[39] (id=R35-L07) requirement_exact / original_scope_and_binding_exact`
* **L07.b conditionals C3/C4 not triggered**. Subject `n/a` / tree `n/a`. Applicability: Conditional. First unresolved: Root has not ruled that C3/C4 are not triggered. Actor: **Root**.
  * `585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[criterion_id=R35-L07] (authority NONE; operation refs and residual only)`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-Q01 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Retain original `R53-DAG-*` positive/negative/boundary/adjacent/held-out coverage and actual failing predecessors. Changed evaluators, schemas, expected answers or pins require independent property justification; test output labels must be …
>
> Binding: P plus REVIEW for changed oracle justification. [B, E]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[40] (id=R35-Q01) requirement_exact / original_scope_and_binding_exact`

* **Q01.a retained original R53-DAG-* coverage and failing predecessors**. Subject `n/a` / tree `n/a`. Applicability: P. First unresolved: UNRESOLVED CITATION: no R53-DAG-* identifiers were found in 2450417a (git grep found nothing). The original coverage locator is unknown. Actor: **Opus/DG16 executor**.
  * `703f19ae91df7fd8e28211d4033a60445ce231ba:handoff/pro-executor-results-20261115/continuing-execution-20261120-19/dg16-m2/ROOT_ADJUDICATION.json (run 44666584405, job 136057233704, exact 51416 scope) original_linked_rows includes R35-Q01 (no award)`
* **Q01.b list of changed evaluators/schemas/expected answers/pins since original**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: P. First unresolved: No consolidated changed-oracle list exists. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `src 5c7634b9, 01c67ee1, d60798ea, ea827457 (verifier-task property and bookend oracles)`
  * `src 9b308ac6 (Andon fixture numeric refusal; DG17)`
* **Q01.c independent property justification of each changed oracle (REVIEW)**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: REVIEW. First unresolved: Depends on Q01.b; no reviewer is assigned. Actor: **independent non-author reviewer**.

_Working disposition only; final M6 dispositions remain 0/48._

### R35-Q02 — WORKING_AWARDED_AT_SCOPE

> Run applicable focused baseline/regression controls, then actual canonical `bash scripts/verify-package.sh` on the exact candidate when runnable. Distinguish runtime RED, acceptance-artifact RED, missing evidence and harness/policy/transport …
>
> Binding: P qualification; no invented option or guessed PASS marker. [B, E, A]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[41] (id=R35-Q02) requirement_exact / original_scope_and_binding_exact`

* **Q02.a focused controls then canonical verifier, failure kinds distinguished**. Subject `51416b2f156b341c4a5f09029e2c6ceb5b30b1e7` / tree `9c3913ceaa95f3f36b0377fe2dba4a302afcba89`. Applicability: Awarded at the 51416 scope. First unresolved: None at that scope. Actor: **Root**.
  * `disc d8c22d3:handoff/astra-dg16-dg18/DG16_Q02_ROOT_ADJUDICATION.json ACCEPT_AT_EXACT_51416_WITNESSED_EXECUTION_SCOPE (src 1fc726b9; CI run 44655969487 job 136022135798)`
* **Q02.b literal `bash scripts/verify-package.sh` on frozen 2450417a**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: Ordinary and runnable. Inspect retained operations first. First unresolved: No literal canonical invocation on 2450417a has been located or received. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `disc cdba51c5:CONTINUATION.json v18.root_A2_and_M5.V03_and_Q02 'the literal canonical bash invocation need applicable evidence'`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-Q03 — WORKING_OPEN_PORTABLE_LIMBS_EXECUTABLE

> Shared governor/child/continuity/host/effect owners, central registry/workflows, builders/installers/manifests, helper applicability/load maps and public portal/index remain unmodified in the independent published slice. Deliver necessary exact integration patches and …
>
> Binding: I; graph-specific source/schema/fixtures stay together under R0035. New test registry obligation must remain visible. [E]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[42] (id=R35-Q03) requirement_exact / original_scope_and_binding_exact`

* **Q03.a shared owners unmodified in the independent slice, or exact integration patches**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: I. First unresolved: Root has not named the base for the DG16 slice comparison. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[criterion_id=R35-Q03] (authority NONE; operation refs and residual only)`
  * `disc d8c22d3:CONTINUATION.json shared_final_package_candidate.composition_inputs.integration_base 51416b2f`
* **Q03.b separately identified disposable overlay where lawful**. Subject `n/a` / tree `n/a`. Applicability: I. First unresolved: No overlay is identified. Actor: **Opus/DG16 executor**.

_Working disposition only; final M6 dispositions remain 0/48._

### R35-Q04 — WORKING_AWARDED_AND_RECONFIRMED_AT_SCOPE

> Shipped bytes trigger actual package/inventory/helper-dispatch coverage and isolated copy parity, Windows/POSIX path applicability, exact cost and retirement trigger. Preserve runtime 0.4.0, release v0.4.0.0, both 327,680-byte …
>
> Binding: P build/copy only; I integration/package writer; NATIVE discovery/activation separately. [N, E, A]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[43] (id=R35-Q04) requirement_exact / original_scope_and_binding_exact`

* **Q04.a package/inventory/helper-dispatch/copy parity/path/cost/retirement at applicable scope**. Subject `b30ef328c9a22f68ab420c84dc87e849fd4e4599` / tree `d79487990b4fcad5fac823c76c48406822732f13`. Applicability: Awarded at b30ef328 scope and reconfirmed at 379581a8. The optional alias is unverified. First unresolved: None at those scopes. Actor: **Root**.
  * `disc cdba51c5:CONTINUATION.json active_qualification.v18.root_A2_and_M5['R35-Q04'] ACCEPT (reader-bindings 'Root also awards original R35-Q04')`
  * `disc fba28b30:CONTINUATION.json v19.DG16_A3_B2_M5_R2 reconfirm (379581a8)`
  * `disc d8c22d3:BB781F62_ORIGINAL_AWARDS.json decisions[M5].limits 'Whole Q04/Q05… remain open'`
* **Q04.b archives and cost on 2450417a**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: DG17 clause scope corroborates the 2450417a archives; it does not award Q04. First unresolved: Root has not bound Q04 to the 2450417a archives. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `disc d8c22d3:CONTINUATION.json 2450417a_hosted_freeze.compatible_DG17_reconfirmations (archives rehashed; eb2bf7fd, b1d75acd)`
  * `disc 809ca1bc:CONTINUATION.json 2450417a_hosted_freeze.T10 (cost)`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-Q05 — WORKING_AWARDED_AND_RECONFIRMED_AT_SCOPE

> Source→generated→built→packaged→isolated-installed→discovered/routed/native→hosted/public remain separate evidence legs. Test-only change can mark package leg not triggered; changed packaged runtime cannot. Missing native host is an exact pending gate, …
>
> Binding: P / I / NATIVE by claimed layer. [B, N, R, E]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[44] (id=R35-Q05) requirement_exact / original_scope_and_binding_exact`

* **Q05.a separate source/generated/built/packaged/installed/native/hosted legs**. Subject `b30ef328c9a22f68ab420c84dc87e849fd4e4599` / tree `d79487990b4fcad5fac823c76c48406822732f13`. Applicability: Awarded and reconfirmed. Native discovery and release carry no claim. First unresolved: None at those scopes. Actor: **Root**.
  * `disc cdba51c5:CONTINUATION.json v18.root_A2_and_M5['R35-Q05'] ACCEPT at exact evidence-layer disposition scope`
  * `disc fba28b30:v19 reconfirm (379581a8)`
* **Q05.b layer disposition on 2450417a**. Subject `2450417a3d442e189e20ba261120aff3ed7444c6` / tree `b14577983c5e0ab05225250491efe7363945742c`. Applicability: DG17 T15 corroborates; it does not award Q05. First unresolved: Root has not bound Q05 to 2450417a. Actor: **Opus/DG16 executor**. *(portable, executable now)*
  * `disc d8c22d3:CONTINUATION.json 2450417a_hosted_freeze.compatible_DG17_reconfirmations (T15 layer dispositions)`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-Q06 — WORKING_BLOCKED_LIVE_G3

> One bounded governed live run corroborates at least two independent cells, required JOIN, shared-writer or stale-result boundary, parent normalization and recomputation at exact source/package/host identity. …
>
> Binding: NATIVE; portable simulation is qualified only as simulation. [B F5/terminal acceptance, L, E]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[45] (id=R35-Q06) requirement_exact / original_scope_and_binding_exact`

* **Q06.a one bounded governed live run: two independent cells, JOIN, shared-writer/stale boundary, normalization, recompute**. Subject `n/a` / tree `n/a`. Applicability: NATIVE. Portable simulation qualifies only as simulation. First unresolved: No G3 window, staffing or grant; no eligible G1 host. Actor: **Root**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-Q06] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false) remaining 'At least two independent cells… remain unproved by this run; no Q06 promotion.'`
  * `disc d8c22d3:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.owner_recovery_20261124.G3 'Planning rendezvous only; no live window or grant.'`
  * `disc d8c22d3:CONTINUATION.json active_qualification.owner_recovery_20261124.g132_measurement state SPENT_STOP (45544754821; image 20261116.133.1; Git differed; bwrap absent)`
* **Q06.b L natural-transition requirement preserved separately**. Subject `05371833d30e81815475d0d00aa107b6be5fbba3` / tree `d5a35d88ae08df60a48ad758ffc2fe5482de6083`. Applicability: Satisfied separately by L04. First unresolved: None. Keep it separate unless the same run satisfies both shapes. Actor: **Root**.
  * `6940d94e840c06f51dfe840dea8a2e29f62daaac:handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json scoped_row_deltas[criterion_id=R35-L04] (Root /root, 2026-11-17, run 44076469956; other_27_rows_new_award=false)`
  * `585012cb:recovery/contracts/evidence/L04_ROOT_DECISION.json (historical window2, 2026-11-09; other_rows_awarded=[])`

_Working disposition only; final M6 dispositions remain 0/48._

### R35-Q07 — WORKING_OPEN_ROOT_RULING

> Rigorous self-review plus genuine fresh independent exact-tree cold review with no authoring-context reuse; retain PASS/GAP-REVISE/BLOCKED/OWNER DECISION and review scope. This contract review does not satisfy …
>
> Binding: P self-review; REVIEW exact final candidate; published CI if available. [B, E]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[46] (id=R35-Q07) requirement_exact / original_scope_and_binding_exact`

* **Q07.a applicable final DG16 candidate selected**. Subject `n/a` / tree `n/a`. Applicability: 2450417a is frozen for ordinary comparison work but is not selected as the final candidate. First unresolved: SEQUENCE step 1: Root selects the applicable final candidate. Not done. Actor: **Root**.
  * `disc d8c22d3:CONTINUATION.json active_qualification.owner_recovery_20261124.M6_draft_receiving (RECEIVE_FIRST_POPULATED_DRAFT__REVISE_FOR_FINAL_DISPOSITIONS; final 0/48) ('any material product successor requires Root freeze before final applicability')`
  * `disc 0242f9d2:Root freeze of 2450417a/b1457798 (CONTINUATION active_qualification.2450417a_hosted_freeze)`
* **Q07.b rigorous self-review on the selected candidate**. Subject `n/a` / tree `n/a`. Applicability: P. First unresolved: Blocked on Q07.a. Actor: **Opus/DG16 executor**.
* **Q07.c fresh independent exact-tree cold review, no authoring-context reuse; retain PASS/GAP-REVISE/BLOCKED/OWNER DECISION and scope**. Subject `n/a` / tree `n/a`. Applicability: REVIEW. First unresolved: Blocked on Q07.b. Actor: **independent non-author reviewer**.
  * `disc d8c22d3:reader-bindings '## Root execution decision…' (fresh read-only Claude reviewers eligible for non-author review)`
* **Q07.d CI bound to real PR/merge candidate head/base/tree/run/attempt/job and terminal artifacts**. Subject `n/a` / tree `n/a`. Applicability: Published CI if available. First unresolved: Blocked on Q07.a. Root receives the exact CI. Actor: **Root**.
  * `585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=6].executed (PR255 CI 41403118577 failed; canonical verifier skipped)`

_Order: Root selects -> Opus self-review -> fresh non-author review -> Root receives exact CI. Working disposition only; final M6 dispositions remain 0/48._

### R35-Q08 — WORKING_OPEN_ROOT_RULING

> Return complete criterion statuses (satisfied at scope, inherited/applicable, integration, private input, native, review, reserved authority), pinned interface/patches, narrow missing input, commands/statuses/failures, portable bundle/patch verified on …
>
> Binding: P deliverable; non-closing draft publication only if genuinely supported; OWNER merge/certification/closure later. [E]

Locator: `585012cb:recovery/contracts/original/DEFINITIONS_48_20_117_12.json original48[47] (id=R35-Q08) requirement_exact / original_scope_and_binding_exact`

* **Q08.a complete criterion statuses (satisfied at scope, inherited/applicable, integration, private input, native, review, reserved authority)**. Subject `n/a` / tree `n/a`. Applicability: P deliverable. Owner merge, certification and closure come later. First unresolved: Every other row must reach a final disposition first. Actor: **Opus/DG16 executor**.
  * `585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=6].unresolved`
  * `disc d8c22d3:CONTINUATION.json active_qualification.owner_recovery_20261124.M6_draft_receiving (RECEIVE_FIRST_POPULATED_DRAFT__REVISE_FOR_FINAL_DISPOSITIONS; final 0/48)`
* **Q08.b pinned interface/patches**. Subject `n/a` / tree `n/a`. Applicability: P deliverable. Owner merge, certification and closure come later. First unresolved: Q03.a (owner-classified patch set) is not produced. Actor: **Opus/DG16 executor**.
  * `585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=6].unresolved`
  * `disc d8c22d3:CONTINUATION.json active_qualification.owner_recovery_20261124.M6_draft_receiving (RECEIVE_FIRST_POPULATED_DRAFT__REVISE_FOR_FINAL_DISPOSITIONS; final 0/48)`
* **Q08.c narrow missing input**. Subject `n/a` / tree `n/a`. Applicability: P deliverable. Owner merge, certification and closure come later. First unresolved: Depends on Q08.a. Actor: **Opus/DG16 executor**.
  * `585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=6].unresolved`
  * `disc d8c22d3:CONTINUATION.json active_qualification.owner_recovery_20261124.M6_draft_receiving (RECEIVE_FIRST_POPULATED_DRAFT__REVISE_FOR_FINAL_DISPOSITIONS; final 0/48)`
* **Q08.d commands/statuses/failures (including retained failures)**. Subject `n/a` / tree `n/a`. Applicability: P deliverable. Owner merge, certification and closure come later. First unresolved: No consolidated command log is bound to the selected candidate. Actor: **Opus/DG16 executor**.
  * `585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=6].unresolved`
  * `disc d8c22d3:CONTINUATION.json active_qualification.owner_recovery_20261124.M6_draft_receiving (RECEIVE_FIRST_POPULATED_DRAFT__REVISE_FOR_FINAL_DISPOSITIONS; final 0/48)`
* **Q08.e portable bundle/patch VERIFIED ON BASE**. Subject `n/a` / tree `n/a`. Applicability: P deliverable. Owner merge, certification and closure come later. First unresolved: Root has not named the base, and the final candidate is unselected (Q07.a). Actor: **Root**.
  * `585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=6].unresolved`
  * `disc d8c22d3:CONTINUATION.json active_qualification.owner_recovery_20261124.M6_draft_receiving (RECEIVE_FIRST_POPULATED_DRAFT__REVISE_FOR_FINAL_DISPOSITIONS; final 0/48)`
* **Q08.f manifest/bytes/hashes/CRC (CHECKSUM)**. Subject `n/a` / tree `n/a`. Applicability: P deliverable. Owner merge, certification and closure come later. First unresolved: No bundle exists yet. Actor: **Opus/DG16 executor**.
  * `585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=6].unresolved`
  * `disc d8c22d3:CONTINUATION.json active_qualification.owner_recovery_20261124.M6_draft_receiving (RECEIVE_FIRST_POPULATED_DRAFT__REVISE_FOR_FINAL_DISPOSITIONS; final 0/48)`
* **Q08.g exact branch/worktree/ROLLBACK**. Subject `n/a` / tree `n/a`. Applicability: P deliverable. Owner merge, certification and closure come later. First unresolved: Final candidate is unselected. Actor: **Opus/DG16 executor**.
  * `585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=6].unresolved`
  * `disc d8c22d3:CONTINUATION.json active_qualification.owner_recovery_20261124.M6_draft_receiving (RECEIVE_FIRST_POPULATED_DRAFT__REVISE_FOR_FINAL_DISPOSITIONS; final 0/48)`
* **Q08.h ready draft PR METADATA (non-closing; publication only if genuinely supported)**. Subject `n/a` / tree `n/a`. Applicability: P deliverable. Owner merge, certification and closure come later. First unresolved: Depends on Q07. Publication needs its own authority. Actor: **Root**.
  * `585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=6].unresolved`
  * `disc d8c22d3:CONTINUATION.json active_qualification.owner_recovery_20261124.M6_draft_receiving (RECEIVE_FIRST_POPULATED_DRAFT__REVISE_FOR_FINAL_DISPOSITIONS; final 0/48)`
* **Q08.i no campaign mutation, source adoption, release/certification or denominator credit**. Subject `n/a` / tree `n/a`. Applicability: P deliverable. Owner merge, certification and closure come later. First unresolved: Holds by construction. Root confirms at delivery. Actor: **Root**.
  * `585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=6].unresolved`
  * `disc d8c22d3:CONTINUATION.json active_qualification.owner_recovery_20261124.M6_draft_receiving (RECEIVE_FIRST_POPULATED_DRAFT__REVISE_FOR_FINAL_DISPOSITIONS; final 0/48)`

_Every original Q08 field is carried as its own limb. Working disposition only; final M6 dispositions remain 0/48._
