# Canonical current-state rotation — R0039

Status: **portable candidate; shared integration and native qualification are
separate**. Related to #215. No lifecycle, closure, release, occurrence-observation,
pending-consumption or model-routing authority.

`scripts/rotate-canonical-state.py` binds `scripts/canonical_hot_projection.py`
by exact bytes/hash. Review, package and copy both together. The private claim-run companion is part of the
existing claim-run owner, not authentication against arbitrary same-principal
code execution. `/implementaudit` remains the governor, with four bounded child
skills. The deterministic rotation path makes zero model calls.

## Admission and complete preimage

Input is the complete current STATE/ROADMAP pair, exact owner map and every
declared artifact. Only actual claim-run currentness admits preparation; archives,
files, fixture labels and pure-function results cannot.

The qualified pair grammar is `implementaudit.canonical-pair.v2`. Each UTF-8/LF
Markdown frame precedes one canonical JSON body. Parsing requires byte equality
with the regenerated complete file. Extra text, duplicate
JSON keys, unknown states/owners, missing declarations, unsupported legacy prose,
mixed pairs, omitted empty values and altered evidence hashes refuse. A native
owner must explicitly migrate an unsupported large legacy pair; no heuristic
summary or second authoritative event store is introduced here.

STATE owns identity, continuation, all instruction and authorisation dispositions,
terminal/effect/one-shot state, Andons, original REDs, non-verdicts, evidence
ceilings, steers, rollback, runtime artifacts and pending boundaries. ROADMAP owns
the closed DONE/ACTIVE/READY/BLOCKED frontier, obligations, deferrals,
dependencies, compensations and planning. Each group carries one declared native
owner. Owner-map rows cover every JSON-pointer leaf, including empty containers,
and bind owner, exact source, source digest and value digest. Artifact declarations
in the pair determine the denominator; the caller cannot shrink it. One exact
current receipt and one WORK_GRAPH are mandatory. Other declared evidence is
read from contained, non-aliased paths and hash bound. WORK_GRAPH bytes and the
closed frontier are preserved; this does not independently certify an external
graph owner's semantic decisions.

The four manifest partitions are disjoint:

| Partition | Rule |
|---|---|
| PRESERVED_PAYLOAD | Exact equality of every protected value, relation, owner and evidence burden. Terminal/satisfied/revoked history-bearing dispositions remain protected. |
| MONOTONIC_TRANSITION | Exact unused projection generation, native successor epoch, fresh invalidation and actual predecessor receipt. An explicitly recorded failed allocation permits the next recovery epoch without fabricating an intermediate receipt. |
| DERIVED_BINDINGS | Recompute pair/protected/archive hashes and expected pointer/receipt scopes. Future receipt and future pointer OIDs cannot appear upstream. |
| ARCHIVED_ONLY_HISTORY | Exact typed retrieval of previous pair/history bytes; never currentness or retroactive acceptance. |

`validate_protected_payload_v2`, `parse_canonical_pair_v2`,
`derive_hot_pair_v2` and `verify_projection_equivalence_v2` are pure. They expose
`NO_CURRENTNESS_AUTHORITY`. Equivalence independently reparses the original
inputs and recomputes the full candidate; it never trusts a caller's PASS bit.
An F2 candidate has `transition: null`, with no successor envelope.

Predecessor and prepared descriptors have closed fields: unknown keys, wrong
types, mismatched scopes and future bindings refuse before archive/final-file
effects. Archive readback reparses the whole pair, owner map and declared artifact
denominator. `archive_retention_guards` binds every ancestor and object anchor
into claim-run's publication CAS.

Optional paired `native_guards` preserve original native Markdown as protected
values. STATE Status/Next action exactly mirror typed continuation; only the owner
transition supplies Current epoch. Adapters retain the canonical bytes and derive
native validator views. Missing profiles refuse native validation; ordinary legacy
roots retain their route. Readers recheck owner and snapshot before success or
mutation-authority evidence.

## Required transaction and sole writer

The exact order is:

1. Claim-run admits the mechanically current predecessor and obtains its rotation
   lease. Freeze the complete pair/owner population.
2. The helper captures and verifies immutable preimage objects, anchors the
   archive and constructs an undiscoverable, independently checked draft.
3. Claim-run creates the unique `canonical-state-rotation` invalidation and
   allocates the exact fresh epoch. A rotation is never relabelled as compaction.
4. The helper finalizes the immutable generation from verified archive/draft and
   the owner-supplied transition. It computes pair/manifests; claim-run hashes the
   exact pointer blob and performs expected-old CAS plus readback.
5. Claim-run mints and verifies the v3 receipt after the pointer OID is known.
   The receipt OID stays outside all upstream pair/pointer hashes.
6. On first migration, claim-run expected-zero CASes and rereads the permanent
   marker. Ordinary work requires the complete pointer/receipt/marker JOIN.

Immutable final files reside at
`.IMPLEMENTAUDIT/runs/<run>/state-generations/<Gxxxx>/`. A `draft/` child is
undiscoverable and is never a final generation. The sole current selector is
`refs/implementaudit/current-generations/<controller>`, whose immutable JSON blob
has schema `implementaudit.current-generation.v1` and exactly these fields:

```text
schema, controller, claim_id, run_root_identity, projection_generation_id,
continuity_epoch, invalidation_oid, predecessor_receipt_ref_oid,
expected_receipt_ref_schema, projection_schema, state_sha256, roadmap_sha256,
protected_manifest_sha256, archive_manifest_sha256, exact_next_action
```

The projection schema is `implementaudit.protected-projection.v2`. Hashes are
SHA-256; Git object IDs use the repository's qualified SHA-1 format. Only claim-run writes current-generation, invalidation, receipt and migration
refs and verifies native identity/transition provenance; helper results cannot
replace those gates.

Receipt v3 uses the original fourteen-field TSV wire, with exactly one final LF:

```text
schema controller claim_id run_root_identity continuity_epoch invalidation_oid
pointer_ref pointer_oid state_sha256 roadmap_sha256 protected_manifest_sha256
archive_manifest_sha256 exact_next_action predecessor_receipt_ref_oid
```

Actual fields are tab separated on one line. The marker is the original `implementaudit.current-generation-
migration.v1` record under
`refs/implementaudit/current-generation-migrations/<controller>` and binds the
first terminal v3 receipt. It is permanent: later rotation/recovery never rewrites
or removes it.

## Reader and migration matrix

Every reader must resolve and verify the selector before reading a canonical
pair. Re-entry reads STATE then ROADMAP in separate completed host actions,
binding both to the same observed pointer token. A changed token is a boundary,
not permission to mix files. Human recovery uses the same verified paths.

| Marker | Pointer | Receipt | Admission |
|---|---|---|---|
| absent | absent | exact current legacy v2 | Legacy compatibility before first migration only |
| absent | absent | absent, v3, invalidated or mismatched v2 | STOP |
| absent | valid | exact current matching v3 | FIRST_MIGRATION_INCOMPLETE until marker CAS/readback |
| absent | valid | absent, v2, stale or mismatched v3 | STOP |
| valid | valid | exact current matching v3 | Pointer route current |
| valid | valid | absent, v2, stale or mismatched v3 | STOP |
| valid | absent or malformed | any | STOP, no root fallback |
| malformed or wrong controller/run/schema | any | any | STOP |

Ref absence and broken refs are distinct. An ordinary marker file does not
replace the permanent Git marker. Copying a generation into a legacy root does
not restore currentness. claim-run's currentness JOIN must be rechecked after
every observed change; file paths by themselves carry no authority.

## Archive and retained objects

The archive authority is
`refs/implementaudit/state-archives/<controller>/<preparation-generation>` with
schema `implementaudit.state-archive.v1`. It binds the admitted controller,
claim/run, complete predecessor identity, source pair, owner map, typed artifacts,
source modes, hashes and blob OIDs. Every retained payload blob also has an
expected-zero anchor under the reserved `objects/<oid>` subnamespace. This is
necessary because Git does not traverse OIDs written inside a JSON blob during
garbage collection. Archive manifests alone cannot retain their referenced
payloads. Immutable claim-run transition records use the reserved `epochs/<Gxxxx>`
subnamespace for crash recovery; neither subnamespace is an archive generation.
After final bytes produce the exact candidate pointer OID, claim-run retains a
separate `epochs/<Gxxxx>-publication` intent binding that OID, the expected-old
selector and the prior epoch record. This is downstream of the immutable
projection hashes and upstream of CAS. Recovery uses it to distinguish the
owner's failed pointer from a substituted same-epoch pointer. It is neither a
second current selector nor permission to mint a receipt for a failed allocation.

Typed history pointers bind the exact manifest ref/OID/SHA-256, source role,
source SHA-256/Git blob/byte length, JSON pointer, record identity, record hash and
native owner. Retrieval validates the complete anchored population before
returning the selected raw pair or canonical history record with
`ARCHIVED_ONLY_HISTORY`. Existing pointers remain supported across later
rotations. Archives stay outside current-run discovery, recursive validation,
fixtures and automatic cleanup. No archive/preimage may be deleted without a
separately authorised retention successor preserving every typed object and
genealogy.

## Failures, compensation and new boundaries

| Observed result | Required owner action |
|---|---|
| Failure before transition admission | Preserve archive/preimage and undiscoverable candidate; old receipt remains subject to its ordinary currentness gate |
| CAS fails, pointer remains exact expected-old | Fresh recovery invalidation/epoch, verify prior payload, expected-old recovery CAS, fresh v3, first marker if needed, complete JOIN |
| CAS fails, pointer changed | Never restore the old projection over another writer. Require the exact winner's complete JOIN or STOP |
| CAS lands, readback/receipt/first marker fails | Only the proved recovery owner may create a fresh recovery transition and compensate from that exact failed pointer to a verified prior projection, then mint v3 and complete marker/JOIN |
| Any writer/pointer/invalidation/epoch/effect/receipt/marker uncertainty | STOP; no blind retry, old receipt reuse or root fallback |

The shared claim-run namespace gate protects each short admission/CAS. The
rotation lease must not prevent a genuine newer host/session boundary from
invalidating stale rotation work. A recovery cannot compensate over that newer
invalidation. Failed allocations remain in immutable history even if no receipt
was minted for them. A missing receipt is not manufactured to make epochs appear
contiguous.

Migrated native resume uses `prepare_native_resume_draft` and the same immutable
generations. `implementaudit.native-resume-transition.v1` preserves the actual
native boundary/invalidation and protected payload while advancing generation and
epoch. It creates no erroneous-invalidation correction grant. Separate STATE then
ROADMAP pre-resume reads bind both pointer and invalidation tokens and carry no
currentness authority; ordinary work requires the fresh v3/permanent-marker JOIN.

Only complete unchanged native F2 before epoch/publication allocation permits
read-only reuse; partial/finalized preparations refuse. Native preparation bypasses
only the rotation trigger/minimum reduction: source, output, time and memory
bounds remain. Its archive declares `preparation_kind: native-resume` and retains
the exact derived owner map. Shared claim-run integration remains separately owned.

## Trigger, cost and qualification limits

The retained calibration is `R0039-F1-CAL-v2`, population SHA-256
`b3df1ff07d18f8f5de145cf6d10f48a15f0a0416b392d0ca84567dce6d23e497`.
Its original thresholds are 131072 UTF-8 bytes, 32768 tokens or at most 2500
remaining-context basis points, bound to cl100k_base/tiktoken0.12.0 and
codex-desktop2026-08-20. Its minimum byte reduction is32768, token payoff8192,
maximum runtime5000ms and memory67108864bytes.

The executable portable admission currently uses the exact byte route; it does
not fabricate observations from another host or tokenizer. Below the byte
threshold it returns the ordinary cheap path without loading an owner map,
writing an archive/generation or calling a model. Triggered unsupported grammar
or insufficient measured payoff refuses; retained bytes are never discarded to
meet a budget. Token/context-health admission and original host calibration
remain separate qualification burdens. The owner-approved scoped issue exit
described below does not satisfy those original predicates. Storage is retained and deduplicated;
budget excess is an owner decision, never silent deletion.

Triggered work checks the process peak resident set against67108864bytes before
archive effects, after parsing and derivation, and before returning a prepared
candidate. The process-only observation includes interpreter/caller: Linux RSS
in KiB, macOS RSS in bytes, or Windows peak working-set bytes; other platforms
refuse. This is not whole-process-tree memory. A conservative twelvefold
source-population reserve refuses inputs before parsing when their encoded
population alone cannot fit that admission envelope. Admission and observed-peak checks provide no OS hard memory limit.
Measured times and RSS stay in qualification evidence, outside deterministic
generation bytes. If a later budget check fails, retained evidence remains
undiscoverable as current state and no currentness is authorised.

Source and output custody requires native directory-handle operations. The
helper holds non-following handles from the filesystem anchor through every
ancestor, accesses children relative to those handles, rechecks their identities,
and applies output permissions to the opened descriptor. Hosts without this
capability refuse. The Windows parent-handle implementation requires its own
native qualification. These checks prevent path redirection; they do not
authenticate against an equally privileged process that can modify held objects.

The canonical package remains version 0.4.0 / family v0.4.0.0, one governor and
four children. Owner-approved prospective budget revision 3 permits 458,752
compressed bytes per projection with a 2,000-byte reserve: at most 456,752 bytes
per artifact. Revisions 1 and 2 retain their 327,680 and 393,216-byte caps and
original failures as historical evidence. Both generated inventories and isolated plugin/standalone copy routes
must contain the exact bound helper pair. A source or portable fixture result
does not confer native Windows, host discovery, install, release or campaign
qualification. Source reviews and fresh-context canaries bind an immutable
candidate; they are separate from each zero-model rotation.

### Prospective Windows byte-only qualification

The October 22, 2026 owner amendment for issue #215 selects only the demonstrated
`EXACT_BYTES` path, protected-state equivalence at its measured scope, Windows
custody/crash/rollback controls, distribution parity and selected installed Codex
receiving. Token/context activation and accepting C02 publication remain
unavailable; unauthenticated or unqualified inputs fail closed. The retained
authentic-input, full amended occurrence-canary and entitled-correction predicates
remain unearned with their existing owners in one linked follow-up. No pending
or unknown obligation is consumed by this narrower issue exit.

For the pinned Windows qualification population only, the prospective complete
owner CLI ceiling is 60,000 ms and 201,326,592 peak aggregate committed bytes
(192 MiB), with no baseline subtraction. A private Windows Job Object contains
the suspended-before-assignment root and inherited descendants with no breakaway.
Time starts immediately before process creation and ends after root exit AND
an empty job; shell, Python, Git and in-job console/helper overhead are included.
Subsequent independent readback, storage scans, token counts and model receiving
are outside this interval. Missing or incomplete accounting refuses qualification.
This is a candidate qualification ceiling, not a new runtime timeout, universal
guarantee, or budget for other hosts. Existing helper limits, security checks and
test deadlines remain unchanged.

The source-owned repo record
`docs/research/implementaudit/r0039-windows-byte-qualification.json` binds the
exact runtime, fixture, owner map, pre/post pairs, recorder, controls and observed
host versions. It is qualification evidence, not an installed runtime dependency.
PL5 measured full rotation took 25,409.039 ms and 139,272,192 committed bytes;
migrated and unmigrated non-triggers took 5,293.447/3,794.531 ms and
106,127,360/138,952,704 committed bytes. Original 5,000 ms / 67,108,864-byte
full-operation failures and calibration remain unchanged. The measured pair
saved 188,537 live bytes and 23,662 separately counted tiktoken 0.13.0 tokens,
while retaining 242,750 additional archive/run/Git-object bytes. No deletion
is justified by this qualification. Exact-head review, composed CI, package
receiving, separate merge approval and certification remain distinct gates;
no original-DAG, whole-cell, campaign, native-currentness or full-release credit
follows from the scope amendment.

## Pending occurrences and retirement

Two proved compactions under identical H0/currentness labels remain distinct.
Each pending boundary retains physical/source identity, original evidence
locator, offset/hash/ordinal, observation prefix/cutoff, selected prior occurrence
and supported retry, reservation, actual RETURN, accepted JOIN or its absence,
uncovered successors and historical refusal. A copied or unselected identical
occurrence, changed physical identity or later good answer cannot repair an
original wrong response. Missing epoch/currentness proof leaves the bounded
R0033/continuity audit-state obligation mandatory and its result non-authoritative.
R0039 preserves those facts; it does not observe, route or consume the obligation.

TC06: disabling new rotations does not retire readers, permanent markers,
archives, in-flight effects or supported-consumer acceptance duties. TC11:
historical evidence remains valid at its original scope; changed semantics/grants
invalidate only affected current reuse. Neither retrieval nor recovery rewrites
historical conduct. Retirement requires no active transaction and a separately
proved supported successor before removing any migrated reader/retention duty.
