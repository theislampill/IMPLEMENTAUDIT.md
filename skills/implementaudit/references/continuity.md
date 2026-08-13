# Context-epoch continuity (#35)

The run root is durable across compactions, sessions, resumes, and handoffs. A
reconstructed summary is an OBSERVATION OF HISTORY, never current authority.
Reconcile after a boundary and never replay a satisfied one-shot instruction.

## Boundaries and epochs

A boundary starts a CONTEXT EPOCH in STATE.md `## Context epochs and instruction
applicability`. Provenance is exactly one of:

```text
host-reported-compaction
new-session
handoff-resume
manual-resume
inferred-context-gap
```

Never invent a host compaction. If continuity is doubtful without a host signal,
use `inferred-context-gap`. An uninterrupted turn crosses no boundary and adds
no epoch ceremony.

## Required post-boundary reconciliation

Before the next repository mutation:

1. Establish the unique run root and repository identity.
   `scripts/claim-run.sh --current-controller [controller-id]` discovers the
   Git-common controller without prior worktree knowledge. Missing, ambiguous,
   invalid, or stale custody refuses; never guess.
2. Reread current `ROADMAP.md`, `STATE.md`, repository-family
   `.IMPLEMENTAUDIT/host-notes.md` when present, process/background-chain state,
   and relevant terminal evidence. Each live durable-state file must be read in
   its own completed host action. Evidence-bearing read actions must not use
   ';', '&&', pipelines, multi-stage shell composition, or batching.
3. Classify continuity-critical instructions by kind, status, and target.
4. Compare reconstructed context with durable state. LIVE STATE WINS; summaries
   never reopen terminal evidence.
5. Refuse a satisfied or superseded one-shot with `Target already satisfied at
   <evidence>; no duplicate action taken.`
6. Restore STATE.md's current next authorised action; continue rather than
   restarting the run.
7. If identity, state, or instructions cannot be reconciled, hand off the exact
   evidence rather than speculate.

Transfer controller ownership with the expected-claim CAS:

```text
claim-run.sh --controller <id> --supersede-claim <claim> <task>
```

Controller roots carry a value-bearing `.controller` record. A governed
mutation validates that record against the current Git-common controller ref
while holding the shared writer gate. Thus stale custody refuses before product
or transaction effects, and cooperating controller transfer serialises with an
active mutation. Ordinary roots have no controller record and retain the direct
claim/phase/pre-state/post-state cheap path. This does not fence arbitrary
non-cooperating same-principal filesystem writers.

After separate live reads and a reconciled epoch row, use `--resume-controller
<id> --boundary <provenance> --epoch <epoch>` and verify the token with
`--verify-resume-receipt`. It binds controller/run claim, HEAD/tree,
STATE/ROADMAP hashes, boundary, epoch, and Next action. Refuse post-boundary
mutation without a verified current receipt.

At phase start, read repository-family `.IMPLEMENTAUDIT/host-notes.md` when
present. It is local linked-worktree context, not portable payload authority;
portable rules use `AGENTS_UPDATE_DECISION`.

Record execution identity as:

```text
model-identity: requested_model: <model> | actual_model: <model> | evidence: self-report|host-event:<id> | claims: bound|IDENTITY_UNBOUND
```

This is the independent-review requested/resolved mapping. A model mismatch
raises `transport-infrastructure` Andon and marks later claims
`IDENTITY_UNBOUND` until reproduced or reverified under the requested identity.
Prefer a host event; otherwise mark self-report. The epoch row is the record;
there is no new transcript marker.

## Instruction lifecycle

Kinds:

```text
one-shot-action
standing-constraint
standing-authorization
persistent-objective
query-or-information-request
```

Statuses are `active`, `satisfied`, `superseded`, `revoked`, `expired`, or
`ambiguous`. Only one-shot actions normally become satisfied. Standing
constraints and authorisations survive until revoked, superseded, expired, or
out of scope; reconciliation must not consume them.

Each applicability row binds instruction id, hashed/id source reference (not
raw chat), kind, authority, subject/version, issued epoch, status and evidence,
supersedes/by links, and scope end/expiry. Preconditions and terminal predicates
belong in status evidence.

Apply this lifecycle to run-authored steer and advisory outputs. Successors
amend one continuity document with a `supersedes:` header rather than leaving
competing authorities. Copy precision-critical owner vocabulary verbatim at
receipt time. More than two artifacts without precedence warns but does not
automatically fail because authority may remain external.

## Repeated current owner message

An identical new owner message is fresh authority. For a terminal target say:
`Target already satisfied at <evidence>; no duplicate action taken. Current
open state is <state>.` Reactivation requires reopen/re-audit, a changed target,
or invalidating evidence, recorded as a new row.

## Capsule and terminal durability

A boundary capsule rederives repository identity, epoch, next action, and active
instructions from live owners; inherited capsules reverify. At closure,
recapture anchors; moved anchors need checkable re-anchor evidence or
`SUPERSEDED_BY_CONCURRENT_MUTATION`.

Before a terminal action, append one `PENDING_TERMINAL` line naming the exact command and preconditions.
Clear it only after success. On re-entry, resume it
only after re-checking its preconditions. This preserves both halves of the
one-shot invariant: never lose an unsatisfied one, and never redo a satisfied one-shot
whose cleared record and terminal evidence remain valid.

## Single-writer epoch and migration

At most one concurrent resume establishes an epoch; the loser observes the
create-once claim and waits or hands off. Legacy roots without an epoch section
remain resumable; the section becomes required only for new epochs. The first
legacy resume may create it after validating durable state. Never copy full
conversation text into the run root; retain ids/hashes under existing custody
and privacy boundaries.
