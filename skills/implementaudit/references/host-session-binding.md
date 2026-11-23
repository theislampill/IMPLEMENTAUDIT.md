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

The default Stop route performs read-only attribution and reports unsupported
effect authentication. A selected policy can validate its pinned record. The
unselected donor route below requires a separately admitted integration.

`consume-proximal-action` is the R0035 continuation-custody join. An admitted
Stop adapter selects this operation from its trusted installation and the fixed
`PLUGIN_DATA/host-session-binding-v1` store. It supplies the exact current
binding/event plus the deterministic compiler selection. The selection uses the
operation's fixed canonical UTF-8 stdin channel, never argv or a caller-selected
path/alias, and is bounded at 131072 bytes before parsing or custody. Empty,
oversized, malformed, duplicate-member, or noncanonical stdin fails closed.
Under the existing writer lock, the core first-creates an immutable receipt
keyed by the canonical selection digest beneath the exact host/session binding.
Byte-identical copied, renamed, or concurrent transports therefore have one
identity; same-event redelivery is idempotent, another event is replay, and
uncertain completion remains consumed. The receipt carries authority `NONE`:
it proves one continuation decision was consumed, not DONE, merge, install,
currentness, publication, cutover, or release.

The Stop adapter evaluates the current route and turn disposition before this
custody step. A blocked, unsatisfied, or unavailable turn cannot consume its
selection merely by reaching Stop. Only an otherwise-`ALLOW` turn may consume
the exact selection, and authoritative `ALLOW` is emitted only after that
consumption succeeds. Thus disposition failure preserves the action for a
later current event, while a consumed or unknown-completion action cannot be
replayed under another event.

The Stop consumer accepts only one closed
`implementaudit.host-abnormality-classification.v1` record bound to the exact
Stop event, with classification `NONE`, `MECHANICAL` or `SUBSTANTIVE`. The Stop
adapter never infers this class from assistant prose. The donor standard Stop
hook has no host-owned trusted semantic producer for that record; parallel Stop
hooks receive the same event rather than a prior hook's transformed output.
Accordingly ordinary installed Stop events remain `UNCLASSIFIED` and
non-authorizing until the host exposes such a producer capability.
Absent, malformed, stale or foreign classification is non-authorizing.
`NONE` and `MECHANICAL` retain the cheap path. `SUBSTANTIVE` is admissible only
when the current route reports exact selected child `audit-andon`,
`REQUIRED/SATISFIED`, and one governor reconciliation; otherwise Stop blocks
governor substitution. A governed child requester remains rejected by the live
dispatch gate.

## Host-owned holon stage receipts

`record-holon-stage` is the source owner for writing LOAD, USE and DISPOSE
receipts. Under the current ACTIVE binding and store writer lock, it first-creates
one immutable `implementaudit.host-holon-stage-receipt.v1` file. The receipt is
bound to the store owner, host, session, binding generation, selected child,
packet digest, obligation, route transaction, exact stage and observed event.
Its identity is the digest of that closed body; aliases, replacement and a
second creation of the same identity fail closed.

A child return carries only the three ordered receipt identities. The route
consumer independently resolves their exact immutable bytes through this
host-owned store and revalidates every binding before projecting lifecycle
credit. Arbitrary, absent, foreign, wrong-stage, wrong-child, wrong-packet,
wrong-obligation, wrong-transaction or cross-session identities leave
LOAD/USE/DISPOSE unverified. Re-reading the same exact resolved receipts during
completion is currentness verification, not new credit; using them for another
delivery is rejected by the identity bindings.

Target prose, transcripts, child or subagent output, cwd, newest-run selection,
and controller-singleton inference are never inputs to identity resolution.

## Session end, GC and proof boundaries

`tombstone --reason session-end` ends session attribution. It reports
`object_closed: false` and does not write to the controller, run root,
continuity receipts or evidence state.

`gc` is store-owner-bound and expected-generation fenced. It retains at least
the current generation and removes only explicitly named non-active generations
that carry a separately supplied closure-owner resolution receipt. Missing
resolution evidence fails closed. Repeating the same request is idempotent.
GC never deletes or edits controller, run-root, continuity or evidence state.
Resolved older generations may be absent from retained history; a caller's
requested lineage slice must still be contiguous and every requested record
must be present. GC does not manufacture missing lineage evidence.

Every successful binding result separates the proof layers:

```text
source_core=PRESENT
package=UNVERIFIED
install=UNVERIFIED
host_activation=UNVERIFIED
```

Source behavior therefore cannot be promoted into a package, install, native
host discovery, activation, enforcement or universal-host claim.

Rollback removes the thin host adapter and R003A store records. Preserve the
controller, claim, governed run, continuity receipts and audit evidence.

## Stop attribution and reserved adapters

For selected Stop attribution (role R), use `python -I -S -B
<skill-dir>/scripts/host-stop-interlock.py` with bounded Stop JSON.
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
