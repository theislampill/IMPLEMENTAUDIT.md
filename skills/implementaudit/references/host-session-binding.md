# Host-session binding (R003A)

R003A binds a `(host_id, host_session_id)` pair to an already governed object.
Lifecycle attribution requires a current binding and matching controller, claim,
run, repository, worktree and continuity identities. Their owners retain
currentness, receipts, route satisfaction, closure, mutation, READY/JOIN and
native activation authority.

## Custody and record

`scripts/host-session-binding.py` requires an explicit `--store`. The store is
plugin-owned or equivalently host-owned outside target-repository authority; do
not derive it from cwd or target content. `init --owner-id <id>` creates its
owner marker. Disabled, untrusted, malformed, aliased or mixed-version state is
unavailable and cannot support an enforcement claim.

`init` first-creates one owner marker under the existing store writer lock. An
exact owner may repeat initialization; a different owner or a partial marker
cannot replace it. Writers recheck the owner after acquiring the lock and
verify that the acquired lock descriptor still names the live lock file and
store. A waiting writer whose lock was replaced refuses before entering its
critical section.

POSIX custody requires effective-user ownership and excludes group or other
writes at every store path member. Regular files require one link. Aliases,
symlinks and reparse points refuse. Repository and worktree paths follow their
canonical-directory contract without any added Git or store permission rule.
Parse one descriptor-bound JSON buffer, verifying pre/post identity and metadata.
Refuse duplicate members, malformed typed fields or custody drift.

Native host authentication is **unsupported by this portable core**. Caller
owner IDs, receipts, principal names and grants establish no native principal.
POSIX ownership, permissions and the cooperating writer lock establish local
custody only. Same-user noncooperating actors and native provenance are outside
that proof. Windows and other non-POSIX store operations refuse before creation.
Read-only absent-binding lookup stays available. Windows ACLs and durability
require their own evidence. Portable attribution reports
`host_activation_proven: false` and `enforcement_available: false`.

The key is the exact host ID plus exact host-session ID. A direct session index
also prevents one session ID from being rebound under an incompatible host
identity without enumerating bindings. Each value records:

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

`bind` starts at `G0001`. `rebind` and `tombstone` require the exact expected
current generation, run under the store writer lock, and advance exactly one
generation. Records are replaced atomically. `ACTIVE`, `SUPERSEDED` and
`TOMBSTONED` are attribution states only.

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

The default entry returns `UNBOUND` for an absent store or never-bound session
without scanning, creating state, starting subprocesses or validating records.
It compiles the adjacent pinned binding core from one checked buffer.
Foreign fields, aliases, drift and unsupported custody refuse. Other selections
block as `UNAVAILABLE` with false activation, enforcement and effect flags.
Caller IDs, claims, receipts, flags, output and digests cannot grant effects.
The default entry calls no route, compiler, disposition or writer and grants
no proximal consumption. TC11 refuses only dependent current use.

Selected Stop policy v3 pins eligible dispositions, shares one owner execution
budget and retains the verdict for each attempted kind. The lifecycle owner
must validate exactly one. The selected hook acknowledges a proven failed
first activation as unavailable and retains the normative validator fallback.

The isolated adapter/recorder/runtime chain and its AM01–AM03 requirements
remain unadmitted. The historical policy
`d2114a8dc618d7405901ebe625d1f08e0c7591d75739bb67c4ddef256940e23c`
does not substitute for the absent one. Before adoption qualify actual
prepare, preflight and runtime consumers, including both control polarities.

`codex-compact-interlock.py` and `codex-recovery-prompt-input.py` remain
donor proposals. Existing native-runtime/route-graph peers keep their own
source manifests. Further inclusion requires consumer and package decisions
binding actual dispatch, standalone applicability and exact executable
sources, then role checks. A copied or directly invoked file proves no route.

## Portable nonterminal-yield record predicate (R0037)

For an already selected governed run, the governor can check the durable
continuation record through the existing run-root owner:

```text
bash <skill-dir>/scripts/validate-run-root.sh --nonterminal-yield <run-root>
```

This mode runs the full structural validator and rechecks its selected
canonical STATE/ROADMAP after consumption. The same read-set identity binds
STATE, ROADMAP and the numbered phase, including legacy selection. The
original full, micro and ledger modes remain available. A pass proves the
portable yield predicate. Host authentication, currentness, Stop, effects,
handoff and closure remain with their owners. The governor verifies exact
controller, claim and currentness before using the result.

STATE's Current phase table owns a yield. Keep `Audit object state` open and
the status nonterminal. Record Phase, Last check, Owner/source, Authorization
state, concrete Next action and Re-entry condition. Resolve a numbered phase
to its spec. For intake that has not run, record the actual reason. The mode
refuses duplicate fields, terminal or handoff markers, missing phase identity,
unsafe records and blank or template actions. Tests require concrete continuation
rather than any fixed list of English verbs. The governor owns semantic truth.

Only the applicable state needs further facts in that same table:

| Status | Durable continuation facts |
|---|---|
| `IN_PHASE` | Current checkpoint and Last completed step |
| `PAUSED` | Pause reason, Resume point and Pause trigger (`clarification`, `owner-authority`, `external-wait` or `user-interruption`) |
| `BLOCKED` | Blocker, Containment and concrete Next probe |
| `INTERRUPTED` | Stop source, Interruption point and Interruption log naming its exact existing Andon row |
| `open` / `READY_TO_DISPATCH` | Pending decision and exact Next action |

A user-interruption pause records `Pause phase context` as `IN_PROGRESS` or
`OUTSIDE_PHASE`. Only `IN_PROGRESS` requires a numbered phase and the existing
IMPLEMENTAUDIT_PAUSE record with matching Phase, pause Status, Last completed
step and `STATE.md: updated`. `OUTSIDE_PHASE` permits truthful intake or
pre-dispatch pause without that inapplicable marker and rejects a fabricated
one. Phase-spec START/DONE anchors are templates, not execution chronology;
this context is a supplied record fact, not native event authentication.
An owner stop must bind the same source and interruption point in its
Andon row using complete identity boundaries and the same numbered phase.
A same-phase pause block cannot contradict a supplied Last completed step. An
external-wait pause also records Blocker, Containment and concrete Next probe.
These are conditions for the selected yield, not a new lifecycle,
mandatory worksheet for ordinary work, or automatic conversion of a wait into
handoff. Source parsing cannot prove the truth of an asserted fact; its evidence
and authority remain with the governor and their original owners.

TY-1 through TY-5 allow the corresponding truthful continuation record; TY-6
refuses bare abandonment. Any terminal or handoff claim routes to its original
audit predicate and cannot escape through yield. A forced host turn ending is
neither closure nor handoff. Ordinary unbound sessions retain the immediate
native cheap path and do not invoke this validator.
