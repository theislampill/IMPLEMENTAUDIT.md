# dg18-eligible-operations

Report state: FINAL

Parent continuity: G0013, verified before dispatch. No shared controller mutation.
Owned output: this report and any explicitly named disjoint task directory.
Authority: NONE; no original acceptance, native/protected launch, credentials, private keys, or external publication delegated.

Declared output resource: `/workspace/scratch/0269e6626329/dg18-continued/retained-record-receiving-20261115.json`.
Resource boundary: one receiving JSON file in that disjoint directory; retained for parent inspection. No held DG18 source, owner stores, controllers, STATE, ROADMAP, or Git refs are in the write set.
Acceptance for this report: verify retained pins and literal states, derive minimum missing authentic inputs from existing owner/source, and make no new source-qualification or original-acceptance claim.
Rollback: remove only this newly declared JSON and restore this lane report's pre-dispatch body if the parent rejects the receiving record.

## Actual result

Executed one bounded receiving check of the retained DG18 records and original producer artifacts. Its 31 integrity/consistency predicates passed. The result is `RETAINED_RECORDS_CONSISTENT_AUTHENTIC_INPUTS_BLOCKED`; it grants no source qualification, native authority, original acceptance, currentness, or final cold receiving.

The held branch remains clean at commit `ef7bfa0590876f6a92ebe3dcdc833829f0d43c09`, tree `7ee35549c92eae66f7428cdb7f9eea2d15b64570`. No runtime source, controller, shared STATE/ROADMAP, or Git ref was changed. The existing 3 CLI cases, 99-check receiving receipt, and Windows 44/Linux 47 baselines were not rerun.

Receiving output: `/workspace/scratch/0269e6626329/dg18-continued/retained-record-receiving-20261115.json`, 28,000 bytes, SHA-256 `2fd32891f497727aa44a3f5bf67e04bae0fa9c15fbdf0846cb5392346de00274`.

## What the receiving actually checked

- Recomputed both retained pins cited by `EXECUTION_SCOPE_RECONCILIATION_20261115.json`: the existing hosted receipt and `N1_RETAINED_RECORD_CHECK.json`.
- Joined the held commit/tree to run `43676967250` through the retained receiving receipt, preserving its 3 passed source cases, 99 passed checks, no native-gate change, and zero original-acceptance delta. This is integrity readback of that receipt, not a replacement execution or reissued receipt.
- Recomputed the four selected core consumer pins and the existing C02 issuer-source pin against `INPUT_PACKETS.json`; all matched. The selected source remains `skills/implementaudit/scripts`. The `source-peers/native-runtime` issuer is an existing distinct adapter, not authority to change the selected core or appoint an adjudicator.
- Recomputed the exact original H0 `INPUT_TEMPLATE.json` at `faaa43e068bc758e28f1953d4204ce6aae1e543d`, plus the Windows `SOURCE_MANIFEST.json`, `prepare_and_execute.py`, and `entitlement-reference.txt` at `27a41c9b53f43244a97f03fa00a0b3e41ff8ab84`. All matched the retained original pins. The Windows entitlement bytes are exactly `UNGRANTED\n`.
- Verified the retained N1 identity, cutoff 109411, and mandatory audit-state obligation. Reservation is `RESERVED`, result and consumption are `PENDING`, currentness is `UNRESOLVED`, epoch and accepted witness are null, and covered boundary IDs are empty. The retained progress check is historical corroboration; its underlying large source was not reacquired and no owner/store was inferred.
- Confirmed every missing-record group in the supplied OR, C02 and W-FULL input packets remains null, and the current reconciliation says the actual N1 custodian records have not been received. This is bounded to the supplied records; it is not a claim of global absence.

## First blocked predicates

| Cell | First eligibility predicate not satisfied by actual supplied inputs |
|---|---|
| OR | No entitled existing source-owner `NativeInputState` lease with authentic current-host observation and applicable issuer grant. `canonical_rotation_inputs.py::rotation_input_lease_v1` requires the existing owner capability; a matching proposal or generic local-host observation cannot supply it. |
| C02 | No actual `CONTINUITY_ADJUDICATION_OWNER` retained decision, erroneous-event evidence, complete later-boundary/prior-decision census, or exact append grant. `ConfiguredC02IssuerV1` remains scoped `CONTROLLED_NONPROTECTED_FAULT_INJECTION`; it cannot self-authorize historical adjudication. |
| W-FULL | No exact final Windows operation record, fresh owner grant, actual Windows/tool readbacks, or two concurrent admitted DG16/DG17 owner originals. The historical packet remains explicitly ungranted and is not a current launch record. |
| N1 | No actual custodian fixed selection, supported owner attribution/current record, or assignment-bearing pending store record. The archival transport controller is not an owner substitute. |
| Original cold receiving | N1's result and accepted consumption are pending. The complete original criterion-5 receiving cannot finish from the retained progress label. |

These are eligibility findings from the actual records and source, not runtime failure codes from an attempted native operation. No OR, C02, W-FULL, N1, E/F, or protected episode was attempted.

## Minimum remaining authentic inputs from the existing producers

### OR

The original entitled current-host connection/source owner must provide the admitted unconsumed capability and its actual issuer grant, using the twelve-field binding required by `canonical_rotation_inputs.py::_validate_binding`: `issuer`, `grant_sha256`, `producer_sha256`, `semantic_contract_sha256`, `host`, `budget_policy`, `tokenizer`, `subject`, `source_bytes`, `source_tokens`, `thread_id`, and `turn_id`.

The subject binds controller, claim, run root, receipt token and the exact STATE/ROADMAP hashes. Host identity includes name/version, binary hash, effective configuration hash and model. Tokenizer identity includes name, implementation, version and encoding hash. Actual source-owned `rawResponse/completed` exact usage, a later matching reported-window record, terminal cutoff and wall/monotonic receipt clocks and stream revisions are still required. Freshness remains at most 30,000 ms. The pure `check_rotation_observation_v1` explicitly provides no effect authority; the fresh canary source explicitly labels its counters `DETERMINISTIC_LOCAL_RESPONSES_EMULATION`.

Source read: `skills/implementaudit/scripts/canonical_rotation_inputs.py` lines 85–227 and 508–525; `skills/implementaudit/scripts/rotate-canonical-state.py` lines 865–927; `source-peers/native-runtime/skills/implementaudit/scripts/compaction-source-owner-codex-app.py` lines 2394–2497.

### C02

The actual adjudication owner must provide its physically retained decision and configured route (`issuer`, `census_owner`, absolute `decision_path`, `owner_decision_locator`, `source_contract_locator`). The decision schema is `implementaudit.c02-configured-owner-decision.v1`, with `issuer`, `role`, `subject`, `decision_id`, `revoked`, `qualification`, `expected_old`, `source_cutoff`, `append_grant` and `conditional_fresh_grant` in addition to `schema`. The current adapter's qualification scope remains narrow and must actually apply.

The exact expected-old tuple is controller, claim ID, run-root identity, pointer OID, receipt OID, permanent-marker OID and invalidation OID; publication additionally binds controller OID and receipt ref. The actual erroneous event and complete later-boundary/prior-decision census must come from the admitted census owner. Its snapshot requires `census_complete: true`, `ordering: SOURCE_OWNER_COMPLETE_SEQUENCE`, exact source cutoff and the current grant revision. The actual append grant schema is `implementaudit.c02-issuer-grant.v1`, bound to issuer, exact event/expected-old scope, kind, `APPEND_ONLY_NO_CURRENTNESS`, consumer code hash and `revoked: false`. Any fresh transition needs its separately scoped actual grant. No empty census, owner decision or matching grant was fabricated.

Source read: `skills/implementaudit/scripts/claim-run-rotation.py` lines 169–248 and 3172–3247; `source-peers/native-runtime/skills/implementaudit/scripts/compaction-source-owner-codex-app.py` lines 1551–1642.

### W-FULL

The actual Windows operator and existing concurrent DG16/DG17 owners must provide a final-location operation record/digest with current source/helper/tool/population pins, a fresh written owner grant naming that exact record, physical Windows/tool readbacks, both admitted original owner records, and their overlapping live window/readiness. The accepting input still needs the exact preimage pair/owner map/current pointer/receipt/marker and a distinct receiver.

The original measurement contract starts before `CreateProcessW/CREATE_SUSPENDED`, assigns the root to a private job before resume, includes all descendants, and ends only at root exit plus `ActiveProcesses == 0`. It uses kernel `PeakJobMemoryUsed`, zero baseline subtraction, at most 60,000 ms and 201,326,592 bytes. The original Windows20 runner refuses absent entitlement before subject allocation; neither its historical source nor `UNGRANTED` can launch the current candidate. The Windows envelope does not extend OR freshness.

Source read: `INPUT_PACKETS.json::W_FULL`; original Windows `prepare_and_execute.py` at the pinned commit, especially `Campaign.__init__` lines 3967–4008 and result projection lines 4220–4235; retained `ISSUE215_ORIGINAL.md` lines 323–340.

### N1 and final receiving

The original custodian must supply the authentic fixed selection with `pending_owner {store, session_id, owner_id}` and `episode_owner {module_pin, repository, controller}`, supported H0 owner attribution/current-record readback, and `<store>/compaction-audits-v1/<session key>/pending.json` with the exact N1 assignment, actual reservation/result/consumption or explicit absence, and uncovered successors. The source reader binds these through `attribution`, the selected episode and assignment, actual RETURN/JOIN, qualified source custody and accepted coverage; a retained progress label is not that record. A subsequent bounded authentic audit-state operation still needs its existing exact-operation authorization, and final original cold receiving remains downstream of N1.

Source read: `source-peers/native-runtime/skills/implementaudit/scripts/compaction-audit-pending.py::read_selected_accepted_episode_v1`, lines 792–886.

## Contained read abnormality and scope

One exact historical entitlement read with Git lazy fetching disabled returned `bad object` because that blob had not been materialized locally. The same pinned commit/path was then acquired through ordinary Git object reading and passed exact byte/hash verification. Class: `transport-infrastructure`; disposition: resolved for this bounded read only. No alternate subject, grant or source was substituted.

No source fix was justified by this receiving. Zero native operations, model calls, new grants, UNKNOWN replays, protected effects, original-acceptance claims or external publications occurred. The actual effect frontier remains blocked on the authentic inputs above. The report and receiving JSON are the only owned writes.

BLOCKED
