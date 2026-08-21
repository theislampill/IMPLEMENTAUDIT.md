# Route-decision and obligation authority (R0033 H2A/H2B)

After a live boundary and current continuity receipt, substantive advancement
still requires one canonical route decision. The durable values are exactly
`PENDING`, `NOT_REQUIRED`, or `REQUIRED`. Absence, malformed state, stale
currentness, or incomplete evidence is `PENDING` and blocks advancement.
Governor reasoning, route prose, a transcript marker, child output, or a STATE
edit cannot mint or satisfy the decision.

## Classification

`scripts/route-transaction.py` owns the versioned positive predicate:

- `MECHANICALLY_REQUIRED` produces `REQUIRED` for a known route trigger.
- `JUDGEMENT_REQUIRED` always produces `REQUIRED`; judgement cannot mint the
  cheap path.
- `MECHANICALLY_NOT_REQUIRED` is possible only for a closed non-trigger class:
  `MECHANICAL_CURRENTNESS_ACTION`, `PURE_BOUNDED_READ_OR_VALIDATION`,
  `EXACT_PACKAGE_OR_TOPOLOGY_VERIFICATION`, `SAFE_STATUS_OR_CONTAINMENT`, or
  `EXACT_ALREADY_BOUND_DETERMINISTIC_ACTION`.

The request is an action proposal, never its own evidence. It cannot supply
`CURRENT` assertions. The helper rehashes each repository-relative input,
derives the action class from a closed exact-argv/executable recognizer, binds
boundary and scope to the live continuity invalidation and Next action, reads
the current controller record and continuity receipt, validates the exact H0
event, and hashes the live HEAD/tree, executing route sources and exact child
source. Required triggers and judgement are derived from the admitted action,
not caller booleans. System executables must resolve through root/host-owned
custody and are digest-bound. Currentness argv must be a complete feasible
helper form. Pure read and safe-status classes use internal digest snapshots;
Git diff/status are not cheap-path executables, so repository filter helpers
cannot enter between the decision and action. Action environments strip shell
startup, exported-function, dynamic-loader and Git execution controls, and use
a trusted minimal `PATH`. Every trusted Git read-set command disables fsmonitor
and hooks before evidence is gathered.
Missing, mismatched, aliased or fabricated evidence stays `PENDING` or maps to
`REQUIRED`; caller-selected class labels cannot mint the cheap path.

The mechanically-not-required predicate also requires the exact current H0
host/session binding; current controller, claim, run, continuity generation and
receipt; exact boundary, scope, action and action class; current owner,
authority, effect and dependency evidence; a complete, uniquely ordered input
identity/digest set; current package and child-source identities; no missing,
stale or contradictory input; and no active same-controller obligation.

## Machine record and CAS

The canonical record is an immutable Git blob selected by
`refs/implementaudit/route-decisions/<controller>`. Every decision write is an
expected-old `git update-ref` CAS under a lock in the shared Git-common
namespace, followed by current ref/controller/binding rechecks. The record binds
the predicate version, H0 binding generation,
controller/claim/run/continuity, boundary, scope, exact action/class,
owner/authority/effect/dependency evidence, canonical inputs and digests,
package and child-source identities, predecessor, classification, outcome,
expiry fingerprint and current record identity.

`NOT_REQUIRED` is a scoped one-shot receipt, not a global exemption. `decide`
and `check` never authorize execution directly. `consume --expected-record
<oid>` rechecks every owner and first consumes the receipt by CAS to canonical
`PENDING/action-in-progress`. Only then does it execute the exact mechanically
vetted action. Normal success rechecks currentness and records a second
canonical `PENDING/action-completion` successor. Process loss at any point after
the first CAS leaves unknown completion fail-closed and cannot automatically
re-admit or replay the action. Normal completion returns `ACTION_COMPLETE`,
never an ephemeral allow that contradicts canonical PENDING. This cheap action
execution/completion is not H2B child completion. The receipt also
expires on any next-action, scope, read-set, binding, continuity,
package, child-source, owner, authority, dependency, effect, contradiction,
invalidation or scope-expansion change. Re-run `check` immediately before
`consume`. Independent work outside the bound controller/scope is not
blocked by another controller's obligation.

`REQUIRED` creates a controller-scoped obligation with route state
`UNSATISFIED`. H2A `decide` does not open a child, admit child bytes or packet
identity, accept a child return, reread post-return currentness, or complete the
obligation. Those transitions belong to the H2B commands below. An active
obligation cannot be downgraded or replaced.

## Bounded history routing

Routine route recovery consumes only verified current hot authority and reports
`history_read_performed: false`; it does not enumerate or hydrate immutable
event segments. When the exact action is `route-trigger
QUERY_HISTORY_THEN_RESUME iaevt-v1-<64-lowercase-hex>`, `decide` emits and records one
`implementaudit.history-query-request.v1` object with route
`QUERY_HISTORY_THEN_RESUME`, requirement `REQUIRED`, and a one-element ordered
`evidence_ids` list. The route remains `REQUIRED/JUDGEMENT_REQUIRED`. This is a
request for the later R0038 owner, not execution or satisfaction of that query.

An optional `--mirror-claim` is observation only. `check` reports
`IGNORED_CORROBORATION`, `IGNORED_CONTRADICTION`, or `IGNORED_ABSENT` against
the canonical decision/route state. A mirror or ActiveGraph claim never writes
the route ref, changes its result, or grants advancement.

## H2B child lifecycle and replay

`open --expected-record <oid> --packet <path>` accepts only the exact current
`REQUIRED/UNSATISFIED` record. It validates the immutable packet and stores the
full audit-state child and packet bytes, byte counts, digests, and identities in
the canonical `OPEN` successor. The packet's source-event identity is bound to
the exact current host/session attribution and route obligation/transaction;
a caller-supplied label is not provenance. `return --expected-record <oid> --return
<path>` accepts only a return bound to that obligation, route transaction, and
packet digest, then stores its exact bytes as the canonical `RETURNED`
successor. Neither state advances.

`complete --expected-record <oid> --packet <path> --return <path> --decision
<path>` rereads controller, continuity, host binding, predicate, child, packet,
and the same live return before recording a canonical `SATISFIED` successor. A
decision must bind the exact return digest. Every lifecycle read revalidates the
embedded child, packet, return, and decision bytes against the exact current
audit-state child and the original `REQUIRED/UNSATISFIED` authority. The
lifecycle admits exactly one governor decision; replaying that identical
completion is idempotent and emits no second record. Only a current
`REQUIRED/SATISFIED` check grants advancement.

`replay --expected-record <oid> --event <path>` compares immutable source-event
identity plus canonical body, kind, reactivation flags, and host-correlation
provenance, not message text alone. Reconstructed `E1` for a satisfied one-shot
is a zero-effect `REPLAY_NO_OP`. A host-bound distinct `E2` remains distinct
even if its body is identical, while an already-terminal target is a zero-effect
`TERMINAL_NO_OP` unless its event explicitly carries reopen, target-change, or
invalidating evidence. Missing, unreadable, malformed, unbound, ambiguous, or
identity-conflicting provenance returns one typed `ambiguous` STOP with no
issuance, transition, authorization, dispatch, or effect. An outstanding
standing constraint with the same source identity remains `STANDING_APPLIES`;
it is not converted into a new instruction row.

## Projection and proof boundary

STATE carries only `Route decision projection` and `Route decision record`.
Those rows may report the canonical record, but are never authority; a direct
edit has no effect and disagreement is an invalid projection. The source core
does not prove package inclusion, installation, native host activation, READY,
JOIN, lifecycle closure beyond its exact route obligation, or
`AUDIT_COMPLETE`.

Rollback removes the helper, reference, wrapper route and template projection.
Preserve any immutable `REQUIRED/UNSATISFIED` blob or receipt as unsatisfied
evidence; do not rewrite it into `NOT_REQUIRED` or completion.
