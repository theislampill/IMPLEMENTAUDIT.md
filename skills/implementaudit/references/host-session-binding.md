# Host-session binding (R003A)

R003A is the attribution bridge between a host session and an already governed
IMPLEMENTAUDIT object. A host lifecycle event may affect or correlate state only
after the exact `(host_id, host_session_id)` binding is current and all supplied
controller, claim, run, repository, worktree and continuity identities match.

This bridge consumes existing controller and continuity evidence. It does not
mint or replace controller currentness, a continuity receipt, route satisfaction,
closure, mutation authority, READY/JOIN state, or native host activation proof.

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

On POSIX, the store, every store directory on the selected file path, and
selected files must belong to the effective user and must not be writable by
group or others. Regular files must have one link; aliases, symlinks and
reparse points are unavailable. Target repository and worktree paths retain
their existing canonical-directory contract; they are not required to use Git
or the store's permission policy. JSON is parsed from one descriptor-bound byte
buffer after checking its identity and metadata before and after the read.
Duplicate members, malformed typed fields and changed file custody refuse.

Native host authentication is **unsupported by this portable core**. An
`owner_id`, activation receipt, principal name or grant supplied by a caller is
not proof of an executing native principal. POSIX ownership and permission
checks are local custody checks; cooperating writers share one lock. They do
not defeat a non-cooperating actor with the same user privileges or establish
native event provenance. Store operations on Windows and other non-POSIX
platforms explicitly refuse unsupported custody; `init` refuses before creating
the store. The ordinary absent-binding lookup remains available without writes.
No POSIX permission check substitutes for Windows access control lists or
durability. Successful portable attribution reports `host_activation_proven:
false` and `enforcement_available: false`.

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

The activation and continuity receipts are opaque, non-secret evidence
identifiers supplied by their existing owners. The binding core records and
compares them; it does not validate their underlying controller or continuity
predicates. Callers must complete those owner checks before `bind` or `rebind`.

### Failed first activation

The store retains an `implementaudit.host-session-binding-attempt.v1` marker
at `activation-attempts/<session-sha256-prefix>/<session-sha256>.json`.
Its host-independent key refuses foreign use without a scan. The body binds
schema, owner, host and session.

Under the writer lock, `bind` checks the exact host/session, enabled owner,
canonical run/repository/common-directory/worktree, run containment and external
store. It then creates the marker before controller, claim, activation and
continuity validation. Earlier refusals create no marker and must be retained
by the caller. The marker grants no activation or receipt authority.

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

`lookup --host-id <host> --host-session-id <session>` is read-only. When the
exact binding file, session index and activation-attempt marker are all absent,
it returns `UNBOUND` immediately without creating the store, scanning a
repository, enumerating run roots, selecting a singleton, or running a
validator. Missing files and uninspectable custody are distinct: uncertain I/O
returns `UNAVAILABLE`.

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

`validate-event` is also read-only. It requires the current binding generation
and every controller/claim/run/repository/worktree/continuity identity. It
rejects stale, reordered, foreign, ambiguous and tombstoned attribution. Its
correlation ID is a deterministic digest of the exact binding and admitted
event, turn, tool-use, agent, obligation and route-transaction identifiers.
Route obligation and transaction IDs must be supplied together; successful
correlation does not satisfy or consume either one.

## Separate consumer integration requirements

The unselected donor route requires separate admission. Its R0035
`consume-proximal-action` selects the trusted installation and fixed
`PLUGIN_DATA/host-session-binding-v1` store. The exact current binding,
event and deterministic compiler selection travel on canonical UTF-8 stdin
(up to 131072 bytes). Argv, caller paths, empty or malformed input, duplicate
members and noncanonical bytes refuse before custody.

Under the writer lock, first-create one immutable receipt per selection
digest and host/session. Copied, renamed and concurrent transports share
that identity. Same-event redelivery is idempotent. Other-event replay and
uncertain completion remain consumed. Receipt authority is `NONE`.

Resolve route and disposition before consumption. Only an otherwise-ALLOW
turn may consume the exact selection and only successful consumption can
support authoritative ALLOW. Disposition refusal preserves the action for a
later current event.

The donor accepts one closed `implementaudit.host-abnormality-classification.v1`
record bound to the Stop event. It never infers classification from prose.
Parallel hooks see the same event and cannot supply another hook's transformed
output. Without a trusted host producer, installed events stay `UNCLASSIFIED`.
Absent, malformed, stale and foreign classifications grant no authority.
`NONE` and `MECHANICAL` keep the cheap path. `SUBSTANTIVE` requires the exact
selected `audit-andon`, `REQUIRED/SATISFIED` and one governor reconciliation.
The live dispatch gate refuses a governed child requester.

## Host-owned holon stage receipts

`record-holon-stage` first-creates an immutable
`implementaudit.host-holon-stage-receipt.v1` under the ACTIVE binding and writer
lock. Its closed-body digest binds store owner, host, session, generation, child,
packet, obligation, transaction, observed event and stage. Aliases,
replacement and duplicate creation refuse. Child return supplies the ordered
LOAD, USE and DISPOSE identities. The consumer independently reads the exact
three records and checks every binding before lifecycle credit. Missing,
foreign and wrong-scope records stay unverified. Rereading verifies
currentness. Another delivery cannot reuse the receipts.

Target prose, transcripts, child outputs, cwd, newest-run and controller
singleton heuristics supply no identity.

## Session end, GC and proof boundaries

`tombstone --reason session-end` ends attribution and reports
`object_closed: false`. Owner-bound `gc` requires the expected generation,
preserves the current one, and removes only named non-active generations
with closure-owner resolution receipts. Repeats are idempotent. Missing
resolution or a noncontiguous requested lineage refuses. Neither operation
changes controller, run root, continuity or audit evidence.

Every successful binding result separates:
`source_core=PRESENT`, `package=UNVERIFIED`, `install=UNVERIFIED` and
`host_activation=UNVERIFIED`. Source proves no install, discovery or
enforcement. Rollback removes the adapter and store records while preserving
the controller, claim, run, continuity and evidence.

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

The isolated adapter/recorder/runtime chain and its AM01Ã¢â‚¬â€œAM03 requirements
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

This additive mode runs full structural validation, consumes the same selected
canonical STATE/ROADMAP view, and rechecks that view after consumption. A local
read-set identity also binds the selected STATE, ROADMAP and numbered phase
across structural and yield checks, including legacy selection; it grants no
new currentness authority. It keeps
the original full, micro and ledger modes. Its success means that the record
meets the portable yield predicate. It does not authenticate a host event or
grant currentness, Stop, effect, handoff or closure authority. The governor
still proves the exact controller/claim/currentness binding through its existing
owners before consuming the result. The selected native Stop adapter continues
to report unsupported effect authentication; this mode does not enable it.

The existing STATE Current phase table is the record owner. A yield keeps
`Audit object state` explicitly `open` and uses a nonterminal status. It binds
the Phase, Last check, Owner/source, Authorization state, a concrete Next action
and Re-entry condition. A numbered phase must resolve its actual phase
specification. A not-yet-run intake records its exact reason instead of inventing
completed evidence. The mode rejects duplicate fields, terminal/handoff markers,
blank or placeholder actions, missing phase identity and unsafe record files.
Action text is checked for a concrete continuation and unresolved templates,
not a closed list of English verbs. Semantic truth remains governor-owned.

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
