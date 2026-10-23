# Native continuity resume after canonical migration

This is the R0039 helper and pure-projection contract exercised by
`native_resume_v2_test.py`. Its constructed records and disposable Git subjects
provide source and filesystem evidence. They do not authenticate a host boundary,
grant currentness, execute `audit-state`, or supply an accepting native receipt.
The separate `claim-run.sh` integration owns those currentness operations.

## Source and owner boundary

`prepare_native_resume_draft(repo, run_root, controller, generation, predecessor)`
accepts the exact original predecessor descriptor from claim-run. It requires an
already migrated v3 predecessor, its actual pointer and receipt objects, and its
unchanged permanent migration ref. The helper verifies the immutable current
generation and the receipt's original fourteen-field wire binding before it
creates any archive or derived owner-map file.

There is no caller-supplied owner map or protected-payload update. The new map for
the complete current preimage is derived from the verified protected manifest:

| Owner row | Permitted rebinding |
| --- | --- |
| `PAIR` | Replace only `source_sha256` with the actual current STATE or ROADMAP hash; retain field, owner, source locator and protected value hash. |
| Current receipt artifact | Bind both byte/value hashes to the actual committed predecessor v3 receipt; retain its artifact identity, role and owner. |
| Other artifacts | Retain every row unchanged; altered live artifact bytes refuse parsing. |

These rows identify the newly captured current preimage. They do not rewrite the
older source-owner map retained in the predecessor generation and archive. The
native finalizer's complete protected payload and source-owner map must equal the
newly captured preimage exactly, through the existing deterministic equivalence
oracle.

## Preparation and archive

Native preparation uses the existing archive and draft writer. Its descriptor
schema is `implementaudit.native-resume-prepared.v1`; the existing rotation
descriptor remains `implementaudit.canonical-prepared.v2`.

Only native preparation bypasses the rotation byte trigger and minimum reduction
test. Its memory, source-size, output-size and runtime gates remain active. The
unchanged frozen calibration object binds these resource limits; the explicit
native preparation schema and archive kind identify the exception to rotation
admission. Ordinary below-threshold rotation still returns without an archive or
extra source-schema work.

The native derived owner-map bytes are written once at the actual contained path
`state-generations/<new-generation>/native-resume-owner-map.json`, with immutable
file mode. The archive retains those exact bytes. Only a native archive may name
that exact new-generation path for its `OWNER_MAP` entry. Normal rotation retains
its original source-path exclusions.

`implementaudit.state-archive.v1` admits one narrowly scoped optional member:
`preparation_kind: "native-resume"`. An unknown value, a legacy predecessor, a
different owner-map path, a mismatched mode, or a descriptor whose kind differs
from its anchored archive refuses. The manifest and every retained object use
the original archive namespaces and expected-zero publication operation.

The draft contains no successor transition, future receipt OID or future pointer
OID. Its exact no-transition manifest and all four files are reread before
finalization. Previous archived populations remain typed historical pointers.

## Completed preparation reuse before allocation

A newer native boundary can preempt claim-run after a complete archive/draft but
before allocation. Such a preparation contains no native event or future epoch
envelope. It may be reused by exact readback when the original pointer, receipt,
marker, source pair, referenced artifacts, derived owner map, archive and draft
are unchanged.

The reuse path writes no blob, ref, file or directory. It requires the generation
directory to contain exactly the derived map and draft directory, and the draft
directory to contain exactly its four immutable files. Partial, modified or
already finalized generations refuse. Claim-run separately requires the
successor epoch, publication and receipt refs to be absent before entering a new
native transaction. This is reuse of an unallocated F2 preparation; it does not
repair or replay an allocated epoch.

## Transition algebra and publication

The owner envelope has schema `implementaudit.native-resume-transition.v1` and
`transition_kind: "native-resume"`. Its `payload_source` is `preimage`; every
`failed_transition_*` member is explicitly null. The pure envelope retains the
same identifier in `schema_version` and its existing complete transition field
population.

The native boundary is exactly one of the original native vocabulary:
`host-reported-compaction`, `new-session`, `handoff-resume`, `manual-resume`, or
`inferred-context-gap`. The finalizer preserves the owner's actual native
invalidation object. It does not relabel that boundary as
`canonical-state-rotation` or create another invalidation.

The permitted transition requires the exact previous generation, epoch and
committed v3 receipt token, a fresh generation and epoch each incremented by one,
a different invalidation OID, and the exact expected successor v3 receipt ref.
Skipped or reused identities, substituted predecessors, recovery fields,
unreconciled state, legacy input, future pointer/receipt fields and protected
payload changes refuse.

The resulting pointer preserves the original
`implementaudit.current-generation.v1` field population. Claim-run remains the
sole expected-old pointer CAS, native epoch, original v3 receipt and currentness
JOIN owner. A completed migration marker is never rewritten. Helper readback
alone does not authorize ordinary work.

## Retention guards and qualification scope

`archive_retention_guards(repo, controller, archive_ref, expected_sha256)` reuses
the complete iterative archive verifier and returns exact ref-to-OID guards for
the root manifest, all ancestor manifests, and every retained object anchor
across that population. It rereads all guards before returning. Claim-run adds
those guards to its publication transaction, so deletion or substitution after
archive checking is fenced by the actual owner CAS.

The focused source fixture covers the five native boundaries, transition and
predecessor omission/mutation populations, source and pointer drift, alias
refusal, incomplete drafts, operation-kind substitution, exact read-only
preparation reuse, multi-generation genealogy, typed retrieval after GC, and
retention drift during handoff. The constructed producer retains its own
declared invalidation before GC; archive assertions and the runtime readback
requirements remain unchanged.

The entitled producer for guarded correction of an erroneous invalidation is
still a separate missing input. These helpers do not infer such entitlement,
mint a grant, change protected instructions, or substitute synthetic occurrence
records for the amendment's original evidence.
