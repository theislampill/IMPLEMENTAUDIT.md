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
