# Context-epoch continuity (#35)

The run root survives context loss. A reconstructed summary is an OBSERVATION OF HISTORY,
never authority. Reconcile a boundary; never replay a satisfied one-shot.

## Boundary contract

A boundary starts a CONTEXT EPOCH in STATE.md with provenance
`host-reported-compaction`, `new-session`, `handoff-resume`, `manual-resume`, or
`inferred-context-gap`. Never fabricate compaction; doubtful continuity without
a host signal is `inferred-context-gap`. An uninterrupted turn adds no ceremony.

Before repository mutation:

1. Use `scripts/claim-run.sh --current-controller [controller-id]`; missing,
   ambiguous, invalid, foreign, or stale custody refuses—never guess.
2. Reread ROADMAP.md, STATE.md, optional `.IMPLEMENTAUDIT/host-notes.md`, live
   repository/external/process/background state, and terminal evidence. Each
   durable file needs its own completed host action; evidence reads must not use
   ';', '&&', pipelines, multi-stage shell composition, or batching.
3. Classify critical instructions by kind/status/target. LIVE STATE WINS over
   reconstructed context.
4. Refuse a satisfied/superseded one-shot: `Target already satisfied at
   <evidence>; no duplicate action taken.`
5. Record the reconciled epoch and Next action; otherwise hand off exact evidence.

At a boundary call `claim-run.sh --invalidate-continuity <id> --boundary
<provenance> --event <opaque-event-id>`. A native host signal is a trigger,
never continuity authority. The generic no-native-hook fallback uses it for
new-session, handoff/manual-resume, or inferred-context-gap. One portable gate
governs with or without native support.

After separate reads mint `--resume-controller <id> --boundary <provenance>
--epoch <epoch>`, then `--verify-resume-receipt`. This binds controller/claim,
HEAD/tree, STATE/ROADMAP hashes, invalidation, boundary, epoch, and Next action.
`--require-current-continuity <id>` verifies the binding under the shared writer
gate before effects. Legacy v1 receipts work only without invalidation.

Transfer by expected-claim CAS:

```text
claim-run.sh --controller <id> --supersede-claim <claim> <task>
```

Controller roots carry value-bearing `.controller`; the gate compares it with
current Git-common custody, refusing stale custody and serialising cooperating
transfer. Ordinary roots retain the claim/phase/pre/post-state cheap path.
Non-cooperating same-principal writers remain outside the guarantee.

`.IMPLEMENTAUDIT/host-notes.md` is local context, not portable authority;
portable rules use `AGENTS_UPDATE_DECISION`.

## Identity and instruction lifecycle

```text
model-identity: requested_model: <model> | actual_model: <model> | evidence: self-report|host-event:<id> | claims: bound|IDENTITY_UNBOUND
```

Mismatch raises `transport-infrastructure` and keeps claims `IDENTITY_UNBOUND`
until reproduced/reverified. Prefer host-event evidence; otherwise self-report.
The epoch row, not a transcript marker, records reviewer requested/resolved.

Kinds: `one-shot-action`, `standing-constraint`, `standing-authorization`,
`persistent-objective`, `query-or-information-request`. Status: `active`,
`satisfied`, `superseded`, `revoked`, `expired`, `ambiguous`. Normally only a
one-shot is satisfied; standing controls persist until ended.

Rows bind instruction id, hashed/id source (not raw chat), kind, authority,
subject/version, epoch, status/evidence, supersedes/by, and scope end; status
evidence holds predicates. Apply this to run-authored steer and advisory
outputs. Successors amend one document with `supersedes:`. Copy
precision-critical owner vocabulary verbatim. Missing precedence warns but is
not alone failure.

An identical owner message is fresh authority. For terminal targets say
`Target already satisfied at <evidence>; no duplicate action taken. Current
open state is <state>.` Reactivation requires reopen/re-audit, changed target,
or invalidating evidence in a new row.

## Terminal and migration durability

A boundary capsule rederives identity, epoch, Next action, and active
instructions; inherited capsules reverify. Moved closure anchors need checkable
re-anchoring or `SUPERSEDED_BY_CONCURRENT_MUTATION`.

Before terminal action append `PENDING_TERMINAL` with the exact command and preconditions.
Clear it only after success; resume only after re-checking its preconditions.
Thus never lose an unsatisfied one-shot and never redo a satisfied one-shot
with cleared record and terminal evidence.

One writer establishes an epoch; a loser waits or hands off. Legacy roots may
create the epoch table after validation. Never copy full conversation text;
retain ids/hashes within existing custody/privacy.
