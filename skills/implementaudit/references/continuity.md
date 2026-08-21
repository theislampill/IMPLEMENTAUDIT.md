# Context-epoch continuity (#35)

The run root survives context loss. A reconstructed summary is an OBSERVATION OF HISTORY,
never authority. Reconcile a boundary; never replay a satisfied one-shot.

## Boundary contract

A boundary starts a CONTEXT EPOCH in STATE.md with provenance
`host-reported-compaction`, `new-session`, `handoff-resume`, `manual-resume`, or
`inferred-context-gap`. Never fabricate compaction; doubtful continuity without
a host signal is `inferred-context-gap`. An uninterrupted turn adds no ceremony.

```text
POST_BOUNDARY_FIRST_SUBSTANTIVE_MESSAGE=VERIFIED_CONTINUITY_RECEIPT
POST_BOUNDARY_NEW_EXECUTION=REFUSE_UNTIL_CURRENT
PREBOUNDARY_PROCESS=WAIT_OR_TERMINATE_ONLY
STANDING_CONSTRAINT_ROLE=DO_NOT_PROMOTE_WITHOUT_LIVE_STATE
```

The boundary is an ordered stop-the-line gate. Before ordinary task narration,
new commands, audit-artifact writes, package builds, source effects or external
effects, discover the controller and immediately record the real boundary with
`claim-run.sh --invalidate-continuity <id> --boundary <provenance> --event
<opaque-event-id>`. This makes an older receipt mechanically stale before any
reconstructed summary can route work. A pre-boundary process may only be waited
on or terminated for containment. Its terminal output is classified after
reconciliation against the exact process/candidate; do not start a replacement
or promote the result before currentness.

Before repository mutation:

1. Use `scripts/claim-run.sh --current-controller [controller-id]`; missing,
   ambiguous, invalid, foreign, or stale custody refuses—never guess.
2. Issue the fresh `--invalidate-continuity` event described above. If the host
   did not supply a native boundary, use the honest fallback provenance rather
   than silently retaining an old receipt.
3. Reread STATE.md, ROADMAP.md, optional `.IMPLEMENTAUDIT/host-notes.md`, live
   repository/external/process/background state, and terminal evidence. Each
   durable file needs its own completed host action; evidence reads must not use
   ';', '&&', pipelines, multi-stage shell composition, or batching.
4. Classify critical instructions by kind/status/target. LIVE STATE WINS over
   reconstructed context.
   A true standing constraint remains binding but cannot become the ACTIVE work
   cell merely because compaction retained it prominently.
5. Refuse a satisfied/superseded one-shot: `Target already satisfied at
   <evidence>; no duplicate action taken.`
6. Record the reconciled epoch and Next action; otherwise hand off exact evidence.

At a boundary call `claim-run.sh --invalidate-continuity <id> --boundary
<provenance> --event <opaque-event-id>`. A native host signal is a trigger,
never continuity authority. The generic no-native-hook fallback uses it for
new-session, handoff/manual-resume, or inferred-context-gap. One portable gate
governs with or without native support.

After separate reads mint `--resume-controller <id> --boundary <provenance>
--epoch <epoch>`, then `--verify-resume-receipt`. This binds controller/claim,
HEAD/tree, STATE/ROADMAP hashes, invalidation, boundary, epoch, and Next action.
New continuity generations use `G` plus four uppercase hexadecimal digits
(`G0001`, `G000A`, `G0040`). A legacy `eNN` input is accepted only as an alias
and is canonicalised before a new receipt is minted; unchanged historical
`eNN` state and receipt records remain exact legacy evidence rather than being
rewritten in place.
`--require-current-continuity <id>` verifies the binding under the shared writer
gate before effects. The first substantive post-boundary message reports the
verified receipt, controller/epoch, exact ACTIVE/READY/BLOCKED frontier and any
discrepancy. Only then may ordinary task narration or new execution resume.
Legacy v1 receipts work only without invalidation.

### Canonical-state reader migration

`--require-current-continuity` reads the permanent migration marker at
`refs/implementaudit/current-generation-migrations/<controller>`, the pointer at
`refs/implementaudit/current-generations/<controller>`, and the receipt selected
by that pointer before it considers the root receipt path. The first publication
order is exactly `pointer -> receipt v3 -> permanent marker`: R0039 publishes and
rereads the canonical pointer by expected-old-zero CAS, R0011 mints and verifies
the receipt from that already-current pointer, and R0039 may publish the marker
only after the verified receipt exists. There is no alternative order or second
currentness writer.

The final `implementaudit.continuity-receipt.v3` has one byte form: 18 nonempty
UTF-8 fields separated by exactly 17 tabs and terminated by exactly one LF,
with no CR or interior LF. Missing/extra LF, CRLF, trailing tabs, or an extra
empty field are not receipts. It binds controller, claim, bound run name,
source epoch, invalidation OID, pointer ref, pointer OID/digest, hot
STATE/ROADMAP digests, WORK_GRAPH path/digest, generation manifest OID/digest,
cold high-water, exact next action, and the immediately preceding receipt token.
Every v3 verifier derives the exact `G(n-1)` receipt ref, requires token equality,
then validates that predecessor record; a valid record aliased under any other
generation ref is not a predecessor. R0011 preserves and verifies the raw bytes
after expected-zero publication. The reader matrix is fail closed:

- with marker and pointer both physically proved absent from loose and packed
  ref custody, only the exact current root receipt with schema
  `implementaudit.continuity-receipt.v2` is current; a broken or malformed ref
  is STOP, and v1 remains historical verification evidence, not a current route;
- a pointer without its exact v3 receipt is incomplete and never current;
- a valid pointer and its exact joined v3 receipt without a marker stops as
  `FIRST_MIGRATION_INCOMPLETE`;
- once any marker ref exists, an absent or structurally malformed pointer stops
  as `STOP_NO_ROOT_FALLBACK`, and no root receipt may restore currentness; and
- marker, pointer, and `implementaudit.continuity-receipt.v3` are current only
  when their schemas and every authority, pointer, hot, graph, manifest,
  high-water, predecessor, and next-action field form one exact join.

Unknown records, mixed v2/v3 state, wrong object types, owner/run/schema drift,
or a stale pointer/receipt join are STOP. These are reader rules only: reading
does not publish, repair, delete, or otherwise update a pointer, receipt, or
migration marker.

Routine v3 recovery is bounded: it reads the current pointer, hot STATE and
ROADMAP pair, `WORK_GRAPH` path/digest, selected receipt, invalidation and
marker. Historical event segments are not read. A corrupt referenced segment
therefore does not invalidate an otherwise exact routine currentness check; it
fails only when the explicit immutable-history query reads and validates that
segment. Recovery after an interrupted first publication uses a fresh R0011
invalidation/epoch and either completes the same verified pointer transaction
or publishes a proved compensating successor. It never hydrates wholesale
history or restores root-v2 after a marker exists.

`audit-state` is downstream cognition, never the gate: route it only after the
receipt is mechanically current when stale-context reconstruction still needs
model judgement. It cannot mint the invalidation/receipt or authorise an effect.
When the governor then resolves and actually loads `audit-state`, the first
permitted route narration must include `CHILD_SKILL_ROUTE=audit-state` and a
plain-language reason for the selection. Do not emit that line for a
deterministic/governor-only recovery, package discovery, similar vocabulary, or
an intended-but-unloaded route. A route announcement before current receipt,
after unrelated post-receipt narration, without an actual load, or under a
different child name is non-evidence and violates the routing contract.

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
