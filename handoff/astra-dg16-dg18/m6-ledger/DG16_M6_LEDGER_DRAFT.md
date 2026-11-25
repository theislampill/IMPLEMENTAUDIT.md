# DG16 M6 evidence ledger (draft, read-only)

Drafted from disc clone HEAD `47cf35b` (CONTINUATION.json unchanged since `a4064a7`) and `585012cb` contracts. Authority: NONE. This is a draft for Root to check, not a disposition. A row is AWARDED or RECONFIRMED only where a Root decision names that row id. Root's ledger still records DG16 at 3/6 milestones and 0/48 M6 final dispositions.

## Counts

| Disposition | Rows |
|---|---|
| AWARDED | 5 |
| RECONFIRMED | 3 |
| HISTORICAL_PRESERVED | 1 |
| OPEN | 35 |
| BLOCKED_EXTERNAL | 4 |
| UNCLEAR | 0 |

- **AWARDED (5):** V04 (2450417a, Root 809ca1b), V02 (71b6315c), V03 (51416b2f), Q02 (51416b2f), L04 (Nov 9, historical window2 witness).
- **RECONFIRMED (3):** V01 (51416b2f, then b30ef328 and 379581a8), Q04 and Q05 (b30ef328, then 379581a8).
- **HISTORICAL_PRESERVED (1):** H01.

None of the awards sits on a single final candidate. Each still needs Root to bind it into M6.

## Rows by what they wait on

- **Blocked on the G132 operation (G1/G3), BLOCKED_EXTERNAL:** R35-D10, R35-V05, R35-V06, R35-Q06.
- **Wait on G3 unless Root rules that the accepted M4/L04 window2 witness covers them:** R35-N01, R35-N02, R35-N03, R35-N04, R35-D01, R35-D02, R35-D04, R35-D05, R35-D06, R35-D07, R35-D08, R35-R01, R35-R02, R35-L01, R35-L02, R35-L03, R35-L05, R35-L06. Nov06 references these rows to M3+M4 (N/D/R) or to M4 only (L). D07's residual names 'G3 ... and natural L' as alternatives. This is a Root ruling on existing evidence, not engineering.
- **Engineering the DG16 executor (Opus) can do now:** R35-P01, R35-P02, R35-Q01, R35-Q02, R35-Q03, R35-Q08. Also the V03 2e72a912 run after Root GO.
- **Root/reviewer verification of existing evidence only:** awarded or reconfirmed rows R35-H01, R35-V01, R35-V02, R35-V03, R35-L04, R35-Q02, R35-Q04, R35-Q05 (final-candidate binding); conditional or portable rows R35-N05, R35-D03, R35-D09, R35-D11, R35-V07, R35-R03, R35-R04, R35-R05, R35-R06, R35-R07, R35-L07, R35-Q07.
- **R35-V04 AWARDED** on 2450417a (Root 809ca1b). Before the award: W4b has run (5901e00: W3 received through the frozen 2450417a consumer, 28/28 mutations refused), so only Root's whole-V04 adjudication on 2450417a remains.

## Cross-cutting gap

The accepted evidence sits on different subjects: 51416b2f (V01, V03, Q02, M2), b30ef328 and 379581a8 (V01, Q04, Q05, M5), 71b6315c (V02), 2e72a912 (pending V03 successor) and 2450417a (V04 freeze). Q07 and M6 need one exact final candidate, so Root must name it and rule which awards carry forward by dependency comparison.

## Ledger

| # | Row | Grp | Disposition | Requirement (paraphrase) | Gap | Next action | Next actor |
|---|---|---|---|---|---|---|---|
| 1 | R35-H01 | 6 | HISTORICAL_PRESERVED | Preserve historical H acceptance (exact commit/tree, 104/104, 108-vs-104 assertion, three Windows path failures) without successor equivalence or revocation. | No current Root M6 entry records H01's final disposition. | Root records the H01 final disposition as preserved historical acceptance, with no replay and no successor equivalence. | Root |
| 2 | R35-P01 | - | OPEN | Bind live base/head/tree/dirty state, issue and amendments, authority, donor lineage and writer census; separate local reconstruction from real identity. | Per-operation preflight row referencing M1-M5. Needs a final-candidate preflight binding plus G1/G3 operation custody, and G132 has not run. | Opus assembles the preflight receipts for each accepted operation (M2, M4, M5) on the final candidate; the G1/G3 legs follow G132. | Opus/DG16 executor |
| 3 | R35-P02 | - | OPEN | Tie each change to its semantic owner, real gap, smallest delta, discriminator and rollback, with a preserved failing semantic preimage. | No row disposition yet ties each DG16 change to its semantic owner, RED and smallest delta. The M1 reference needs G132. | Opus lists each DG16 delta (V02 emitter 5c7634b9/01c67ee1, V04 d60798ea/ea827457, C5 V20) with owner, failing preimage, discriminator and rollback. | Opus/DG16 executor |
| 4 | R35-N01 | 3 | OPEN | Derive native population from bound STATE/ROADMAP, controller/epoch/receipts and plan specs with stable node identities. | Portable controls retained. The live native-consumer predicate needs M3 (G3, blocked with G132) unless Root rules that the accepted M4/L04 window2 witness discharges it. | Root decides whether the accepted M4 (L04 window2) evidence covers this row's live-consumer predicate; otherwise the row waits for G3. | Root |
| 5 | R35-N02 | 3 | OPEN | Native census fails closed on missing, duplicate, unknown, stale or contradictory state; unknown owner/schema stays explicit. | Portable controls retained. The live native-consumer predicate needs M3 (G3, blocked with G132) unless Root rules that the accepted M4/L04 window2 witness discharges it. | Root decides whether the accepted M4 (L04 window2) evidence covers this row's live-consumer predicate; otherwise the row waits for G3. | Root |
| 6 | R35-N03 | 3 | OPEN | One normalized versioned graph schema binds edges, read/write/resource/authority sets, effects, vocabularies and candidate/effect identities. | Portable controls retained. The live native-consumer predicate needs M3 (G3, blocked with G132) unless Root rules that the accepted M4/L04 window2 witness discharges it. | Root decides whether the accepted M4 (L04 window2) evidence covers this row's live-consumer predicate; otherwise the row waits for G3. | Root |
| 7 | R35-N04 | 3 | OPEN | Inputs, graph, dispatch, results and invalidators traceable by exact identity; relevant changes invalidate affected use. | Portable controls retained. The live native-consumer predicate needs M3 (G3, blocked with G132) unless Root rules that the accepted M4/L04 window2 witness discharges it. | Root decides whether the accepted M4 (L04 window2) evidence covers this row's live-consumer predicate; otherwise the row waits for G3. | Root |
| 8 | R35-N05 | 6 | OPEN | Small, serial, uncertain or irreversible cases keep the cheap serial path, which still rechecks drift and never waives a consequential JOIN. | No M-operation required. Portable cheap-path controls retained but not re-received on a final candidate. | Independent reviewer confirms the portable controls are unchanged on the final candidate; Root records the disposition. | independent reviewer |
| 9 | R35-D01 | 3 | OPEN | Closed native population gives exactly one DONE/ACTIVE/READY/BLOCKED membership per cell; equations over incomplete census are invalid. | Portable controls retained. The live native-consumer predicate needs M3 (G3, blocked with G132) unless Root rules that the accepted M4/L04 window2 witness discharges it. | Root decides whether the accepted M4 (L04 window2) evidence covers this row's live-consumer predicate; otherwise the row waits for G3. | Root |
| 10 | R35-D02 | 3 | OPEN | READY derives from actual predecessor, JOIN, authority, writer/resource, independence, reversibility and currentness closure. | Portable controls retained. The live native-consumer predicate needs M3 (G3, blocked with G132) unless Root rules that the accepted M4/L04 window2 witness discharges it. | Root decides whether the accepted M4 (L04 window2) evidence covers this row's live-consumer predicate; otherwise the row waits for G3. | Root |
| 11 | R35-D03 | 6 | OPEN | Capacity uses actual roster, occupied work, zero/absent/positive ceiling, rollback margin and value; dispatch stays bounded. | No M-operation required. Portable capacity controls retained; any actual host-capacity claim would be NATIVE. | Independent reviewer confirms the controls are unchanged on the final candidate and that no native capacity claim is made; Root records. | independent reviewer |
| 12 | R35-D04 | 3 | OPEN | Shared semantic owner/acceptance/resource/effect serializes across files or lanes; genuinely independent preimages may overlap. | Portable controls retained. The live native-consumer predicate needs M3 (G3, blocked with G132) unless Root rules that the accepted M4/L04 window2 witness discharges it. | Root decides whether the accepted M4 (L04 window2) evidence covers this row's live-consumer predicate; otherwise the row waits for G3. | Root |
| 13 | R35-D05 | 3 | OPEN | Each consequential JOIN binds consumer, required lanes, result schema, graph identity, evidence, independence, sole writer and recompute trigger. | Portable controls retained. The live native-consumer predicate needs M3 (G3, blocked with G132) unless Root rules that the accepted M4/L04 window2 witness discharges it. | Root decides whether the accepted M4 (L04 window2) evidence covers this row's live-consumer predicate; otherwise the row waits for G3. | Root |
| 14 | R35-D06 | 3 | OPEN | Parent normalizes terminal, partial, unknown, nonverdict, transport and contradictory returns; arrival order or PASS prose cannot create acceptance. | Portable controls retained. The live native-consumer predicate needs M3 (G3, blocked with G132) unless Root rules that the accepted M4/L04 window2 witness discharges it. | Root decides whether the accepted M4 (L04 window2) evidence covers this row's live-consumer predicate; otherwise the row waits for G3. | Root |
| 15 | R35-D07 | 3 | OPEN | Before consumption, reread live owner/source, fence stale results, recompute, consume via sole writer, then expose the new frontier. | Portable controls retained. The live native-consumer predicate needs M3 (G3, blocked with G132) unless Root rules that the accepted M4/L04 window2 witness discharges it. | Root decides whether the accepted M4 (L04 window2) evidence covers this row's live-consumer predicate; otherwise the row waits for G3. | Root |
| 16 | R35-D08 | 3 | OPEN | Material events trigger reconsideration; unchanged events do not redispatch; interruptions fence only affected results. | Portable controls retained. The live native-consumer predicate needs M3 (G3, blocked with G132) unless Root rules that the accepted M4/L04 window2 witness discharges it. | Root decides whether the accepted M4 (L04 window2) evidence covers this row's live-consumer predicate; otherwise the row waits for G3. | Root |
| 17 | R35-D09 | 6 | OPEN | Conflict/retry admission recognizes logical-delivery identity and pending/unknown effects; matching labels cannot authorize duplicate effects. | Conditional C5. No protected UNKNOWN or exactly-once claim is selected. Needs a Root ruling that the conditional is not triggered, plus the portable discriminator receipt. | Root rules that conditional C5 is not triggered for D09, or names the triggering claim. | Root |
| 18 | R35-D10 | 1 | BLOCKED_EXTERNAL | Placement uses actual locality and context cost; effect admission enforceable at the actual executor; prompt-only read-only is not containment. | Current G1 containment/resource execution is unearned. G132 (fresh protected G1 pair + G3 two-stage receiving) not performed; no eligible host: measured git differs, bwrap absent, image not admitted. | Root rules on host-profile revision (image admission, git re-pin, bwrap provision) and sender/receiver; owner grants one-use G132; Opus prepares the source correction; reviewer reviews; staffed G3 window. | Root |
| 19 | R35-D11 | 6 | OPEN | Sole governor, exact four child skills, unique audit-andon and L1-L5 authority survive; no child or JOIN grants READY, PASS or closure. | No-regression row; portable routing and child-authority checks retained. DG17 T3 (bb781f62) belongs to another cell and does not transfer. | Independent reviewer confirms the governor and four-child authority are unchanged on the final candidate; Root records. | independent reviewer |
| 20 | R35-V01 | 2 | RECONFIRMED | Derive the complete live verifier obligation population from actual canonical source/registry, including prelude, final and currentness semantics. | Awarded or reconfirmed on 51416b2f, b30ef328 and 379581a8 only. M6 needs a binding on one final candidate. | Root binds V01 to the final candidate (A4 on 71b6315c covered all 119 nodes; check applicability) and records the M6 disposition. | Root |
| 21 | R35-V02 | 2 | AWARDED | Every property/obligation maps exactly once to one node or composed JOIN with input, order, environment, normalization, evidence and invalidator. | Scope is the no-argument registry on 71b6315c, with three argument-mode rows inapplicable. M6 needs final-candidate applicability. | Root confirms A4 applies to the final candidate (diff against 71b6315c) and records the M6 disposition. | Root |
| 22 | R35-V03 | 2 | AWARDED | Run legacy and DAG on the same exact candidate and complete mapped population; retain raw outputs and compare accepted normalization semantics. | The award is at the earlier 51416b2f scope. Successor V03 on frozen 2e72a912 has no Root GO: the r2 run commit is staged and unpublished, with launch preflight PASS. P3 on b30ef328 is raw-unequal. | Luna assembles one launch-ready GO packet (origin checks, reviewer and Root availability); Root issues GO; Opus runs the single 2e72a912 V03 comparison. | Root |
| 23 | R35-V04 | 2 | OPEN | Missing, duplicate, unknown, reordered, stale or falsely settled obligations fail closed, including nonzero, partial and interrupted cases. | Whole V04 is held pending adjudication on frozen 2450417a. W4 is partial: P4 has no per-case table, and W3 was refused because of the input mode error. The DG17 hosted structural run outcome is pending. | Root gives GO or declines the proposed W4b, then adjudicates whole V04 on 2450417a together with the DG17 hosted result. | Root |
| 24 | R35-V05 | 3 | BLOCKED_EXTERNAL | Selective invalidation reruns exactly the affected scope, preserving unaffected qualified evidence; drift rebuilds the map conservatively. | The actual new generation and stale old-return decision are unperformed and need G3. G132 (fresh protected G1 pair + G3 two-stage receiving) not performed; no eligible host: measured git differs, bwrap absent, image not admitted. | Root rules on host-profile revision (image admission, git re-pin, bwrap provision) and sender/receiver; owner grants one-use G132; Opus prepares the source correction; reviewer reviews; staffed G3 window. | Root |
| 25 | R35-V06 | 1 | BLOCKED_EXTERNAL | Held-out topology, concurrent change, interruption, duplicates, shared writers, unknown owners and coupling alter outcomes correctly; isolation recorded. | Actual host isolation/resource boundaries remain at G1/G3 scope. G132 (fresh protected G1 pair + G3 two-stage receiving) not performed; no eligible host: measured git differs, bwrap absent, image not admitted. | Root rules on host-profile revision (image admission, git re-pin, bwrap provision) and sender/receiver; owner grants one-use G132; Opus prepares the source correction; reviewer reviews; staffed G3 window. | Root |
| 26 | R35-V07 | 6 | OPEN | Keep the legacy route until equivalence passes; conversion and retirement are separate reviewed/owner steps with rollback. | Conditional C2/C3. Legacy retention is required and no conversion or retirement is selected. Needs a Root ruling that retention is the final disposition. | Root records that legacy is retained and conversion/retirement is not triggered; the owner is involved only if conversion is wanted. | Root |
| 27 | R35-R01 | 3 | OPEN | Consume current R0033 obligation/blocking-scope facts; nodes touching that scope are not READY; independent nodes stay eligible. | Portable controls retained. The live native-consumer predicate needs M3 (G3, blocked with G132) unless Root rules that the accepted M4/L04 window2 witness discharges it. | Root decides whether the accepted M4 (L04 window2) evidence covers this row's live-consumer predicate; otherwise the row waits for G3. | Root |
| 28 | R35-R02 | 3 | OPEN | Changed obligation, binding or continuity generation forces recomputation; stale satisfaction receipts cannot unblock. | Portable controls retained. The live native-consumer predicate needs M3 (G3, blocked with G132) unless Root rules that the accepted M4/L04 window2 witness discharges it. | Root decides whether the accepted M4 (L04 window2) evidence covers this row's live-consumer predicate; otherwise the row waits for G3. | Root |
| 29 | R35-R03 | 6 | OPEN | A native interlock requires all nine stated prerequisites; none defaults to current or trusted. | Conditional C1 native interlock with no selected prevention claim. Needs a Root ruling that C1 is not triggered and the boundary controls are retained. | Root rules that C1 is not triggered (or names the claim) and records the disposition; reviewer confirms the boundary controls are unchanged. | Root |
| 30 | R35-R04 | 6 | OPEN | Qualified interlock allows matching current requests and denies stale, foreign, changed or contradictory ones, preserving lawful bounded actions. | Conditional C1 native interlock with no selected prevention claim. Needs a Root ruling that C1 is not triggered and the boundary controls are retained. | Root rules that C1 is not triggered (or names the claim) and records the disposition; reviewer confirms the boundary controls are unchanged. | Root |
| 31 | R35-R05 | 6 | OPEN | Unbound tools stay outside the interlock; unavailable or untrusted hooks are not prevention; serial work keeps the cheap path. | Conditional C1 native interlock with no selected prevention claim. Needs a Root ruling that C1 is not triggered and the boundary controls are retained. | Root rules that C1 is not triggered (or names the claim) and records the disposition; reviewer confirms the boundary controls are unchanged. | Root |
| 32 | R35-R06 | 6 | OPEN | Pre-event allow or post-event observation never establishes effect, dependency, authority, JOIN, PASS or closure. | Conditional C1 native interlock with no selected prevention claim. Needs a Root ruling that C1 is not triggered and the boundary controls are retained. | Root rules that C1 is not triggered (or names the claim) and records the disposition; reviewer confirms the boundary controls are unchanged. | Root |
| 33 | R35-R07 | 6 | OPEN | Interlock rollback removes only the admitted adapter/route edge; retirement weighs coverage, mapping, native enforcement and cost. | Conditional C1 native interlock with no selected prevention claim. Needs a Root ruling that C1 is not triggered and the boundary controls are retained. | Root rules that C1 is not triggered (or names the claim) and records the disposition; reviewer confirms the boundary controls are unchanged. | Root |
| 34 | R35-L01 | 4 | OPEN | At accepted RETURN/JOIN, traverse ancestry to the named campaign root and reconsider siblings and future prerequisites at every ancestor. | Only L04 was accepted from window2. This row needs its own shape facts from a received natural event or from G3, which is blocked with G132. | Root or a reviewer checks whether the L04 window2 receiving (39 ranges, 2 negative readbacks) proves this row's shape; otherwise the row waits for G3. | Root |
| 35 | R35-L02 | 4 | OPEN | Completed comparison inputs keep an independently useful preparation successor when prerequisites are met; block only the exact effect. | Only L04 was accepted from window2. This row needs its own shape facts from a received natural event or from G3, which is blocked with G132. | Root or a reviewer checks whether the L04 window2 receiving (39 ranges, 2 negative readbacks) proves this row's shape; otherwise the row waits for G3. | Root |
| 36 | R35-L03 | 4 | OPEN | Preserve inward/outward/forward/backward cycle, reconciliation and immediate reconsideration with bounded future consumers. | Only L04 was accepted from window2. This row needs its own shape facts from a received natural event or from G3, which is blocked with G132. | Root or a reviewer checks whether the L04 window2 receiving (39 ranges, 2 negative readbacks) proves this row's shape; otherwise the row waits for G3. | Root |
| 37 | R35-L04 | 4 | AWARDED | Held-out natural transition: completed inputs, blocked effect, useful preparation, ancestor JOIN prerequisite and consumed decision-changing return. | Historical actor/runtime scope (Sept 11 window2). Not listed in the current named_current_row_awards_this_phase; Root must carry it into M6. | Root confirms the Nov 9 L04 acceptance carries into the M6 ledger at its historical scope. | Root |
| 38 | R35-L05 | 4 | OPEN | A matched negative with identical facts but no valid dispatch or deferral fails; omission, stale and blanket-block negatives also fail. | Only L04 was accepted from window2. This row needs its own shape facts from a received natural event or from G3, which is blocked with G132. | Root or a reviewer checks whether the L04 window2 receiving (39 ranges, 2 negative readbacks) proves this row's shape; otherwise the row waits for G3. | Root |
| 39 | R35-L06 | 4 | OPEN | Preserve legitimate shared-writer, unknown, missing-input, capacity, authority and boundary blocks; an unchanged event yields no redispatch. | Only L04 was accepted from window2. This row needs its own shape facts from a received natural event or from G3, which is blocked with G132. | Root or a reviewer checks whether the L04 window2 receiving (39 ranges, 2 negative readbacks) proves this row's shape; otherwise the row waits for G3. | Root |
| 40 | R35-L07 | 6 | OPEN | Triad relation graph is guarded evidence; TC07 liveness distinctions use actual joint facts; TC06 preserves consumers until discharge. | Conditional C3/C4 at guarded-triad scope only; global liveness and retirement are unproved by design. Needs a Root ruling that the conditionals are not triggered. | Root records the scoped guard disposition, with the stronger liveness and retirement claims not triggered. | Root |
| 41 | R35-Q01 | 2 | OPEN | Retain original R53-DAG coverage and failing predecessors; changed evaluators or oracles need independent property justification. | Changed oracles and fixtures (DIST fixture, V02 v4 rows, V04 bookend checks) need independent property justification on the final candidate. | Opus compiles the list of evaluators and expected answers changed since the original; an independent reviewer justifies each; Root records. | Opus/DG16 executor |
| 42 | R35-Q02 | 2 | AWARDED | Run focused baseline/regression controls, then the actual canonical verify-package.sh on the exact candidate; classify failure kinds. | The award is at 51416b2f scope only. The literal canonical verify-package.sh run on the final candidate still needs applicable evidence. | Opus finds an existing literal canonical invocation on the final candidate (for example DG17 hosted CI) or declares one ordinary run; Root receives it. | Opus/DG16 executor |
| 43 | R35-Q03 | 6 | OPEN | Shared governor, registry, builder, installer and portal owners stay unmodified in the independent slice; deliver exact integration patches. | The reserved shared owners must be shown unmodified, or exactly patched, in the final candidate. No final-candidate owner diff has been received. | Opus produces the final-candidate diff against base, classified by owner; an independent reviewer confirms the reserved owners; Root records. | Opus/DG16 executor |
| 44 | R35-Q04 | 5 | RECONFIRMED | Shipped bytes trigger package, inventory, helper-dispatch, copy parity, path, cost and retirement coverage; preserve version and size budgets. | The optional alias is unverified, and the reconfirmation covers 379581a8 only. The final-candidate archives (for example 2450417a) need binding. | Root binds Q04 to the final-candidate archives using the existing M5 route evidence, or names the missing leg. | Root |
| 45 | R35-Q05 | 5 | RECONFIRMED | Source, generated, built, packaged, installed, discovered/native and hosted/public remain separate evidence legs. | Native discovery, activation and public release carry no claim, by design. The layer binding is still needed on the final candidate. | Root binds the Q05 layer disposition to the final candidate and records M6. | Root |
| 46 | R35-Q06 | 3 | BLOCKED_EXTERNAL | One bounded governed live run corroborates two independent cells, required JOIN, shared-writer/stale boundary, normalization and recomputation. | An actual two-cell governed JOIN at exact source/package/host identity requires G3. G132 (fresh protected G1 pair + G3 two-stage receiving) not performed; no eligible host: measured git differs, bwrap absent, image not admitted. | Root rules on host-profile revision (image admission, git re-pin, bwrap provision) and sender/receiver; owner grants one-use G132; Opus prepares the source correction; reviewer reviews; staffed G3 window. | Root |
| 47 | R35-Q07 | 6 | OPEN | Rigorous self-review plus fresh independent exact-tree cold review and CI bound to the real final candidate. | No final exact DG16 candidate is selected, so no fresh independent exact-tree cold review or bound CI exists for one. | Root names the final DG16 candidate; a fresh independent cold reviewer reviews the exact tree; CI is bound to it. | independent reviewer |
| 48 | R35-Q08 | 6 | OPEN | Return complete criterion statuses, pinned interfaces/patches, failures, verified bundle, rollback and draft PR metadata; no closure by bundle. | Complete criterion statuses and the delivery bundle depend on every other row; this ledger is a draft input only. | Opus finalizes the ledger once the other rows settle; Root verifies; the owner handles merge and closure later. | Opus/DG16 executor |

## Evidence locators

**R35-H01** (HISTORICAL_PRESERVED)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-H01] refs=[] cond=[] disposition=HISTORICAL_PRESERVED (authority NONE)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json amendments[id=issuecomment5312882718].status HISTORICAL_ACCEPTANCE_PRESERVED
- C:/workspace/ai/improveimplementaudit/plans/succession-20261101/dg16-whole-cell-receiving/ORIGINAL_DG16_ROWMAP.json original48[R35-H01] HISTORICAL_PRESERVED (Nov 1 context only)

**R35-P01** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-P01] refs=['M1', 'M2', 'M3', 'M4', 'M5'] cond=[] disposition=CURRENT_SOURCE_SCOPED_RECEIVED (authority NONE)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-P01

**R35-P02** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-P02] refs=['M1', 'M2', 'M5'] cond=[] disposition=CURRENT_SOURCE_SCOPED_RECEIVED (authority NONE)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-P02

**R35-N01** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-N01] refs=['M3', 'M4'] cond=[] disposition=REUSABLE_PORTABLE_CONTROLS_DECLARED_INTERFACE (authority NONE)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=4].unresolved: 'current compiler/native/currentness ... remain separate'
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-N01

**R35-N02** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-N02] refs=['M3', 'M4'] cond=[] disposition=REUSABLE_PORTABLE_CONTROLS_DECLARED_INTERFACE (authority NONE)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=4].unresolved: 'current compiler/native/currentness ... remain separate'
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-N02

**R35-N03** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-N03] refs=['M3', 'M4'] cond=[] disposition=REUSABLE_PORTABLE_CONTROLS_DECLARED_INTERFACE (authority NONE)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=4].unresolved: 'current compiler/native/currentness ... remain separate'
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-N03

**R35-N04** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-N04] refs=['M3', 'M4'] cond=[] disposition=REUSABLE_PORTABLE_CONTROLS_DECLARED_INTERFACE (authority NONE)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=4].unresolved: 'current compiler/native/currentness ... remain separate'
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-N04

**R35-N05** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-N05] refs=[] cond=[] disposition=REUSABLE_PORTABLE_CONTROLS_DECLARED_INTERFACE (authority NONE)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-N05

**R35-D01** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-D01] refs=['M3', 'M4'] cond=[] disposition=REUSABLE_PORTABLE_CONTROLS_DECLARED_INTERFACE (authority NONE)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=4].unresolved: 'current compiler/native/currentness ... remain separate'
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-D01

**R35-D02** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-D02] refs=['M3', 'M4'] cond=[] disposition=REUSABLE_PORTABLE_CONTROLS_DECLARED_INTERFACE (authority NONE)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=4].unresolved: 'current compiler/native/currentness ... remain separate'
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-D02

**R35-D03** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-D03] refs=[] cond=[] disposition=REUSABLE_PORTABLE_CONTROLS_DECLARED_INTERFACE (authority NONE)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-D03

**R35-D04** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-D04] refs=['M3', 'M4'] cond=[] disposition=REUSABLE_PORTABLE_CONTROLS_DECLARED_INTERFACE (authority NONE)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=4].unresolved: 'current compiler/native/currentness ... remain separate'
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-D04

**R35-D05** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-D05] refs=['M3', 'M4'] cond=[] disposition=REUSABLE_PORTABLE_CONTROLS_DECLARED_INTERFACE (authority NONE)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=4].unresolved: 'current compiler/native/currentness ... remain separate'
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-D05

**R35-D06** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-D06] refs=['M3', 'M4'] cond=[] disposition=REUSABLE_PORTABLE_CONTROLS_DECLARED_INTERFACE (authority NONE)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=4].unresolved: 'current compiler/native/currentness ... remain separate'
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-D06

**R35-D07** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-D07] refs=['M3', 'M4'] cond=[] disposition=REUSABLE_PORTABLE_CONTROLS_DECLARED_INTERFACE (authority NONE)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=4].unresolved: 'current compiler/native/currentness ... remain separate'
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-D07

**R35-D08** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-D08] refs=['M3', 'M4'] cond=[] disposition=REUSABLE_PORTABLE_CONTROLS_DECLARED_INTERFACE (authority NONE)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=4].unresolved: 'current compiler/native/currentness ... remain separate'
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-D08

**R35-D09** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-D09] refs=[] cond=['C5'] disposition=SCOPED_LOGICAL_DELIVERY_EFFECT_REUSE (authority NONE)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-D09

**R35-D10** (BLOCKED_EXTERNAL)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-D10] refs=['M1'] cond=['C5'] disposition=CONDITIONAL_NATIVE_PLACEMENT_CLAIM_RESERVED (authority NONE)
- disc@47cf35b:handoff/astra-dg16-dg18/discussions/DG16-DG17-reader-bindings.md '## Root execution decision for the owner-approved recovery session': 'No live G132 window can be confirmed on this evidence.'
- disc@47cf35b:handoff/astra-dg16-dg18/discussions/DG16-DG17-reader-bindings.md '## 2026-11-25 · Opus 5.5 (DG16) to Root and Luna: G132 live-image measurement': git DIFFERS, bwrap ABSENT, ImageVersion not admitted

**R35-D11** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-D11] refs=[] cond=[] disposition=REUSABLE_PORTABLE_CONTROLS_DECLARED_INTERFACE (authority NONE)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-D11

**R35-V01** (RECONFIRMED)
- disc@47cf35b:handoff/astra-dg16-dg18/DG16_V01_V03_ROOT_ADJUDICATION.json decisions[row=R35-V01].decision ACCEPT_AT_EXACT_CURRENT_SOURCE_POPULATION_SCOPE (product 51416b2f)
- disc@47cf35b:handoff/astra-dg16-dg18/ROOT_RECEIVING_02.json new_original_awards: 'DG16.R35-V01 at the current verifier population scope'
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.v18.root_A2_and_M5.V01: 'Reconfirmed at exact source-population scope.' (b30ef328)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.v19.DG16_A3_B2_M5_R2.decision RECONFIRM_V01_M5_Q04_Q05_AT_PREVIOUSLY_TESTED_SCOPES_ON_V19 (379581a8)

**R35-V02** (AWARDED)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.v20.DG16_V02.decision AWARD_ORIGINAL_R35_V02_AT_CANONICAL_NO_ARGUMENT_REGISTRY_SCOPE (71b6315c)
- disc@47cf35b:handoff/astra-dg16-dg18/discussions/DG16-DG17-reader-bindings.md '## Root consolidated acceptance on 71b6315c and the separate V03 review7 packet': 'DG16 V02 awarded for the exact canonical A4 registration.'

**R35-V03** (AWARDED)
- disc@47cf35b:handoff/astra-dg16-dg18/DG16_V01_V03_ROOT_ADJUDICATION.json decisions[row=R35-V03].decision ACCEPT_AT_EXACT_PORTABLE_EXECUTABLE_CORRESPONDENCE_SCOPE (51416b2f, run 44666584405)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.census_successor.DG16_V02_V03_V04_20261124.V03.review7.decision ADOPT_POLICY_ONE_PROSPECTIVE_EPISODE; launch NOT_AUTHORIZED_BY_THIS_ADOPTION
- disc@47cf35b:handoff/astra-dg16-dg18/discussions/DG16-DG17-reader-bindings.md '## Root receiving of V19 A3, B2 and M5-R2': 'The V03 comparison, literal Q02 and full V02/V04 still need their applicable evidence.'

> Update: R35-V04 AWARDED on 2450417a at canonical comparison and settlement scope (Root 809ca1b). Before that, W4b ran at 5901e00 and received W3 through the frozen 2450417a consumer, with 28/28 mutations refused. Next: Root adjudicates whole V04.

**R35-V04** (OPEN)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json dependent_frontiers.DG16.V04_root_receiving.decision RECEIVE_R35_V04_PORTABLE_CONTROLS_ONLY, whole_row_accepted=false
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.v20.DG16_V04.decision RECEIVE_W3_AND_ADVERSE_V4_CONTROLS_HOLD_WHOLE_V04
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.2450417a_hosted_freeze.limits: 'T14 and whole V04 remain open.'
- disc@47cf35b:handoff/astra-dg16-dg18/discussions/DG16-DG17-reader-bindings.md '## 2026-11-25 · Opus 5.5 (DG16) to Luna and Root: W4 actual result (partial, harness and input defect) and proposed W4b'

**R35-V05** (BLOCKED_EXTERNAL)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-V05] refs=['M2', 'M3'] cond=[] disposition=G2_FULL_CORRESPONDENCE_UNESTABLISHED (authority NONE)
- disc@47cf35b:handoff/astra-dg16-dg18/discussions/DG16-DG17-reader-bindings.md '## Root execution decision for the owner-approved recovery session': 'No live G132 window can be confirmed on this evidence.'
- disc@47cf35b:handoff/astra-dg16-dg18/discussions/DG16-DG17-reader-bindings.md '## 2026-11-25 · Opus 5.5 (DG16) to Root and Luna: G132 live-image measurement': git DIFFERS, bwrap ABSENT, ImageVersion not admitted

**R35-V06** (BLOCKED_EXTERNAL)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-V06] refs=['M1', 'M3'] cond=[] disposition=SCOPED_NEGATIVES_RETAINED (authority NONE)
- disc@47cf35b:handoff/astra-dg16-dg18/discussions/DG16-DG17-reader-bindings.md '## Root execution decision for the owner-approved recovery session': 'No live G132 window can be confirmed on this evidence.'
- disc@47cf35b:handoff/astra-dg16-dg18/discussions/DG16-DG17-reader-bindings.md '## 2026-11-25 · Opus 5.5 (DG16) to Root and Luna: G132 live-image measurement': git DIFFERS, bwrap ABSENT, ImageVersion not admitted

**R35-V07** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-V07] refs=[] cond=['C2', 'C3'] disposition=CANONICAL_SWITCH_RETIREMENT_RESERVED (authority NONE)
- disc@47cf35b:handoff/astra-dg16-dg18/DG16_V01_V03_ROOT_ADJUDICATION.json conversion_or_retirement=false

**R35-R01** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-R01] refs=['M3', 'M4'] cond=[] disposition=REUSABLE_PORTABLE_CONTROLS_DECLARED_INTERFACE (authority NONE)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=4].unresolved: 'current compiler/native/currentness ... remain separate'
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-R01

**R35-R02** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-R02] refs=['M3', 'M4'] cond=[] disposition=REUSABLE_PORTABLE_CONTROLS_DECLARED_INTERFACE (authority NONE)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=4].unresolved: 'current compiler/native/currentness ... remain separate'
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-R02

**R35-R03** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-R03] refs=[] cond=['C1'] disposition=CONDITIONAL_INTERLOCK_NO_SELECTED_PREVENTION_CLAIM (authority NONE)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-R03

**R35-R04** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-R04] refs=[] cond=['C1'] disposition=CONDITIONAL_INTERLOCK_NO_SELECTED_PREVENTION_CLAIM (authority NONE)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-R04

**R35-R05** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-R05] refs=[] cond=['C1'] disposition=CONDITIONAL_INTERLOCK_NO_SELECTED_PREVENTION_CLAIM (authority NONE)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-R05

**R35-R06** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-R06] refs=[] cond=['C1'] disposition=CONDITIONAL_INTERLOCK_NO_SELECTED_PREVENTION_CLAIM (authority NONE)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-R06

**R35-R07** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-R07] refs=[] cond=['C1', 'C3'] disposition=CONDITIONAL_INTERLOCK_NO_SELECTED_PREVENTION_CLAIM (authority NONE)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-R07

**R35-L01** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-L01] refs=['M4'] cond=[] disposition=PROSPECTIVE_AMENDMENT_PLUS_G3_ACTUAL_GRAPH_PREDICATE (authority NONE)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=4].unresolved: 'Q06, other L rows ... remain separate'
- 585012cb:recovery/contracts/evidence/L04_ROOT_DECISION.json (accepts only R35-L04; root_readback records 2 negative parent readbacks)

**R35-L02** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-L02] refs=['M4'] cond=[] disposition=PROSPECTIVE_AMENDMENT_PLUS_G3_ACTUAL_GRAPH_PREDICATE (authority NONE)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=4].unresolved: 'Q06, other L rows ... remain separate'
- 585012cb:recovery/contracts/evidence/L04_ROOT_DECISION.json (accepts only R35-L04; root_readback records 2 negative parent readbacks)

**R35-L03** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-L03] refs=['M4'] cond=[] disposition=PROSPECTIVE_AMENDMENT_PLUS_G3_ACTUAL_GRAPH_PREDICATE (authority NONE)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=4].unresolved: 'Q06, other L rows ... remain separate'
- 585012cb:recovery/contracts/evidence/L04_ROOT_DECISION.json (accepts only R35-L04; root_readback records 2 negative parent readbacks)

**R35-L04** (AWARDED)
- 585012cb:recovery/contracts/evidence/L04_ROOT_DECISION.json decision ACCEPT_R35_L04_ORIGINAL_HELD_OUT_NATURAL_BEHAVIORAL_WITNESS (utc 2026-11-09)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=4].independently_received: 'Root accepted exact R35-L04 behavioral witness.'

**R35-L05** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-L05] refs=['M4'] cond=[] disposition=PROSPECTIVE_AMENDMENT_PLUS_G3_ACTUAL_GRAPH_PREDICATE (authority NONE)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=4].unresolved: 'Q06, other L rows ... remain separate'
- 585012cb:recovery/contracts/evidence/L04_ROOT_DECISION.json (accepts only R35-L04; root_readback records 2 negative parent readbacks)

**R35-L06** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-L06] refs=['M4'] cond=[] disposition=PROSPECTIVE_AMENDMENT_PLUS_G3_ACTUAL_GRAPH_PREDICATE (authority NONE)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=4].unresolved: 'Q06, other L rows ... remain separate'
- 585012cb:recovery/contracts/evidence/L04_ROOT_DECISION.json (accepts only R35-L04; root_readback records 2 negative parent readbacks)

**R35-L07** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-L07] refs=[] cond=['C3', 'C4'] disposition=PROSPECTIVE_AMENDMENT_PLUS_G3_ACTUAL_GRAPH_PREDICATE (authority NONE)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-L07

**R35-Q01** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-Q01] refs=['M2'] cond=[] disposition=CONTROLS_FAILURES_RETAINED_APPLICABILITY_REQUIRED (authority NONE)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-Q01
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json dependent_frontiers.DG16.V04_root_receiving.predecessor: 'Existing M2 award at 51416'

**R35-Q02** (AWARDED)
- disc@47cf35b:handoff/astra-dg16-dg18/DG16_Q02_ROOT_ADJUDICATION.json decision ACCEPT_AT_EXACT_51416_WITNESSED_EXECUTION_SCOPE
- disc@47cf35b:handoff/astra-dg16-dg18/ROOT_RECEIVING_02.json new_original_awards: 'DG16.R35-Q02 at exact-source witnessed execution scope'
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.v18.root_A2_and_M5.V03_and_Q02: 'the literal canonical bash invocation need applicable evidence'

**R35-Q03** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-Q03] refs=[] cond=[] disposition=SCOPED_REVIEW_DELIVERY_OUTER_EFFECTS_RESERVED (authority NONE)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]; no Root decision text in CONTINUATION.json, the reader-bindings topic or handoff/astra-dg16-dg18/*.json names R35-Q03

**R35-Q04** (RECONFIRMED)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.v18.root_A2_and_M5['R35-Q04']: 'ACCEPT at applicable package/dispatch/cost scope on b30ef328.'
- disc@47cf35b:handoff/astra-dg16-dg18/discussions/DG16-DG17-reader-bindings.md '## 2026-11-24 - Astra to Opus: A2 and M5 on b30ef328': 'Root also awards original R35-Q04'
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.v19.DG16_A3_B2_M5_R2.decision RECONFIRM_V01_M5_Q04_Q05_AT_PREVIOUSLY_TESTED_SCOPES_ON_V19 (379581a8)

**R35-Q05** (RECONFIRMED)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.v18.root_A2_and_M5['R35-Q05']: 'ACCEPT at exact evidence-layer disposition scope.'
- disc@47cf35b:handoff/astra-dg16-dg18/discussions/DG16-DG17-reader-bindings.md '## 2026-11-24 - Astra to Opus: A2 and M5 on b30ef328': 'R35-Q05 at the evidence-layer disposition scope'
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json active_qualification.v19.DG16_A3_B2_M5_R2.decision RECONFIRM_V01_M5_Q04_Q05_AT_PREVIOUSLY_TESTED_SCOPES_ON_V19 (379581a8)

**R35-Q06** (BLOCKED_EXTERNAL)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-Q06] refs=['M3', 'M4'] cond=[] disposition=G3_ACTUAL_LIVE_COMPOSITION_SCOPE (authority NONE)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=3].original_scope_earned: 'No new Q06/L01-L07/T08 live conjunction'
- disc@47cf35b:handoff/astra-dg16-dg18/discussions/DG16-DG17-reader-bindings.md '## Root execution decision for the owner-approved recovery session': 'No live G132 window can be confirmed on this evidence.'
- disc@47cf35b:handoff/astra-dg16-dg18/discussions/DG16-DG17-reader-bindings.md '## 2026-11-25 · Opus 5.5 (DG16) to Root and Luna: G132 live-image measurement': git DIFFERS, bwrap ABSENT, ImageVersion not admitted

**R35-Q07** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-Q07] refs=['M6'] cond=[] disposition=SCOPED_REVIEW_DELIVERY_OUTER_EFFECTS_RESERVED (authority NONE)
- 585012cb:recovery/contracts/SIX_GROUP_MILESTONES.json groups[id=6].original_scope_earned: 'Q07/Q08 and T09-T12 still require their exact applicable conjunction.'

**R35-Q08** (OPEN)
- 585012cb:recovery/contracts/original/ORIGINAL48_CURRENT_MAP_NOV06.json rows[R35-Q08] refs=['M6'] cond=[] disposition=SCOPED_REVIEW_DELIVERY_OUTER_EFFECTS_RESERVED (authority NONE)
- disc@47cf35b:handoff/astra-dg16-dg18/CONTINUATION.json original_counts.DG16.M6_final_rows=[0,48]

## Notes

- Milestone group: the primary remaining gate among the Nov06 `mandatory_operation_or_consumer_references` (M1..M6 = SIX_GROUP ids 1..6). It is null for P01/P02, which span several groups. The JSON keeps the full Nov06 reference lists.
- The Nov06 map has authority NONE. It is used only for the reference lists and residuals, never for awards.
- Milestones 3/6: M2 ("Existing M2 award at 51416", V04_root_receiving.predecessor), M4 (L04, Nov 9) and M5 (BB781F62_ORIGINAL_AWARDS.json AWARD_ORIGINAL_MILESTONE, reconfirmed on b30ef328 and 379581a8). No standalone M2 decision file was located.
