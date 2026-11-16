# R0039 — Deterministic canonical current-state rotation with lossless archival and rehydration equivalence

**Authoritative status: OPEN / INCOMPLETE. R0039 is one Rockstar: issue #215.**

[PR #249](https://github.com/theislampill/IMPLEMENTAUDIT.md/pull/249), merge `0eb6fdaf00d827447dfe033f9052c32fe803bca1`, is implemented and qualified byte-rotation/Windows work at its demonstrated scope; it is not whole-R0039 completion.

**Parallel engineering:** R0039 continuation is authorised in its isolated worktree alongside R003A/#216. R003A/PR #247 retains ownership of its active changed paths and priority for final integration; overlapping R0039 integration will compose against its qualified merged result. Separate run roots and host homes are required, and only conflicting integration or resource-heavy qualification is serialised. R0039 remains OPEN / INCOMPLETE until its whole applicable original acceptance is earned; a separate exact-source approval is required before any continuation merge.

```text
NEW_RXX=YES
PUBLICATION_TARGET=R0039
SEMANTIC_OWNER=CANONICAL_CURRENT_STATE_GENERATION_TRANSACTION
```

## Problem

Long-running audit campaigns accumulate canonical `STATE.md`/`ROADMAP.md` content
until re-entry itself becomes costly and stale-history confusion rises. Current
continuity machinery binds controller, epoch, next action and STATE/ROADMAP hashes,
but no current owner automatically and safely rotates those canonical current
projections from authoritative history while preserving exact actionable meaning.

This is not R0038 operational observability: R0038 is read-only and cannot author
STATE/ROADMAP. It is not `audit-state`: that child interprets an already current
checkpoint and has no mutation/currentness authority. R0037 and continuity define
current-run semantics but do not own deterministic rotation.

## Invariant

When an explicit calibrated size/token/context-health trigger fires, one deterministic,
single-writer transaction may produce a bounded canonical current STATE/ROADMAP
pair plus an immutable hash-bound archive only when the zero-model equivalence
oracle proves every protected state class/relation is preserved. A fresh-context
canary is separate candidate/release qualification, never the per-rotation gate.
The preimage is never deleted.

## Authority and state direction

```text
authoritative append/history/evidence owners
-> deterministic current projection + immutable archive
-> continuity invalidation/new receipt
-> ordinary governor re-entry

current projection -> R0038 read-only consumer
current projection -> audit-state only when model judgement is separately warranted
```

Derived R0038/Cupola/model output can never become the preimage or authorize the
write. The rotator owns only its canonical pair/archive transaction and no lifecycle,
release, closure or external effect.

## Authoritative preimage

There is no proved complete append-only event store today. The authoritative
preimage is therefore the exact current complete `STATE.md` + `ROADMAP.md` pair,
plus an enumerated hash-bound owner map for every referenced run artifact/evidence
needed to interpret that pair. Supporting history cannot silently outrank live
current state.

The preimage manifest records schema version, controller, run/audit object,
candidate/tree/package/PR/release identities, current epoch/receipt, both file
hashes, owner-map denominator and each referenced artifact hash/role/currentness.
Missing, contradictory, duplicate or unknown owners are STOP. The complete
protected-state population is:

- phase/status/audit object, exact next action and the closed
  `DONE + ACTIVE + READY + BLOCKED` frontier; unknown states refuse projection;
- active, satisfied, superseded, revoked, expired and ambiguous
  instructions/authorisations, including issuer, scope and applicability;
- current continuity generation/epoch, invalidation event/object, predecessor
  receipt identity and expected successor receipt ref/schema; the successor
  receipt OID is a derived post-pointer binding outside the pair hash; plus pending
  terminal one-shots, terminal-marker state, handoffs and external effects;
- current Andons and preserved original REDs;
- unresolved obligations, deferrals and revisit triggers;
- non-verdicts, evidence ceilings, dependencies and compensations;
- remembered steer dispositions/activation gates, rollback state, runtime
  artifacts and unknown/contradictory values.

Each protected field has exactly one owner and one omission/semantic-mutation
fixture. The protected manifest is partitioned without overlap:

1. `PRESERVED_PAYLOAD`: audit/run/candidate/package identities, instructions and
   authority dispositions, DONE/ACTIVE/READY/BLOCKED frontier, obligations,
   exact next action, effects, Andons, steers, evidence burdens, dependencies,
   rollback and all values that must remain equal;
2. `MONOTONIC_TRANSITION`: unique projection generation, canonical successor
   continuity epoch, unique invalidation and predecessor receipt, each governed by
   an exact predecessor/successor relation and never reused;
3. `DERIVED_BINDINGS`: pair, protected/archive manifest, pointer and receipt refs/
   hashes, verified by recomputation rather than copied equality;
4. `ARCHIVED_ONLY_HISTORY`: superseded bytes, generations and receipts that remain
   retrievable but can never resolve as current.

“Same actionable continuation” means exact preserved-payload field/relation equality
plus the permitted monotonic transition algebra. Mutation fixtures reject skipped,
reused, reordered or substituted epochs/invalidations/generations/predecessors and
any protected-payload semantic change.

## Selected atomic generation and reader protocol

Use immutable generation directories at
`.IMPLEMENTAUDIT/runs/<run>/state-generations/<generation-id>/`, containing the
canonical pair, protected-state manifest and typed archive pointers. The sole
discoverable authority is Git ref
`refs/implementaudit/current-generations/<controller>` pointing to an immutable
blob with schema `implementaudit.current-generation.v1` and fields:

```text
controller, claim_id, run_root_identity, projection_generation_id,
continuity_epoch, invalidation_oid, predecessor_receipt_ref_oid,
expected_receipt_ref_schema, projection_schema,
state_sha256, roadmap_sha256, protected_manifest_sha256,
archive_manifest_sha256, exact_next_action
```

The existing `claim-run.sh` lock/controller gate and `git update-ref <ref> <new>
<expected-old>` are the only publication primitive. The record blob is written by
`git hash-object -w --stdin`; expected-old CAS prevents lost updates on Windows and
POSIX. The writer durably writes/rereads the contained files, validates path
containment and rejects symlink/reparse-point traversal before hashing the record.
CAS losers quarantine their undiscoverable candidate directory and never delete a
winner or preimage. Permissions/readback, object/ref identity, lock ownership and
crash recovery are verified before ordinary execution resumes.

Every canonical reader—including `claim-run.sh`, governor re-entry instructions,
validators and human recovery—resolves the ref blob and verifies every bound hash.
Compatibility readers fall back to the legacy root pair only when the ref is
absent; once pointer-aware writer/readers are qualified and the migration terminal
receipt is read back, ref absence or mixed root/pointer state fails closed and the
fallback is removed. Symlinks and filesystem rename alone are never authority.

### Durable migration marker

Ref absence is disambiguated by a second immutable Git-ref authority:
`refs/implementaudit/current-generation-migrations/<controller>`, written once by
`claim-run.sh` with expected-old zero after the first pointer/v3 receipt succeeds.
Its `implementaudit.current-generation-migration.v1` blob binds controller,
claim/run identity, first migration epoch, pointer ref/schema, terminal v3 receipt
ref/OID and `legacy_fallback_retired=true`. It is reread with the pointer and never
deleted or rolled back; later rotations do not rewrite it.

```text
marker absent + pointer absent + validated legacy schema -> legacy compatibility
marker present + pointer present + matching controller/run/schema -> pointer only
marker present + pointer absent/malformed -> STOP; never legacy fallback
marker/pointer controller-run-schema mismatch -> STOP
marker absent + pointer present -> FIRST_MIGRATION_INCOMPLETE; STOP until the
  current pointer + matching v3 receipt are verified and the permanent marker is
  expected-zero CASed/read back for that exact terminal receipt
```

Complete marker x pointer x receipt currentness table:

| Marker | Pointer | Receipt | Result |
|---|---|---|---|
| absent | absent | exact current validated legacy v2 | legacy compatibility before first migration only |
| absent | absent | absent, v3, invalidated or mismatched v2 | STOP |
| absent | present/valid | exact matching current v3 | `FIRST_MIGRATION_INCOMPLETE`; no ordinary work until marker CAS/readback |
| absent | present/valid | absent, v2, stale or mismatched v3 | STOP |
| present/valid | present/valid | exact matching current v3 | pointer route current |
| present/valid | present/valid | absent, v2, stale or mismatched v3 | STOP |
| present/valid | absent/malformed | any | STOP; never root fallback |
| malformed or controller/run/schema mismatch | any | any | STOP |

If first-migration marker CAS/readback fails, no ordinary execution resumes: every
new, recovered-old or verified-winner first-migration branch remains
`FIRST_MIGRATION_INCOMPLETE` until its exact current pointer/v3 is bound by the
permanent marker. Marker CAS failure, pointer/receipt drift during marker write or
an existing nonmatching marker is STOP; recovery cannot terminate pointer/v3-only.
The marker ref/blob is included in source, package/install, corruption/deletion,
winner and recovery fixtures; an ordinary file cannot substitute for it.

### Immutable archive authority

The archive root is the Git object database plus ref namespace
`refs/implementaudit/state-archives/<controller>/<projection-generation-id>`.
`skills/implementaudit/scripts/rotate-canonical-state.py` writes content-addressed
preimage STATE/ROADMAP and referenced protected artifacts with `git hash-object -w`,
then writes an `implementaudit.state-archive.v1` manifest blob and anchors it by
expected-zero `git update-ref`. The manifest binds controller/claim/run, predecessor
receipt, pair/artifact blob OIDs and SHA-256s, protected/owner-map schema and typed
retrieval roles. Objects are retrieved only through validated `git cat-file blob`.

Archive refs are retention/no-delete authority. They are outside run-root discovery,
current-generation, fixture and recursive archive populations; ref/path containment,
permissions and object/manifest readback are mandatory. Archive failure occurs
before pointer publication and is never a warning. No cleanup or retirement may
delete an anchored archive or preimage without a separately authorised retention
successor that preserves every typed object and genealogy.

## Deterministic equivalence oracle

Every rotation runs a zero-model deterministic oracle over the complete preimage,
four-part protected schema, owner/reference graph, transition algebra and current
pair. It proves preserved-payload equality, exact monotonic successor rules,
recomputed derived bindings and archived-only non-currentness. One-field omissions,
reused/reordered transition identities, stale pointers, owner changes and semantic
mutations fail. A fresh-
context human/model rehydration canary is an independent candidate/release
qualification cell, not a hidden model call on each rotation and not currentness
authority.

## Trigger and cost calibration

Bind exact byte threshold plus any token/context-health threshold to a named
tokenizer/host/version and a frozen calibration population. Admission requires a
measured minimum live-state reduction or decision/re-entry payoff, maximum runtime
and memory overhead, and a below-threshold non-trigger. Archives are content-
addressed/deduplicated; cumulative storage is measured. Rotation reduces live
re-entry cost, not total retained information. Storage-budget excess is an owner
decision, never silent deletion of preimages.

## Required design

- implement the complete-pair/owner-map preimage and versioned projection schema;
- implement the calibrated byte/token/context-health trigger and non-trigger/cheap path;
- preserve controller, audit object, candidate/package/PR/release identity, epoch,
  exact next action, DONE/ACTIVE/READY/BLOCKED frontier, unresolved obligations,
  pending effects, Andons, dependencies, steers and evidence limits;
- write an immutable content-addressed archive outside live validator/discovery
  roots with typed pointers for selective retrieval;
- publish immutable generations plus one CAS current-generation pointer; all readers
  detect/refuse mixed or incomplete generations;
- invalidate the prior receipt and mint/verify a new continuity receipt only after
  exact deterministic projection/equivalence success and the total transition below;
- expose no model call on the deterministic rotation path.

## Cold-executor owner and write map

After mandatory exact-current re-anchor, the preferred owners and order are fixed:

- `skills/implementaudit/references/continuity.md`: generation/currentness,
  pointer and receipt-v3 contract;
- `skills/implementaudit/scripts/claim-run.sh`: Git-ref/blob resolution, sole-
  writer lock, invalidation, fresh-epoch selection, CAS, receipt mint/verify/
  require, compensation and legacy migration;
- `skills/implementaudit/templates/STATE.md` and `ROADMAP.md`: protected-state
  schema, generation/pointer identity and legacy migration surface;
- governor Runtime Loop re-entry text: separate pointer-aware STATE then ROADMAP
  reads, fail-closed mixed-state behaviour and optional downstream `audit-state`;
- new `skills/implementaudit/references/canonical-state-rotation.md`: schemas,
  transition algebra, archive/pointer/migration and recovery contract;
- new `skills/implementaudit/scripts/rotate-canonical-state.py`: deterministic
  projection draft/finalizer and Git-object archive writer only; `claim-run.sh`
  remains the sole ref/CAS/invalidation/receipt authority;
- new `scripts/check-canonical-state-rotation.sh`,
  `tests/canonical-state-rotation.test.sh` and
  `fixtures/canonical-state-rotation/`: preimage/oracle/CAS/crash/receipt/
  migration/archive/rollback, omission, semantic-change and cyclic-hash cases;
- exact canonical registry insertion: `scripts/verify-package.sh`, whose parity is
  guarded by `scripts/check-validation-registry.sh` and
  `tests/validation-registry.test.sh`;
- package/generated/install owners: `package/implementaudit-package.json`,
  `scripts/package-contract.py`, `scripts/build-release-asset.sh`,
  `scripts/verify-package.sh`, `scripts/install-codex-from-release.sh`,
  `scripts/install-plugin-from-release.sh` and
  `scripts/install-claude-from-release.sh`; public claims are `NOT_TRIGGERED`
  unless exact shipped behaviour changes user-facing documentation.

The helper, reference, templates and `claim-run.sh` changes necessarily trigger
R0034 source-to-standalone/plugin/inventory/package/isolated-install parity. No
source-only PASS can satisfy that leg. If an exact live re-anchor shows any named
owner moved or was superseded, F0 STOPs and this issue is amended before design.

Ordered single-writer cells:

| Cell | Writer / expected result | STOP / rollback |
|---|---|---|
| F0 re-anchor | governor records exact candidate/tree/dirty/package/install and current pointer/receipt | mismatch -> STOP, no writes |
| F1 freeze RED/algebra | fixture proves current root-only path lacks atomic rotation; freeze preserved payload, four-part transition manifest, complete denominator and oracles | no discriminating RED or ambiguous field class -> amend issue |
| F2 draft/archive | rotation helper writes/rereads an undiscoverable projection draft with transition envelope absent and anchors the immutable archive; no current ref changes | write/read/hash/archive-ref failure -> quarantine draft; old receipt remains current |
| F3 readers/migration matrix | claim-run/governor/templates/validators qualify legacy, pointer and permanent-marker combinations | mixed/unknown or marker-present fallback -> restore old readers |
| F4 CAS/crash controls | sole writer qualifies expected-old Git-ref CAS, security, crash points, loser and recovery branches over fixtures | current ref uncertainty -> STOP |
| F5 transition identities | continuity owner creates `canonical-state-rotation` invalidation and fresh epoch after draft/archive PASS | reuse/substitution/failed invalidation -> old route only or STOP |
| F6 finalize/switch | finalize immutable generation with epoch/invalidation/predecessor receipt; compute hashes -> pointer blob -> expected-old CAS -> exact readback | branch-specific recovery below; no ordinary work |
| F7 receipt/currentness JOIN | mint/verify v3 outside pair hash cycle; on first migration write/read marker; require pointer+receipt(+marker) current | missing half, marker failure or v2/v3 ambiguity -> recovery/STOP |
| F8 exact-tree/package | focused test via `scripts/verify-package.sh`, full registry and unconditional R0034 package/install parity; native host separate | regression/missing layer -> restore verified pointer/readers or NONVERDICT |
| F9 independent review | cold review of exact candidate, receipts, archive/marker and current consumer readback | GAP/BLOCKED -> no retirement |

If live source disproves a preferred owner or order, STOP and amend this RLGWO;
the executor must not redesign the transaction ad hoc.

## Acceptance

1. A pinned large-root positive produces deterministic byte-identical outputs and
   a complete manifest; two clean roots agree.
2. Every protected class/relation has an owner/manifest member plus one-field
   omission and semantic-change mutations; unknown frontier/instruction/
   authorisation/continuity/terminal/steer states fail.
3. Archive content cannot be rediscovered as live current state or trigger recursive
   validators; old and new projections cannot both appear current.
4. Interrupted write, corrupt archive, stale receipt, concurrent writer, wrong
   controller/candidate, path traversal/symlink and Windows/POSIX path controls fail
   safely with the preimage recoverable.
5. A fresh-context rehydration canary derives the same identity, frontier,
   obligations, exact next action and evidence burden from the new pair.
6. Selective historical retrieval resolves exact typed pointers/hashes and cannot
   promote archived history to current authority.
7. Below-threshold/non-trigger campaigns retain ordinary cheap STATE/ROADMAP with no
   archive, model call or extra ceremony.
8. Rollback uses expected-current compensating CAS, never file presence; it
   restores a verified prior projection, records a fresh invalidation/epoch and
   proves controller/pointer/pair/currentness/next action with a new receipt.

9. Crash-point controls cover before archive write, before generation completion,
   before/after current-generation CAS and before/after receipt mint.
10. Exact-source integration censuses continuity, `claim-run.sh`, STATE/ROADMAP,
   governor re-entry instructions, validation registry, generated/package inventory
   and public claims. A baseline failure is preserved before source change.
11. If helper/schema/reference bytes ship, R001E/R0034 isolated-package/install and
   current-consumer evidence is required; otherwise the leg is `NOT_TRIGGERED`.
12. Omission/reordering mutations for invalidation, fresh-epoch selection, CAS,
   ref/blob readback, receipt binding and compensating CAS fail; legacy v2 receipt
   compatibility is proved or migration fails closed.
13. Permanent-marker/pointer absence/corruption/mismatch matrices prevent stale
    root fallback after migration. Archive refs/objects/manifests are complete,
    typed, retrievable, non-discoverable as current and retention protected.
14. The dependency graph is acyclic: draft/archive -> invalidation/epoch -> final
    pair/manifests -> pointer OID/CAS -> receipt OID -> first-migration marker.
    Any fixture embedding the future receipt OID upstream fails.

### Complete original R0039 acceptance

R0039 is this single work order, issue #215. All fourteen criteria above, the [criterion-5 amendment](https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/215#issuecomment-5638756120), and the C02 obligations below remain required here. The existing semantic owners and consumers are implementation boundaries within R0039, not separate completion issues.

1. **Authentic byte/token/context-health OR qualification.** Admit the actual current-host observation producer and issuer/grant, binding exact population/bytes, tokenizer/version/encoding, host applicability, observation identity/scope/cutoff/freshness, and unknown/stale/future failure behaviour. The consumers are `rotate-canonical-state.py::check_rotation_observation_v1`, `rotation_trigger_v1`, `rotation_payoff_v1` and the accepting `claim-run.sh --rotate-canonical-state` path. Independently qualify each OR arm, boundary and non-trigger, minimum payoff, and rejection of unauthenticated, foreign, unknown, stale or future observations. Pure interfaces and tiktoken 0.13 payoff measurements do not admit context health or complete this requirement.

2. **Real H0, compaction identities, coverage and pending boundaries.** Bind the existing actual H0 witness, original physical/source identity and evidence locator, offset/hash/ordinal, prefix cutoff, observation scope, reservation, actual result, accepted-consumption witness or explicit absence, and surviving uncovered successors. The existing R0033/continuity occurrence and pending-boundary acceptance/JOIN consumers retain their mechanisms: source-pin the entitled version of `compaction-audit-pending.py::operate` (join) and `apply_covered_versions`; a later installed copy is not automatically admitted. R0039's projection and paired readers must preserve these facts. Two proved compactions under unchanged H0/currentness labels must survive rotation and cold receiving; acceptance of the first clears only its actually proved coverage and leaves the uncovered successor pending. Missing, failed, incomplete, reserved or merely dispatched results cannot erase obligations. Original13520 documentary acceptance does not consume14114 or authenticate archived native fields.

3. **Original/current/prior/retry discrimination.** The existing R0033/continuity occurrence-selection and attempt-evidence consumers must bind the applicable source/version, original/current/prior/retry identities, original cutoff and early-use/refusal evidence. Qualify a valid selected prior occurrence and supported retry while rejecting identical copied, foreign or unselected occurrences, changed physical file identity/offset/hash/ordinal, repeated call IDs offered as proof, and an incorrect original response followed by a later correct response. R0039 must preserve these meanings through projection and receiving. Later repair cannot retroactively validate the original occurrence; no historical replay or invented compaction may supply missing evidence.

4. **Complete amended criterion-5 cold receiving.** An independent non-authoring receiver must consume the exact preimage STATE/ROADMAP, interpretive owner map, projected pair, archive, receipt/marker and authentic occurrence bindings. Derive the same identity, frontier, obligations, exact next action and evidence burden, and qualify the complete amendment population. Preserve mandatory completed-compaction/resume audit obligations even when currentness is unresolved or a measured epoch is absent; execution does not mint either authority. No real pending, unknown, failed, reserved or uncovered obligation may disappear or become optional/satisfied. Explicitly distinguish TC06 continuing reader/marker/archive/acceptance duties for supported old consumers after new rotations are disabled from TC11 historical validity with only affected current use invalidated by changed meanings/grants. The constructed core canary alone does not complete this requirement. Deterministic rotation is not a host-compaction event.

5. **Authenticated and entitled C02 append-only correction publication.** `CONTINUITY_ADJUDICATION_OWNER` must supply the applicable issuer/grant and actual erroneous-event evidence, exact expected-old pointer/receipt/permanent-marker and claim/run identities, and a complete later-boundary census. The existing continuity/claim sole publication owner must consume the decision through a compatible authenticated accepting adapter; `claim-run-rotation.py::propose_c02_correction_v1` is only a pure proposal. Actual authorized publication and independent host readback must prove append-only correction, exact retry/idempotency, conflicting-kind/replay/ambiguity refusal and immediate admission of a genuine newer boundary. Preserve generation-v1, projection-v2, fourteen-field receipt-v3 and F0–F9 ownership/order unless their existing owners explicitly accept a protocol amendment. Ordinary compensation/resume and an incompatible eighteen-field mutable-root peer are not C02 acceptance. Unknown relevant boundaries or missing entitlement stop the accepting effect.

The full amended canary depends on the authentic occurrence and prior/retry bindings. C02 retains its own actual entitlement and complete-census prerequisites. No new pending store, observer, router, currentness writer, controller or producer self-appointment is authorised. These are R0039's own incomplete requirements; no issue closure, source PASS, fixture labels, matching hashes, copied commands or model answer substitutes for their accepting consumers.

**Performance qualification.** The prospective Windows full-operation envelope remains 60,000 ms and 201,326,592 bytes (192 MiB) peak aggregate job committed memory, where technically applicable to the pinned population and verified process/descendant accounting, with zero baseline subtraction. It is not a universal hard deadline or a budget for other hosts. Existing security checks and test deadlines remain. Original R0039-F1-CAL-v2 and its 5-second/64-MiB failures remain historical evidence; removing the organisational split neither reinstates an arbitrary five-second limit nor commissions further performance optimisation. This envelope waives no original functional requirement.

Reuse PR #249's accepted deterministic/omission/transaction controls, Windows custody, source reviews, isolated installs and selected native Codex receiving at their demonstrated subjects. Preserve original calibration and cost failures, incomplete-memory accounting, packed-object/ref-parser findings, refused same-version update, timeouts/skips, LR10-C's separate existing disposition, native identity/census/ref failures, observation cutoffs and pending/unknown facts. The correction05 source work is not native producer authentication.

Existing original input custody remains `R0039_OCT22_OWNER_RETURN.md` (SHA-256 `486266effef8dac8a76cbac52cde417e1238226aaea8ef79fff3af420aff48b5`), `R0039_OCT22_MANIFEST.json` (`ae7936326961dc4a5571392e4f0e9fa8f757a1289ef9f0ffb40654bfe64008a1`) and `R0039_OCT22_EVIDENCE.zip` (`664dddca0433bab9dba941a12001f940bc80eb83cfaa0d76d7c7645dc84f943a`). Keep the real evidence and negative results available without treating any prior scoped certificate as whole-R0039 acceptance.

R0039 remains OPEN / INCOMPLETE until its whole applicable original acceptance is earned. No original-predicate, whole-cell, campaign M, native-currentness or full-release credit is changed by this administrative restoration.

## Total receipt and rollback state machine

1. Under a mechanically current predecessor receipt and sole-writer gate, freeze
   the preserved payload and build/reread an undiscoverable projection draft plus
   anchored archive. The draft explicitly contains no epoch/invalidation/receipt-
   successor envelope and is not an immutable final generation.
2. Create a unique invalidation with boundary
   `canonical-state-rotation` and allocate the canonical fresh successor epoch.
   Its event binds controller/claim/run, exact old/new projection IDs and the
   predecessor receipt; it cannot masquerade as host compaction, new session,
   handoff, manual resume or inferred context gap.
3. Finalize a new immutable generation from draft + fresh epoch + invalidation OID
   + predecessor receipt ref/OID + expected v3 receipt ref/schema. Compute pair,
   protected/archive manifest hashes, then hash the pointer blob. The future new
   receipt OID is deliberately absent from the pair/pointer.
4. CAS `refs/implementaudit/current-generations/<controller>` from exact old pointer
   OID (or expected-zero on first migration) to exact candidate pointer OID and
   reread ref/blob/pair/manifests.
5. Mint `implementaudit.continuity-receipt.v3` from the already-known pointer OID
   and resolved hashes. It binds controller, claim/run, fresh epoch, invalidation,
   pointer ref/OID, pair/protected/archive manifests, exact next action and
   predecessor receipt. The receipt OID lives only in its controller/epoch receipt
   ref. `require-current` joins pointer + receipt ref/OID and refuses either alone.
6. On first migration only, expected-zero CAS and reread the permanent migration
   marker binding the terminal v3 receipt; then require-current joins marker,
   pointer and receipt. This closes the legacy fallback without a hash cycle.

Exact failure branches:

- **CAS fails and pointer ref is still exact expected-old:** create a recovery
  invalidation and fresh recovery epoch first; finalize/hash a recovery record
  pointing to the still-current old projection; expected-old CAS it; mint/verify a
  recovery v3. On first migration, write/read the permanent marker for that exact
  recovery receipt before currentness. The failed candidate is quarantined and
  never current.
- **CAS fails and pointer ref changed:** the old projection is history, not presumed
  current. Do not publish a recovery record. Verify the winner pointer plus its
  current receipt; if this is the first migration, the winner/recovery owner must
  also write/read the permanent marker for that exact winner receipt. Return only
  after the marker+pointer+v3 JOIN; otherwise STOP while that writer owns recovery.
- **CAS succeeds but readback/receipt/first-marker fails:** under the same recovery
  owner, create a second recovery invalidation and fresh epoch first; finalize/hash
  a recovery record for a verified prior projection; compensating-CAS from the exact
  failed pointer OID; mint/verify recovery v3. If first migration is incomplete,
  write/read the permanent marker for that recovery receipt. A successfully written
  permanent migration marker is never removed; recovery remains pointer-only.
- **Any pointer, writer, invalidation, epoch, CAS, receipt, marker or winner
  uncertainty:** STOP/BLOCKED. No retry, fallback, old-receipt reuse or ordinary
  execution. File/archive presence is not rollback success.

Accepted terminal states are exactly: new projection + current v3 + permanent
marker; verified old projection via a fresh recovery pointer/v3 + permanent marker;
or a complete verified winner pointer/v3 + permanent marker. The marker is already
present on later rotations; every first-migration terminal creates it. Every other
state is STOP. Fixtures record
pointer/receipt before and after, sole writer, discoverability, cleanup and exact
terminal result for every branch.

Receipt-v3 migration is pointer-aware and version-discriminated. Before the
controlled switch, v2/root and v3/pointer readers are tested on exact fixtures;
after the migration terminal receipt, v2 or root fallback is refused. Crash-point
and mutation fixtures cover every numbered transition, all order inversions,
boundary-provenance substitution and attempted future-receipt-OID embedding; the
latter must fail as a cyclic construction.

## Lifecycle and retirement

STOP on incomplete preimage, unknown owner, unresolved reader migration, failed
equivalence, mixed generation, archive write/readback failure, insufficient payoff,
package skew or unrecoverable rollback. Retirement may disable future rotation and
remove the generation writer only after no active transaction; migrated-run pointer
readers, permanent markers and archives remain supported. Removing them requires a
separately proved pointer-to-successor migration with fresh receipts and no legacy
fallback. This owner never becomes a general event
store, scheduler, dashboard, model router, lifecycle/closure or release authority.

## Genealogy and dependencies

- R0005: deferral/supersession/history visibility;
- R0009/R0011: interruption durability and run-root/currentness mechanics;
- R0037/#211: L2 durable current-run semantics;
- R0033/#207 and `audit-state`: downstream cognition and explicit non-authority;
- R0038/#214: optional read-only operational consumer only.

No source branch, PR, merge or release is authorized by this filing.


<!-- implementaudit-v041-current-state-reconciliation -->
## v0.4.1 current-state reconciliation (2026-09-07)

This additive section supersedes stale current-status statements in the historical body; it does not rewrite accepted history or itself grant implementation, qualification, release, publication, tracker-closure, or native AthruK credit.

- Current semantic status: `ENGINEERING_REQUIRED`
- Current statement: Canonical rotation must adjudicate erroneous invalidations without deleting history and admit a genuine newer boundary immediately.
- Applicable accepted evidence: G02A8 pointer/receipt/marker and bounded currentness machinery are reusable.
- Proof/authority limit: One-time raw CAS rescue is dogfood evidence, not native recovery qualification.
- AthruK relationship: `E, H, K`
- Auto-LOOM relationship: T4/T5 pure reducer plus separate authenticated publication adapter
- First remaining discriminator/prerequisite: Append-only authority projection, guarded correction, idempotency/ambiguity/supersession RED bank and host proof.
- Next consumer/owner: `CONTINUITY_ADJUDICATION_OWNER`
- Release accounting: no release cell closes from this reconciliation; required remaining remains 26 plus conditional B-F3.
- Frozen proposal source: `sha256:baf4ab4600363cf3047664fea87971e593a423a55de0a2ab9df8c0d15235770c` (local run evidence; not public authority).


<!-- thread8-triad-integration-f4c2a199743d -->
### Bounded SSS x BWP x AMA integration input

Equal bytes do not preserve decision applicability across changed meanings or grants. Keep historical verdicts at their original scope and invalidate only affected current use; recovery must account for coherent versions, descendants and pending effects.

[Reviewed source and issue crosswalk](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/0e175fe64cbd4846fbf8e06c8b2ede12295c514c/docs/research/implementaudit/triad-integration/ISSUE_ADJUDICATION.json); [draft integration PR](https://github.com/theislampill/IMPLEMENTAUDIT.md/pull/223). The isolated canonical package gate remains failed at the frozen identity-convergence gap. This note grants no governor admission, native authority-NONE, runtime/install/release qualification or issue closure. Existing owner and qualification obligations remain in force.
