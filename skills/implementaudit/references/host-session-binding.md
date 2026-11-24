# Host-session binding (R003A)

R003A binds a host/session pair to a governed object. Controller, claim, run,
repository, worktree and continuity must match. Their owners retain currentness,
receipt, route, closure, mutation, READY/JOIN and native activation authority.

## Custody and record

Use an explicit plugin- or host-owned `--store` outside target authority.
Cwd and target content cannot select it. Reject untrusted, disabled, malformed,
aliased or mixed-version state. `init --owner-id <id>` first-creates the marker
under the writer lock. Only that owner may repeat initialization. Never replace
a partial marker. Recheck live lock, store and owner after acquiring the lock.

POSIX requires effective-user ownership and no group/other writes on store
members. Windows NTFS supports init, first bind and lookup under held paths,
current-user ownership and a protected owner-only DACL. Other Windows commands
refuse. Store files must be regular with one link. Refuse symlinks, reparse
points and aliases. Run/repo/worktree directories follow their canonical path
contract. Compare descriptor identity and metadata before and after reading
one JSON buffer. Reject duplicate fields, malformed data and drift.

The cooperating lock provides local custody. Same-user noncooperating actors
and native authentication need separate proof. Caller IDs and receipts grant no
authority. Portable attribution reports `host_activation_proven: false` and
`enforcement_available: false`.

The exact host/session pair is the key. The index rejects foreign hosts
without scanning. Each value records:

```text
schema
host_id
host_session_id
controller_id
claim_id
explicit_run_root
repository_identity
git_common_directory_identity
worktree_identity
binding_generation
activation_event_id
activation_receipt
applicable_continuity_generation
applicable_continuity_receipt
status
predecessor_generation
supersession_or_tombstone_reason
```

`bind` starts at `G0001`. Under lock, `rebind` and `tombstone` check the expected
generation and atomically advance one. `ACTIVE`, `SUPERSEDED` and `TOMBSTONED`
describe attribution.

Activation and continuity receipts are opaque, non-secret owner identifiers.
Before `bind` or `rebind`, callers validate the controller and continuity with
their owners. The core only records and compares the receipts.

### Failed first activation

The `implementaudit.host-session-binding-attempt.v1` marker at
`activation-attempts/<session-sha256-prefix>/<session-sha256>.json` binds
schema, owner, host and session. The host-independent key refuses foreign
use without scanning. Under lock, `bind` verifies host/session, owner, canonical
run/repo/common/worktree, containment and external store. It writes the marker
before validating controller, claim and both receipts. Earlier refusals write
no marker. The marker grants no authority.

A validation refusal before either pair write records `outcome: REFUSED`.
Stop v3 can use `ACTIVATION_FAILED` only with that exact marker and an absent
pair. Ordinary lookup returns `UNAVAILABLE`. Owner retry resets REFUSED before
validation. A complete pair resolves the attempt, with legacy pairs valid.
Partial, interrupted, foreign or malformed custody refuses fallback. Failed
rebind/CAS preserves the valid pair. Creates and replacements flush. Uncertain
I/O preserves generations and partial files without reset or replay.

## Read path and event correlation

`lookup --host-id <host> --host-session-id <session>` is read-only. Absence of the
exact binding, index and attempt marker returns `UNBOUND` immediately. It skips
store creation, repository scans, run enumeration, singleton selection and
validation. Uninspectable custody or uncertain I/O returns `UNAVAILABLE`.

For selected host-session attribution, binding lookup is a **role R required
procedural** helper. Once the governor selects this attribution boundary, it
must invoke the typed operation with the explicit owned store and exact host
and session:

```text
python -B <skill-dir>/scripts/host-session-binding.py --store <store> lookup --host-id <host> --host-session-id <session>
```

This selected binding-lookup procedure has the boundary **no host activation**.
Its result is local source attribution evidence and supplies no native event
registration, principal authentication or mutation authority.

`validate-event` verifies current generation and binding identities. Refuse
stale, reordered, foreign, ambiguous and tombstoned attribution. Hash the
binding and admitted event, turn, tool-use, agent, obligation and transaction
IDs together. Correlation consumes and satisfies nothing.

## Separate consumer integration requirements

R0035 `consume-proximal-action` requires separate admission and trusted fixed
`PLUGIN_DATA/host-session-binding-v1`. Send current binding, event and
deterministic compiler selection as canonical UTF-8 stdin (131072 bytes max).
Refuse argv, caller paths, empty, malformed, duplicate or noncanonical inputs
before custody. First-create one immutable receipt per selection digest and
host/session under lock, including copied, renamed or concurrent transports.
Authority `NONE`. Same-event delivery is idempotent. Other-event replay and
uncertain completion stay consumed. Resolve route and disposition first.
Only an otherwise-ALLOW turn may consume. Authoritative ALLOW requires
successful consumption. Refusal leaves the action for a later current event.

Use one closed `implementaudit.host-abnormality-classification.v1` from a
trusted producer, bound to the Stop event. Exclude prose and parallel hooks.
Otherwise `UNCLASSIFIED`. Malformed, stale or foreign records grant no
authority. `NONE` and `MECHANICAL` stay cheap. `SUBSTANTIVE` requires the exact
`audit-andon`, `REQUIRED/SATISFIED` and one governor reconciliation. Live
dispatch refuses a governed child requester.

## Host-owned holon stage receipts

Under lock and ACTIVE binding, `record-holon-stage` first-creates immutable
`implementaudit.host-holon-stage-receipt.v1`, binding owner, host, session,
generation, child, packet, obligation, transaction, event and stage. Reject
aliases, replacement and duplicates. Child returns LOAD, USE, DISPOSE in order.
Consumer checks all three current bindings before lifecycle credit. Refuse
absent, foreign, wrong-scope and reused receipts. Prose, transcripts, child
outputs, cwd and run/controller selection heuristics supply no identity.

## Session end, GC and proof boundaries

`tombstone --reason session-end` ends attribution (`object_closed: false`).
Owner-bound `gc` checks generation and removes only named non-active
generations with closure-owner receipts. It is idempotent and preserves the
current generation. Missing resolution or lineage gaps refuse. Both preserve
controller, claim, run root, continuity and audit evidence.

Binding reports `source_core=PRESENT` and `package`, `install` and
`host_activation` as `UNVERIFIED`. Those layers need their own evidence.
Rollback removes adapter and store records, preserving governed evidence.

## Stop attribution and reserved adapters

For selected Stop attribution, this is a role R required procedural helper.
Invoke `python -I -S -B <skill-dir>/scripts/host-stop-interlock.py` with bounded
Stop JSON on stdin. Its boundary is unsupported host effects.
`PLUGIN_ROOT` selects the physical plugin cache, and `PLUGIN_DATA` must
match its owner pair or native scratch name. Neither authenticates a principal.
The standalone copy has no registered native route.

Compile one checked buffer of the pinned adjacent core. Absent binding returns
`UNBOUND` without scans, writes, subprocesses or validation. Foreign fields,
alias, drift and unsupported custody refuse. Other selections return
`UNAVAILABLE` with false activation, enforcement and effect flags. Default
entry never calls route, compiler, disposition, writer or proximal consumers.
TC11 refuses only dependent current use.

Selected Stop v3 pins eligible records and uses one shared owner budget.
Exactly one record must validate. Request typed first-activation lookup only
from a pinned attempt-schema owner. Legacy lookup can bind an active pair.
A proven failed first activation preserves unavailable and normative fallback.

The isolated adapter/recorder/runtime chain and AM01–AM03 remain unadmitted.
Policy `d2114a8dc618d7405901ebe625d1f08e0c7591d75739bb67c4ddef256940e23c` is historical.
Qualify preparation, preflight and runtime at both control polarities.

`codex-compact-interlock.py` and `codex-recovery-prompt-input.py` are donors.
Native-runtime and route-graph have separate manifests. Actual dispatch and
standalone use require consumer/package decisions, exact sources and roles.
Copying or direct invocation supplies no route evidence.

## Portable nonterminal-yield record predicate (R0037)

For a selected governed run, the governor checks durable continuation with the run-root owner:

```text
bash <skill-dir>/scripts/validate-run-root.sh --nonterminal-yield <run-root>
```

One read-set identity binds selected STATE, ROADMAP and numbered phase. Full
structural validation rechecks it after use, including legacy selection. Full, micro and ledger
modes stay available. PASS proves portable yield. The governor verifies
controller, claim and currentness before use. Host authentication, Stop,
effects, handoff and closure retain their owners.

Yield uses STATE's Current phase table with open `Audit object state` and
nonterminal Status. Record Phase, Last check, Owner/source, Authorization state,
concrete Next action and Re-entry condition. Resolve a numbered phase to its
spec. State why untouched intake has yet to run. Duplicate fields, terminal or
handoff markers, missing phase identity, unsafe records, blank or template
actions refuse. Concrete continuation is independent of wording. The governor
owns semantic truth.

Only the applicable state needs further facts in that same table:

| Status | Durable continuation facts |
|---|---|
| `IN_PHASE` | Current checkpoint and Last completed step |
| `PAUSED` | Pause reason, Resume point and Pause trigger (`clarification`, `owner-authority`, `external-wait` or `user-interruption`) |
| `BLOCKED` | Blocker, Containment and concrete Next probe |
| `INTERRUPTED` | Stop source, Interruption point and Interruption log naming its exact existing Andon row |
| `open` / `READY_TO_DISPATCH` | Pending decision and exact Next action |

User interruption requires `Pause phase context`. `IN_PROGRESS` requires a
numbered phase and IMPLEMENTAUDIT_PAUSE with matching Phase, pause Status, Last
completed step and `STATE.md: updated`. `OUTSIDE_PHASE` permits intake or
pre-dispatch pause and refuses a fabricated marker. START/DONE spec anchors are
templates. The recorded context carries no native event authentication.
An owner stop binds the exact source and interruption point in its Andon row
for the same numbered phase. A same-phase pause agrees with Last completed
step. External wait also records Blocker, Containment and concrete Next probe.
These checks apply to selected yield only. The existing owners retain evidence
and authority. A wait remains a wait until an authorized handoff.

TY-1 through TY-5 allow the corresponding truthful continuation record; TY-6
refuses bare abandonment. Any terminal or handoff claim routes to its original
audit predicate and cannot escape through yield. A forced host turn ending is
neither closure nor handoff. Ordinary unbound sessions retain the immediate
native cheap path and do not invoke this validator.
