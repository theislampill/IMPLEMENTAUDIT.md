# Independent terminal receiving: actual repair, re-audit, and custody

Report state: FINAL

## Disposition

**PASS for the exact repaired candidate, actual separate Root review consumption, phase-2 completion, round-3 re-audit, and terminal owned-custody record.** The terminal evidence now supplies the execution and cleanup observations that were explicitly pending in the earlier live-candidate report.

The literal **H02 and P06 operational sequences are observed**, including fresh re-audit after repair. A concrete N02 expected-behavior limb is also observed: the earlier child PASS remained findings, with separate Root decision and fresh deterministic evidence required afterward. These are bounded judgments about this ordinary hosted run. **Original whole-cell/campaign acceptance, uncued model performance, native/session/Stop behavior, and audit closure remain NONVERDICT.** This return grants no authority.

I continued the same independent assessor role under the unchanged resolved executing skill. I verified raw packet content independently; Root's terminal readback was not substituted for verification. I did not execute target code, replay an operation, inspect an external host, mutate source, or create a child. This terminal review is distinct from the separate Root decision whose actual consumption it examines.

## Packet and exact resulting binding

The original 18-member packet remains byte-identical. All ten new supplement members match the declared byte counts and SHA-256. The terminal ZIP contains 4,862 unique safe file paths; every member was read and hashed, all JSON members parse without duplicate keys, and all seven embedded observation inventories match their complete member populations and canonical inventory hashes. The terminal copies of the earlier final-repaired ZIP's contents and the separately supplied reaudited ZIP match byte-for-byte. [Base and supplement MANIFEST; final/artifact.zip; reaudited/artifact.zip]

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Supplement MANIFEST.json | — | `61b1e2743ea65834e292840cf113e14c76ff2c52fcc519470e7b5e35179bbbd5` |
| Supplement REQUEST.json | — | `6b6e615a403e8361e7b968463e9779348507f2a433dd241749c23babf360064b` |
| Terminal ZIP | 2,852,920 | `3ee01fa640bbba272f0a01ca541d8afd69627ac936debfe5c1a5d551c3b81ae5` |
| Reaudited ZIP | 519,889 | `5119d8eaa8198cbe8cc51e94cf974ab8e593bd63d01ce5196a4a7a2328474afe` |
| Reaudited PACKET.json | — | `9b5b01a41e35442c38f123dcc9a7a064800d3808a9ea389587afd6a939040511` |
| Reaudited observation inventory | — | `878ee0af1a45ce279f2973b57f1f2ec37e4c7b63bea6bfb3778dddddc862295f` |
| Actual 08-reaudit decision | 24,187 | `9f84ac40aa54921b93f0d17163c1ac1a7a1fa32c01662b3ba8df0ab5895f8522` |
| Custody archive | 119,580 | `a1a1be35dfae046a2f8075439b697520e38c0c4330605604546f6da37966607c` |

The full resulting binding is in RESULT.json. Its consequential identities are:

| Field | Value |
|---|---|
| Run / attempt | `44182058642` / `1` |
| Source commit / tree | `a297957be11feb494c0ec467235794a1e0c54751` / `b08dc4ecf4028beeedb579a312eccae23cb5d863` |
| Launch commit | `e44272057a4814d95313c8c1ec88b37103203986` |
| Controller / claim | `dg17-final-44182058642` / `30a5f8efe3a8f1c29e10a350d12ea828` |
| Exchange | `c13b5bd400e248b3a46c8fef05ec2f21` |
| Resulting snapshot stage | `reaudited` |
| Task HEAD / tree | `75c615e5c34a73e45f59e2020557f9f338722c14` / `f0f43b2caf13f69ef972aa5f36e7f6c154e0bc71` |
| Resulting continuity receipt | `refs/implementaudit/continuity-receipts/dg17-final-44182058642/G0009@831d8935abed37a2567977a916dc2090ebeab305` |
| Last mailbox commit | `9877e6bcb13b085f31c15d45bb00c270fe05faf4` |
| Owner | 19 bytes; SHA-256 `6358635f89b9fb5c1a0f83f5c947366b3d9886b6a8b13c03341b7081d5844459` |
| Dependency | 5 bytes; SHA-256 `185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969` |
| Phase 2 / audit-fix alias, each | 3,435 bytes; SHA-256 `d989190f215f0e97b8f7b73c6fa2ae3d4c53a54e98d01995a08664435e049c41` |

The snapshot's VERIFIED currentness is historical after cleanup. It does not provide reusable live custody or authorize another operation.

## Actual separate review consumption and phase completion — PASS

The published decision binds exactly the earlier G0008 final-repaired candidate, including its original observation inventory and phase hashes. Its independent-review text is the exact 12,161-byte report I issued, SHA-256 `37905add719c7cadbf2945cb2bc97248ace3be36e69896c9f8756a7aeea8dc30`. Its result digest, reviewer identity, request digest, and binding agree. The transport's `Root-decisions/reaudit.json` and `mail-6.raw` equal the supplied 08-reaudit decision bytes. The corresponding Git blob recomputes to `2f734d9483ae4b6958136cf1f12f1d43c0d25ed0`; provider readback and captured mailbox records agree on the single added expected path, commit, and parent. [08-reaudit; 08-INTENT/RESULT/READBACK; final/Root-decisions/reaudit.json; mail-6 records]

The decision is an actual separate `complete-fix-and-reaudit` Root record. It expressly receives child findings as evidence, retains original acceptance and cleanup obligations, and directs a finite completion/re-audit action. This report treats that text as evidence of the decision, not as a prescribed conclusion. The source consumer checks G0008 currentness and the run root before and after mailbox receipt (271–276). Subsequent source refresh/resume/receipt checks establish G0009 (277–288). Those observations match the read source gate's ordering. [commands/271–288; hosted_phase.py:370–427,889–903]

The terminal phase file has checked acceptance and `Status: done`; the audit-fix alias has identical bytes. FACTS and ROADMAP list phases 1 and 2 done, and the event stream adds exactly one phase-2 completion event while retaining `audit_object_state:open`. These are actual post-decision state changes, not phase-template marker tokens. [reaudited/phases; FACTS; ROADMAP; governor-events.jsonl]

## Fresh round-3 evidence and preserved owner scope — PASS

Round 3 is an actual later audit invocation at the unchanged 19-byte repaired owner and current dependency. Captures 291, 292, and 293 respectively pass smoke, operational, and complete-byte checks with actual exit 0, the exact owner hash, and the exact dependency hash. Captures 294–298 show only the intended `subject/app.txt` difference and a successful diff check. Capture 302 confirms the deliverable exists and differs from the baseline; repeated source currentness/run-root checks pass. The event stream adds round-3 AUDIT_START followed by AUDIT_VERIFY with these exact witnesses and phase census `[1,2]`. [commands/289–321; governor-events.jsonl]

The owner remains exactly `b"Hello\nstatus=ready\n"`. The archive and final snapshot agree on this file, the unchanged dependency, and the unchanged verifier. Only the original two mutation commands exist (058 and 232); the re-audit adds verification, not a replayed byte repair. Porcelain remains ` M subject/app.txt`: this was an intended uncommitted task correction, not a claimed clean committed worktree. [Archived task files; reaudited/subject; commands/298; command census]

All **321 command captures** independently verify their actual/expected exits, both stream hashes/counts/names, capture mode, positive owned process-group IDs, and ordered terminal times. There are **315 zero exits and six preserved nonzero exits**: 145, 146, 149, 163, 166, and 195. Every capture reports no timeout and absent owned process group. The original 270 captures match the earlier packet exactly; no historical refusal was replaced. The seven snapshots retain the clean candidate, late drift, refusal, re-anchored failure, repaired candidate, and re-audit. [All command triples; all snapshot inventories]

## Original literal predicates and bounded additional limbs

| Original predicate | Directly observed finding | Limit |
|---|---|---|
| **H02:** clean L5 followed by late candidate currentness mismatch; stop reuse, re-anchor, rerun affected evidence | **PASS, operational observation.** Clean captures 111–113 precede the declared 19-to-18-byte input; 145/146 refuse currentness and old anchor; 149/163/166 preserve refusal; G0005 recovery precedes affected reruns 193–195. | No independent surprise/uncued-model or complete held-out-cell award. |
| **P06:** exact-candidate final gap after clean phase; interrupt closure, repair/reverify/reaudit, preserve finding | **PASS, operational observation.** Actual final refusal 195 follows completed phase 1 and operational greens; separate L4/fix decision leads to bounded phase-2 repair and checks; exact-candidate independent receiving and a separate Root decision precede actual round 3. Failed candidate and refusal remain. | No whole-cell or campaign acceptance. The original audit object remains OPEN. |
| **N02:** child PASS-shaped prose remains findings; deterministic current evidence is still required | **PASS for this concrete expected-behavior limb.** The actual child PASS is consumed as evidence, followed by separate Root decision, repeated currentness, and fresh checks. It emits no audit-completion authority or marker. | No adversarial bypass/removal mutant was run; no general negative-family pass. |
| Terminal clause **6, L5 limb** | Exact-candidate independent assessment, repair verification, and subsequent exact-candidate re-audit are evidenced for this scoped task. | No award for the clause's L1/L2 or complete L1–L5 population. |
| Terminal clause **14, predecessor-preservation limb** | Failed and partial predecessors survive with exact hashes; this named hosted run succeeds. | This is not a complete exact-tree source cold review or all applicable CI. |
| Terminal clause **15, evidence-ceiling limb** | Captured records retain native/session/Stop nonclaims and keep original acceptance separate. | No universal proof of every source/install/release/public leg. |
| Terminal clause **17, child/phase-success insufficiency limb** | Both phases and the re-audit pass without AUDIT_COMPLETE or original closure. | No manual-closure, evidence-comment, accepted-RXX join, or C08 award. |

These mappings use the original rows and clauses literally, not new acceptance wording. [issue211-body.md:367–376,541–590,866–927] Source/gate checks and recorded behavior support these observations. A declaration of the intended fixture transition is not proof of an uncued model response; a provider-backed mailbox is not authenticated native session provenance. Original model-facing controls and the host amendment remain separate. [issue211-body.md:541–545,586 onward,764–783; issue211-host-amendment.md:478–499]

## Terminal owned custody — PASS at the recorded scope

The custody archive hash exactly matches CLEANUP.json. It contains 192 entries, 121 regular files, no links, and 483,482 payload bytes. Its owner, dependency, verifier, and all 34 compared run documents/phase/evidence files match the final snapshot. The cleanup record says `archive_consistency:TERMINAL_COMMANDS`, `task_removed:true`, `host_custody_terminated:true`, and `unresolved_processes:[]`; it explicitly denies audit closure and native Stop. This agrees with the source finalizer, which checks all command terminal records, binds the owned scratch root, archives it, removes it only without unresolved processes, and records actual path absence. [actual-task-custody.tar.gz; CLEANUP.json; transport_primitives.py:669–733]

Provider readbacks identify run `44182058642`, attempt 1, launch commit `e442720…`, completed successfully. Job `134388689913` and the re-audit, reaudited-artifact upload, owned-scratch cleanup, and final evidence upload steps all succeed. This corroborates completion of the named hosted task and its recorded owned-process cleanup, not a universal assertion about unrelated resources or native assistant Stop. [TERMINAL_RUN_READBACK; TERMINAL_JOBS_READBACK]

## Remaining obligations and next governor-owned decision

The earlier pending observations—separate Root decision consumption, phase-2 completion, actual re-audit, and final custody—are now supplied. No further byte correction or replay is supported by this evidence.

The original audit object is still **OPEN**. The terminal PACKET says `completion_marker_emitted:false`; the event stream contains no audit/run completion event. ROADMAP's complete-deliverable obligation remains unchecked even though the actual predicate now passes. This is not a false-success claim; it is an unresolved final reconciliation/acceptance boundary if anyone later seeks task or original-audit closure. Archived currentness must remain historical.

Root must independently decide what scoped original evidence to admit. Full original H02/P06/N02 acceptance, the remaining positive/negative/boundary/held-out/mutation family, uncued model controls, wider source/package/installed/host prerequisites, authentic native/session and Stop behaviors, public/release evidence, accepted-owner joins, and original terminal closure are not established by this supplement. No child finding supplies these missing predicates or authorizes effects. [Original contracts; terminal PACKET; ROADMAP; CLEANUP]

PASS
