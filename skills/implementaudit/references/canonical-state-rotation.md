# Canonical-state rotation: F2 draft and archive contract (#215)

Canonical-state rotation replaces an oversized live STATE/ROADMAP projection
without changing its protected meaning. F2 draft/archive output is never
current. The bounded Task-4 publisher can commit an already-stored canonical
event lineage only through a no-input lease and an expected-old Git CAS; it
does not select live source evidence, alter R0011, mint receipts, or advance
currentness outside that one guarded current-generation pointer.

## Immutable event-lineage publication

The publisher accepts only canonical Git blobs: an exact v1 generation manifest,
an exact v1 generation pointer, and event blobs addressed at
`refs/implementaudit/state-event-segments/<run>/<generation>/<sequence>/<event-id>`.
Every manifest row is checked against its stored segment's canonical bytes,
typed digest, recomputed event identity, authority tuple, sequence, record kind
and source-evidence ID. This is stored-structure verification only: it never
calls the live owner resolver, which remains fail-closed with
`OE_SOURCE_CONTEXT_NOT_AVAILABLE` until its later owner.

Publication derives controller, claim, run root, receipt, invalidation,
migration-marker and current-generation guards from the one controller record.
It opens retained no-follow STATE, ROADMAP, and WORK_GRAPH handles, derives the
generation and exact STATE/ROADMAP receipt digests from those handles, and
verifies controller-worktree shared custody plus the exact v2 receipt binding.
The candidate STATE/ROADMAP digests must equal those receipt-bound observations;
WORK_GRAPH remains candidate-bound. A create-exclusive shared-writer lease and
all three handles are held before that derivation through post-CAS readback.
Candidate/predecessor objects are frozen and reread before two complete
canonical-path-sorted eight-field observation passes over those same handles.
After vector equality, the prebuilt sanitized `git update-ref --stdin -z`
transaction is the only publication operation; its
ordered verifies guard controller, receipt, invalidation and migration marker,
and its update guards the expected old current-generation OID. A failed CAS is
a typed expected-old loser only when bounded readback proves a distinct winner;
failed or contradictory readback is an unknown effect and forbids blind retry.

The host OS, filesystem semantics, fixed platform Git installation, and runtime
and cryptographic primitives are trusted substrate. The publisher selects Git
only from fixed platform paths, never caller `PATH`, `ProgramFiles`, authority,
or path overrides, but does not authenticate that substrate through SID, UID,
ACL, executable-handle identity, digest, provenance, or authenticity claims.
The physical-owner discovery shell also selects its own fixed platform Git and
receives only the exact six-key `PATH`/locale/config/prompt allowlist; inherited
`GIT_*`, `LD_*`, `DYLD_*`, `BASH_FUNC_*`, `BASH_ENV`, and platform-path override
state is absent.
Repository/global hooks and configuration are neutralized with the fixed
platform null/non-executable sink (`NUL` on Windows, `/dev/null` on POSIX); a
repository-local isolation object is never a fallback.

STATE, ROADMAP, and WORK_GRAPH remain governed mutable inputs rather than
trusted substrate. On native Windows they are opened with `CreateFileW`, all
read/write/delete shares, and `FILE_FLAG_OPEN_REPARSE_POINT`; directory or
reparse attributes are rejected. Exact bytes are read twice from the retained
first-pass handle, while pass two reopens the canonical path under the same
native flags. Both complete eight-field observation vectors are sorted by
`canonical_no_follow_path` and must agree exactly. Missing native semantics is
typed unsupported, never a success. POSIX likewise requires `O_NOFOLLOW` and
retained descriptor/reopen identity for those three mutable inputs.

## Authority and phase boundary

`skills/implementaudit/scripts/rotate-canonical-state.py` is the deterministic
projection-draft and archive-object writer. In F2 it may:

1. load a manifest-enumerated protected preimage from one run root;
2. classify each unique typed role and source path;
3. write and reread an undiscoverable draft under
   `state-generations/<generation>/draft/`;
4. write each captured preimage as a Git blob;
5. write a canonical archive manifest blob; and
6. create and reread only
   `refs/implementaudit/state-archives/<controller>/<generation>` with an
   expected-zero compare-and-swap.

The bounded code owners are `load_preimage`, `classify_protected_state`,
`build_projection_draft`, `archive_preimage`, and `verify_archive`. Finalization
and equivalence/publication functions are deliberately absent in F2.

For immutable history-event identity, `canonical_json_v1` is a distinct
cross-owner byte contract: UTF-8, recursively sorted keys, compact separators,
no terminal LF, signed-64-bit integers only, and no floats. Event requests have
an exact v1 vocabulary; callers cannot supply a source locator or digest.
`normalize_source_locator_v1` normalizes only typed path components (NFC plus
canonical percent encoding), retains POSIX backslashes as data, and accepts the
source identity only from its owner-manifest entry.
The public source-context facade is intentionally unavailable until its later
owner: every syntactically valid source-evidence ID returns
`OE_SOURCE_CONTEXT_NOT_AVAILABLE` without repository or currentness discovery.

It has no function or command that writes a current-generation, migration,
invalidation, epoch, receipt, or marker ref. F2 does not update root STATE or
ROADMAP, does not publish a pointer, and does not create a transition envelope.
An archive is retention evidence, never currentness authority.

## Preimage and path custody

The manifest schema is
`implementaudit.canonical-state-rotation-f2-fixture.v1`. It binds controller,
projection generation, exact archive ref, the ordered `protected_files`
population, recursive-population exclusions, transition-field exclusions, and
expected behavior. Every protected-file row has exactly one `role` and one
run-root-relative POSIX `path`.

The helper rejects absolute paths, drive-qualified paths, backslashes, empty or
dot components, traversal, duplicate roles/paths, and any excluded archive,
generation, or quarantine component. Repository, run-root, manifest, source,
draft, and payload custody is checked without following symbolic links or
Windows reparse points. Protected files must be single-link regular files with
owner read/write permission. Open-file identity and the post-read device,
inode, size, and modification time must remain stable.

Draft payload files preserve the source mode and reread it exactly. On Windows,
where Python exposes only writable/read-only mode classes, exactness means the
corresponding `0666` or `0444` class. The canonical manifest itself remains an
owner-writable regular file.

## Projection-draft schema

`build_projection_draft` writes canonical UTF-8, sorted-key, no-insignificant-
whitespace JSON with schema
`implementaudit.canonical-state-projection-draft.v1`. Its fields are exactly:

- `schema`, `controller`, `generation`, and the future `archive_ref`;
- ordered `entries`, each binding `role`, `source_path`, undiscoverable
  `draft_path`, SHA-256, byte length, source permission mode, and predicted Git
  blob OID;
- `discovery: EXCLUDED`; and
- `recursive_population: EXCLUDED`.

The predicted OID uses `git hash-object --stdin` without `-w`; draft creation
does not write an object or ref. The manifest may not contain
`current_generation`, `epoch`, `invalidation_oid`, `migration_marker`,
`pointer_oid`, `predecessor_receipt`, or `receipt_oid`. Absolute roots,
timestamps, process IDs, and random values are also absent, so identical clean
roots produce byte-identical drafts.

Draft writes are create-only. Existing draft custody is a STOP, never an
overwrite. If a write or exact readback fails after draft creation, only that
task-created undiscoverable draft moves to the fixed sibling
`quarantine-draft`; no preimage or archive is deleted.

## Archive schema and retrieval

`archive_preimage` rereads the complete canonical draft before writing Git
objects. Every payload's recomputed SHA-256, byte length, permission mode, and
predicted blob OID must match. It then writes each blob and a canonical manifest
with schema `implementaudit.canonical-state-archive.v1`. The archive manifest
binds the exact draft-manifest SHA-256, the unchanged ordered entries, and the
discovery/recursive-population exclusions.

The archive ref update is exactly:

```text
git update-ref <archive-ref> <manifest-blob-oid> 0000000000000000000000000000000000000000
```

An existing ref is an expected-zero CAS failure. After a successful update,
`verify_archive` rereads the exact ref and requires the manifest and every
entry to be Git blobs. It recomputes canonical manifest bytes, entry SHA-256,
byte length, and Git OID. Attempt success is not archive success; all typed
readbacks must agree.

Archive objects and their anchored manifest are never inputs to a later draft
or recursive archive population. They are outside live discovery and cannot
resolve as a current projection. Storage-budget excess remains an owner
decision; F2 provides no archive deletion path.

## History population and bounded hot projection

Task 5 adds a non-destructive migration classifier over explicit immutable,
fully materialized `STATE.md` and `ROADMAP.md` migration preimages. Each input
binds its exact compressed fixture bytes, decoded byte count, SHA-256, and a
deterministic two-source population digest. The older frozen template blobs are
derivation inputs, not the claimed complete legacy population: the migration
gate reads them from the exact immutable base commit, verifies their digests,
reproduces the declared materialization operation byte for byte, and only then
directly classifies the materialized fixture bytes. Its classification fixture declares every ordered
top-level section and every literal row/record partition in a mixed section.
The classifier does not guess from a heading allowlist, status vocabulary, or
paragraph heuristic. It parses the declared Markdown table boundary, requires
the complete row population in fixture order, and emits contiguous byte ranges
from byte zero through end of file. An unknown/missing/reordered section,
unmatched row, duplicate literal rule, overlap, gap, empty range, changed source
slice, or invalid derivation pointer is STOP.

Every classified byte range has exactly one class:

- `HOT_CURRENT`: still-open state or currently applicable instruction;
- `HOT_POINTER`: current source, graph, generation, archive, or query custody;
- `COLD_HISTORY`: a closed/resolved/prior/satisfied/completed record;
- `ON_DEMAND_EVIDENCE`: completed detail that is needed only for a bounded
  history inspection; or
- `DUPLICATE_DERIVABLE`: a deterministic projection with a closed typed
  pointer that binds the R0039 owner, exact Git source identity and digest,
  closed derivation operation/selector, and derived-byte digest. Resolution
  reproduces those bytes and requires equality with the classified range.
  Only `template.identity` ranges are admitted, so this class cannot conceal a
  history row. Arbitrary, unresolved, wrong-owner, wrong-digest,
  byte-divergent, and hidden-history pointers fail.

`enumerate_legacy_history_v1` returns every `COLD_HISTORY` and
`ON_DEMAND_EVIDENCE` range in source and byte order. `LegacyRecord` identity
binds source name, heading, kind, ordinal, exact byte range, and SHA-256 of the
unchanged source bytes. `verify_migration_equivalence_v1` rejects duplicate
source or destination identity and requires exact set equality between every
removed `(legacy_record_id, legacy_source_digest)` pair and canonical event
envelopes admitted by `EVENT_OUTPUT_KEYS`. It validates canonical raw segment
bytes, event and payload identities, exact manifest population, and Task-4
manifest/segment semantics, then performs exact stored lookup through each
`refs/implementaudit/state-event-segments/...` identity. There is no parallel
event type and no caller-supplied queryable flag. Missing, extra, duplicated,
malformed, unstored, or unmanifested destination events fail; attempt success
or aggregate counts alone are not equivalence. The population
digest is SHA-256 over canonical JSON for the lexicographically sorted complete
pair population.

`derive_hot_state_v1` and `derive_hot_roadmap_v1` accept only typed native
current fields, the exact `WORK_GRAPH.json` digest/projection, and typed
generation/archive/query custody. The single `NativeCurrent` schema includes
current audit-object identity, runtime artifacts, open Ledger findings and
Andons, consequential residuals, execution identity, decisions, continuity and
instruction rows, action selection, baseline/run-root identity, planning
pointers, active phases, and open scope-creep rows. Their deterministic UTF-8
renderings are bounded to 4096 bytes each. A mechanical section-parity check
requires the renderer and canonical template heading sequences to equal the
closed STATE/ROADMAP section contracts; held-out omission controls cover every
required section. Closed history is absent from hot Markdown but remains
reachable through the immutable event population and exact archive. The
canonical templates are the same hot shape, not a second history ledger.

Task 5 reads existing preimages, archive custody, event identities, and the
current WORK_GRAPH digest. It does not delete or rewrite a preimage/archive,
publish a current-generation pointer, create a migration marker or receipt,
mutate continuity refs, change WORK_GRAPH lifecycle, invoke ActiveGraph, or
perform Task-6 currentness behavior. R0011 retains receipt/currentness authority,
R0033 retains route authority, R0035 retains WORK_GRAPH lifecycle authority, and
the generic migration core has no ActiveGraph import or dependency.

## Failure and later-cell boundary

Unsafe path, symlink/reparse custody, permission drift, source race, malformed
schema, incomplete population, object mismatch, archive CAS collision, or
readback mismatch is STOP. Before pointer publication the old root/v2 route
remains current. Task-created drafts may be quarantined, but protected
preimages and anchored archives are retained.

F2 is GREEN only when two clean roots yield byte-identical draft and archive
identities; typed OID/SHA retrieval, discovery and recursion exclusions,
expected-zero anchoring, and path/link/permission controls all pass. The full
rotation stays RED until F3--F7 supply the ordered reader, transition,
finalization, pointer, receipt-v3, and permanent-marker joins.
