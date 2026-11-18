# Independent focused rereview: retained M4 join v2

**Disposition: PASS at the prospective pure input/row-join repair scope. Authority: NONE.**

The sealed v2 repairs F1: an L04 row naming `retained_m4_receiving` now requires successful exact-body receiving for every disposition. Both originally adverse cases refuse without bodies. No other candidate source changed. Original row constants, accepted-L04 requirements, Q06 separation, L07 residuals, and the complete-G3 conjunction remain intact.

**Hosted integration remains blocked because it is not implemented or proven.** This PASS closes the reviewed candidate defect; it does not award a row/cell, adopt source, establish current custody, authorize a protected operation, or imply original G3 completion. The v1 GAP report and failure witnesses remain unchanged.

## Bound packet and exact delta

| Item | Bytes | SHA256 |
|---|---:|---|
| v2 `REVIEW_MANIFEST.json` | 3,844 | `102bba7f73733ddd6891a3d7c0466fa473e810dfda214f286d7b3a3bd0bb324f` |
| v2 candidate | 11,914 | `4323cfd28e169bd38919e2086f4f45b892bf2e1521a5cd7a59b6eb6f860f37a9` |
| v2 supplied tests | 10,692 | `e65396a7d92894eb011b456dc3779c975d56df36de88e0e558610f4100e8e537` |
| Frozen original G3 | 153,706 | `b85cca1550ff8e7c1c89778180e53a5c70f306f0c8725ba60ef3ccd4bbc3a6ad` |

All 17 v2 members matched manifest byte counts and SHA256 identities before and after the focused test run. All 11 v1 members also remained exact. Packet files remained mode 0400; their bytes and permissions were not changed. The prior report/result copies in v2 match the original review outputs byte-for-byte.

The candidate change is exactly these two added lines inside the existing L04 branch, before disposition handling:

```python
if 'retained_m4_receiving' in row['evidence']:
    need(retained is not None, 'EXACT_RETAINED_M4_REQUIRED')
```

A direct byte comparison established that adding those lines to v1 produces the complete v2 candidate. All other code is unchanged. The supplied test change adds exactly the two requested negative methods; removing those methods yields an AST identical to the original test module. The new lines and methods were inspected before execution and introduce no filesystem, network, controller, or effect operations.

## F1 disposition and focused evidence

**F1: CLOSED FOR V2.** The original v1 GAP remains historical truth.

Fresh command:

```text
python -I -B /workspace/scratch/2678f1e431c3/g132-m4-join-review/v2/run_focused_review.py
```

Exit 0. **Nine focused supplied tests passed: zero failures, errors, or skips.** Two additional valid-body controls passed. The author-reported full 18-test result was retained and read, but the full suite was not rerun; this rereview stayed focused on the concrete defect and affected acceptance boundaries.

| Focused check | Observed result |
|---|---|
| Partial L04 names retained token, no bodies | Refused with `EXACT_RETAINED_M4_REQUIRED`. |
| Unreceived L04 names retained token, no bodies | Refused with `EXACT_RETAINED_M4_REQUIRED`. |
| Accepted L04, no bodies | Still refused. |
| Accepted L04 with exact bodies, missing explicit token | Still refused. |
| Accepted L04 with exact bodies and explicit token | Prospective row validation succeeds; no awards or live G1/G3 proof. |
| Original-key partial L04 without retained join | Remains valid in both the original pure validator and candidate. |
| Retained token used by Q06 or another row | Still refused. |
| L07 stronger-claim residuals removed | Still refused. |
| Any other original row partial, G3 declared accepted | Still refused. |
| Partial L04 with named token and exact bodies | Validates without promoting the disposition or awarding anything. |
| Unreceived L04 with named token and exact bodies | Validates without promoting the disposition or awarding anything. |

Only inspected AST-selected pure candidate declarations were executed. Original execution was limited to the previously reviewed, byte-pinned pure row validator for the unchanged legacy-path control. Neither full module was imported. Candidate main and filesystem reader were not run. Body fixtures were disposable exact copies of the already-public pinned files; all writes were confined to this v2 review directory.

The retained pre-repair regression log is 1,786 bytes, SHA256 `c2e3a347271929601798a7bab388be481cf2102e3be217eadec88c6fde9957fb`. It records both failures as `Refusal not raised`. This matches the independent original witnesses and was not discarded when v2 passed.

## Preserved original contracts and historical M4

All five original constants remain identical to the frozen source: IDs, scopes, dispositions, residuals, and original proof keys. The shared proof allowlist was not expanded. The exact two-line source delta leaves the existing G1/G3 gate evidence restrictions unchanged, including the refusal of the retained token as gate evidence.

The accepted-L04 branch still requires all four exact retained bodies, explicit L04 evidence, and the exact accepted-episode residual. The new pre-disposition guard strengthens only reference closure. It neither relaxes the original conjunction nor requires an already accepted historical event to be performed again.

The five public retained bodies and the independent retained-receiving record are byte-identical to v1. The original Root acceptance of M4/R35-L04 at run 44076469956 remains preserved, with no missing original predicates and no required M4 rerun. The historical receipt remains historical input: no new acceptance, issuer authentication, or current host custody follows from reading it. The review did not reopen M4 or repeat the archive recombination, native execution, dispatch, or Root consumption.

## Remaining hosted integration requirements

The unchanged original source still has the integration gaps documented in the v1 report. They are requirements for a new actual consumer, not additional predicates for the accepted M4 episode:

1. Bind the exact retained bodies and derived receiving to the actual `prepare_final_request`/`validate_public_final_request` population and independent proof consumer.
2. Keep added proof transport binding separate from global row/gate permissions. Do not append the retained token to the shared original `FINAL_PROOF_KEYS`, which authorizes evidence for Q06, other rows, and gates.
3. Wire `validate_final_decision`, `decide`, its retained projection, and `validate_original_receipt` consistently to the same exact retained binding. The frozen row validator still refuses accepted L04 in those unmodified paths.
4. Include newly consumed inputs in the actual acquisition and `final_census`/held-identity/currentness checks. Preserve upstream G1, native graph, receipt, deadline, and currentness requirements.
5. Bind executable source/package/pins and independent/source-applicability reviews. Preserve refusal diagnostics and the live Root issuer/decision path. Root owns source adoption, integration, acceptance, and publication.
6. Preserve the unknown original protected G132 outcome and its no-replay boundary. This review supplies no protected grant or evidence that the earlier effect did not occur.

No original consumer/operator, hosted action, controller operation, branch/ref mutation, native event, grant, or protected effect was performed. No nested child was routed. Original G132 remains `UNKNOWN_NO_REPLAY`; ancestor JOIN remains blocked. Existing unequal G2, expired M4 attempts, bundle failure, pure-checker scope ceiling, correlated evidence, Q06 residuals, and L07 stronger-claim limits remain preserved.

## Retained v1 review lineage

| Record | Bytes | SHA256 |
|---|---:|---|
| v1 review manifest | 2,726 | `4476231306669f0358bb5f861c074b20b79c28ed47e2bffddc8e3002b16ad64a` |
| v1 GAP report | 15,400 | `e9b8f73d8e233d06574943b270fe7dbef591ff7b6ed1ee329bebb7402ac8c8ca` |
| v1 structured result | 6,666 | `c6bb9af862e85c06e8dd2a3d6768168bc18998cb6a8d93071780793cb339a56c` |
| v1 independent failure witnesses | 2,653 | `1e9fa06e54c3c4dc33f93e190f1fc7c822d9cdad492a4933ee7197c149348dba` |

**Final scope:** PASS for the v2 F1 repair and preserved prospective pure-row contracts. Hosted executability and operational acceptance remain unproven and with Root.
