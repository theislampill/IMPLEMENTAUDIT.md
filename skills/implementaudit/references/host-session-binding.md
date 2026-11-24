# Host-session binding (R003A)

R003A binds a `(host_id, host_session_id)` pair to an already governed object.
Lifecycle attribution requires a current binding and matching controller, claim,
run, repository, worktree and continuity identities. Their owners retain
currentness, receipts, route satisfaction, closure, mutation, READY/JOIN and
native activation authority.

## Custody and record

For `scripts/host-session-binding.py`, pass the explicit plugin- or host-owned
`--store` outside target authority. Cwd and target content supply no store.
Disabled, untrusted, malformed, aliased or mixed-version state is unavailable.
`init --owner-id <id>` first-creates the owner marker under the writer lock.
Only the exact owner can repeat initialization. A partial marker cannot be
replaced. After locking, check the owner and descriptor identity against the
live lock and store. Refuse a replaced lock before entering the critical section.

POSIX custody requires effective-user ownership and excludes group or other
writes at every store path member. Regular files require one link. Aliases,
symlinks and reparse points refuse. Repository and worktree paths follow their
canonical-directory contract without any added Git or store permission rule.
Parse one descriptor-bound JSON buffer, verifying pre/post identity and metadata.
Refuse duplicate members, malformed typed fields or custody drift.

Native host authentication is **unsupported by this portable core**. Caller
IDs, receipts, names and grants authenticate no native principal. POSIX
permissions and the cooperating lock give local custody against cooperating
writers. Same-user noncooperating actors and native provenance need separate
proof. Non-POSIX store operations refuse before creation. Read-only
absent-binding lookup stays available. Windows ACLs and durability need their
own proof. Portable attribution reports
`host_activation_proven: false` and `enforcement_available: false`.

The exact host/session pair is the key. The session index refuses a foreign
host without enumerating bindings. Each value records:

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

The store retains an `implementaudit.host-session-binding-attempt.v1` marker
at `activation-attempts/<session-sha256-prefix>/<session-sha256>.json`.
Its host-independent key refuses foreign use without a scan. The body binds
schema, owner, host and session.

Under lock, `bind` checks the host/session, enabled owner, canonical run,
repository, common directory and worktree, run containment and external store.
Then it creates the attempt marker before validating controller, claim,
activation and continuity. Retain earlier refusals. They create no marker.
The marker supplies no activation or receipt authority.

A validation refusal before either pair write records `outcome: REFUSED`.
Stop policy v3 may request the typed `ACTIVATION_FAILED` fallback only for this
exact refused marker with neither pair member present. Ordinary lookup still
returns `UNAVAILABLE`. An owner retry resets a refused marker before validation.
A complete pair resolves the attempt. Legacy pairs without a marker remain valid.
Partial, interrupted, foreign and malformed custody cannot supply fallback.
Failed rebind or CAS leaves a valid pair unchanged and requires the exact
expected generation for dependent use.

POSIX syncs first creates and replacements. Uncertain I/O preserves generations
and partial files, and grants no reset, replay or Windows durability claim.

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

Read-only `validate-event` verifies the current generation and all controller,
claim, run, repository, worktree and continuity identities. Stale, reordered,
foreign, ambiguous and tombstoned attribution refuse. Correlation hashes the
binding and admitted event, turn, tool-use, agent, obligation and transaction
IDs. The route IDs travel together and correlation leaves them unconsumed and
unsatisfied.

## Separate consumer integration requirements

Separate admission governs the unselected R0035 `consume-proximal-action`.
It selects the trusted installation and fixed `PLUGIN_DATA/host-session-binding-v1`.
Send current binding, event and deterministic compiler selection on canonical
UTF-8 stdin, at most 131072 bytes. Before custody, refuse argv, caller paths,
empty, malformed, duplicate-member or noncanonical input.

First-create one immutable receipt under lock per selection digest and
host/session, shared by copied, renamed and concurrent transports. Authority
is `NONE`. Same-event delivery is idempotent. Other-event replay and uncertain
completion stay consumed. Resolve route and disposition first. An otherwise-ALLOW
turn may consume the exact selection. Authoritative ALLOW requires successful
consumption. A refusal leaves the action for a later current event.

Accept one closed `implementaudit.host-abnormality-classification.v1` bound to
the Stop event. Classification excludes prose and parallel hook output. Without
a trusted producer, events stay `UNCLASSIFIED`. Absent, malformed, stale or
foreign records grant no authority. `NONE` and `MECHANICAL` keep the cheap path.
`SUBSTANTIVE` needs the exact selected `audit-andon`, `REQUIRED/SATISFIED` and one
governor reconciliation. Live dispatch refuses a governed child requester.

## Host-owned holon stage receipts

Under lock and an ACTIVE binding, `record-holon-stage` first-creates an immutable
`implementaudit.host-holon-stage-receipt.v1`. Its closed-body digest binds owner,
host, session, generation, child, packet, obligation, transaction, event and
stage. Refuse aliases, replacements and duplicates. The child returns ordered
LOAD, USE and DISPOSE identities. The consumer reads and verifies all three and
their current bindings before lifecycle credit. Missing, foreign or wrong-scope
records remain unverified. Another delivery cannot reuse the receipts.

Target prose, transcripts, child outputs, cwd, newest-run and controller
singleton heuristics supply no identity.

## Session end, GC and proof boundaries

`tombstone --reason session-end` ends attribution and reports
`object_closed: false`. Owner-bound `gc` requires the expected generation,
preserves the current one, and removes only named non-active generations
with closure-owner resolution receipts. Repeats are idempotent. Missing
resolution or a noncontiguous requested lineage refuses. Neither operation
changes controller, run root, continuity or audit evidence.

Binding returns `source_core=PRESENT`, `package=UNVERIFIED`, `install=UNVERIFIED`
and `host_activation=UNVERIFIED`. Installation, discovery and enforcement need
their own evidence. Rollback removes adapter and store records and preserves
controller, claim, run, continuity and evidence.

## Stop attribution and reserved adapters

For selected Stop attribution, this is a role R required procedural helper.
Invoke `python -I -S -B <skill-dir>/scripts/host-stop-interlock.py` with bounded
Stop JSON on stdin. Its boundary is unsupported host effects.
`PLUGIN_ROOT` selects the physical plugin cache, and `PLUGIN_DATA` must
match its owner pair or native scratch name. Neither authenticates a principal.
The standalone copy has no registered native route.

The default entry compiles the adjacent pinned binding core from one checked
buffer. Absence or a never-bound session returns `UNBOUND` without scans, writes,
subprocesses or validation. Foreign fields, aliases, drift and unsupported
custody refuse. Other selections return `UNAVAILABLE` with false activation,
enforcement and effect flags. Caller data grants no effects. The default entry
invokes no route, compiler, disposition or writer, and allows no proximal
consumption. TC11 refuses only dependent current use.

Selected Stop v3 pins eligible dispositions and records each verdict within one
owner budget. The lifecycle owner must validate exactly one. Request typed
first-activation lookup only from a pinned owner declaring the attempt schema.
Legacy lookup may receive an active exact binding. A proven failed first
activation preserves the unavailable verdict and normative validator fallback.

The isolated adapter/recorder/runtime chain and AM01–AM03 remain unadmitted.
Historical policy
`d2114a8dc618d7405901ebe625d1f08e0c7591d75739bb67c4ddef256940e23c`
retains its historical scope. Qualify prepare, preflight and runtime consumers
with both control polarities before adoption.

`codex-compact-interlock.py` and `codex-recovery-prompt-input.py` are donor
proposals. Native-runtime and route-graph keep separate manifests. Inclusion
requires consumer and package decisions for actual dispatch, standalone use,
exact executable sources and role checks. Copy or direct invocation gives no
route proof.

## Portable nonterminal-yield record predicate (R0037)

For an already selected governed run, the governor can check the durable
continuation record through the existing run-root owner:

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
