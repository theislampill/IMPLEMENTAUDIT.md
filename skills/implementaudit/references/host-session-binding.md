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

## Read path and event correlation

`lookup --host-id <host> --host-session-id <session>` is read-only. When the
exact binding file is absent it returns `UNBOUND` immediately without creating
the store, scanning a repository, enumerating run roots, selecting a singleton,
or running a validator.

`validate-event` is also read-only. It requires the current binding generation
and every controller/claim/run/repository/worktree/continuity identity. It
rejects stale, reordered, foreign, ambiguous and tombstoned attribution. Its
correlation ID is a deterministic digest of the exact binding and admitted
event, turn, tool-use, agent, obligation and route-transaction identifiers.
Route obligation and transaction IDs must be supplied together; successful
correlation does not satisfy or consume either one.

`consume-proximal-action` is the R0035 continuation-custody join. The installed
Stop adapter, not target content, selects this operation and the fixed
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
adapter never infers this class from assistant prose. The packaged standard Stop
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

`record-holon-stage` is the only native source owner for LOAD, USE and DISPOSE
credit. Under the current ACTIVE binding and store writer lock, it first-creates
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

## Standalone hook compatibility

The standalone compatibility projection retains the shared internal hook substrate
from the canonical product, but has no hooks/hooks.json and no host activation.
These files are dormant in that projection, not operator diagnostics or a promise
that a native event is registered. Their canonical counterpart remains dispatched
only by its exact installed and enabled hook owner.

- scripts/codex-compact-interlock.py is retained as an internal dormant shared
  SessionStart compact consumer in the standalone projection; the canonical hook
  protects bound continuity. There is no host activation in standalone.
- scripts/codex-recovery-prompt-input.py is retained as an internal dormant shared
  UserPromptSubmit consumer in the standalone projection; the canonical hook
  observes exact recovery input. There is no host activation in standalone.
- scripts/host-stop-interlock.py is retained as an internal dormant shared Stop
  consumer in the standalone projection; the canonical hook checks exact turn
  disposition. There is no host activation in standalone.

The package-role checker verifies both the missing standalone hook manifest and
the exact canonical Python hook commands before admitting this retained dormant
disposition. An added activation route, missing counterpart, changed owner or
different executable identity requires a fresh role decision. Merely copying or
directly calling one of these files does not establish a supported host route.
