# Route-decision and obligation authority (R0033 H2A)

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
not caller booleans.
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
<oid>` rechecks every owner, executes only the exact mechanically vetted action
under the transaction, rechecks currentness again, then records a canonical
`PENDING/action-completion` successor. It returns `ACTION_COMPLETE`, never an
ephemeral allow that contradicts canonical PENDING. The completed fingerprint
cannot be re-minted, so omission or replay cannot retain authority. This cheap
action execution/completion is not H2B child completion. The receipt also
expires on any next-action, scope, read-set, binding, continuity,
package, child-source, owner, authority, dependency, effect, contradiction,
invalidation or scope-expansion change. Re-run `check` immediately before
`consume`. Independent work outside the bound controller/scope is not
blocked by another controller's obligation.

`REQUIRED` creates a controller-scoped obligation with route state
`UNSATISFIED`. H2A does not open a child, admit child bytes or packet identity,
accept a child return, reread post-return currentness, or complete the
obligation. Those transitions belong to H2B. An H2A active obligation therefore
cannot be downgraded or replaced.

## Projection and proof boundary

STATE carries only `Route decision projection` and `Route decision record`.
Those rows may report the canonical record, but are never authority; a direct
edit has no effect and disagreement is an invalid projection. The H2A source
core does not prove package inclusion, installation, native host activation,
child loading, route completion, lifecycle closure, READY, JOIN, or
`AUDIT_COMPLETE`.

Rollback removes the helper, reference, wrapper route and template projection.
Preserve any immutable `REQUIRED/UNSATISFIED` blob or receipt as unsatisfied
evidence; do not rewrite it into `NOT_REQUIRED` or completion.
