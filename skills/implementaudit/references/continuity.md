# Context-epoch continuity (#35)

The run root survives context loss. A reconstructed summary is an OBSERVATION OF HISTORY,
never authority. Reconcile a boundary; never replay a satisfied one-shot.

## Boundary contract

A boundary starts a CONTEXT EPOCH in STATE.md with provenance
`host-reported-compaction`, `new-session`, `handoff-resume`, `manual-resume`, or
`inferred-context-gap`. The distinct rotation boundary is
`canonical-state-rotation`; only the claim-owned rotation transaction emits it
after a verified archive. Never fabricate compaction; doubtful continuity without
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
3. Before migration, read the exact claimed root pair. After migration, select
   the evidence-only resume source below; an invalidated pair cannot pass the
   ordinary current reader. Read STATE.md and ROADMAP.md separately, followed by optional `.IMPLEMENTAUDIT/host-notes.md`, live
   repository/external/process/background state, and terminal evidence. Each
   durable file needs its own completed host action; evidence reads must not use
   ';', '&&', pipelines, multi-stage shell composition, or batching.
4. Classify critical instructions by kind/status/target. LIVE STATE WINS over
   reconstructed context.
   A true standing constraint remains binding but cannot become the ACTIVE work
   cell merely because compaction retained it prominently.
5. Refuse a satisfied/superseded one-shot: `Target already satisfied at
   <evidence>; no duplicate action taken.`
6. Record the reconciled epoch and Next action through their native owner;
   otherwise hand off exact evidence. Immutable migrated payload is not edited
   through a compatibility root or derivative snapshot.

At a boundary call `claim-run.sh --invalidate-continuity <id> --boundary
<provenance> --event <opaque-event-id>`. A native host signal is a trigger,
never continuity authority. The generic no-native-hook fallback uses it for
new-session, handoff/manual-resume, or inferred-context-gap. One portable gate
governs with or without native support.

After separate reads mint `--resume-controller <id> --boundary <provenance>
--epoch <epoch>`, with the exact expected pointer and invalidation tokens for
migrated runs as below, then `--verify-resume-receipt`. This binds controller/claim,
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

`audit-state` is downstream cognition, never the currentness gate. The ordinary
reconstruction route requires a mechanically current receipt when judgement is
needed. The completed-compaction/resume requirement below is a separate bounded
execution obligation even when currentness or the measured epoch is unresolved.
Neither route can mint the invalidation/receipt or authorise an effect.
When the governor then resolves and actually loads `audit-state`, the first
permitted route narration must include `CHILD_SKILL_ROUTE=audit-state` and a
plain-language reason for the selection. Do not emit that line for a
deterministic/governor-only recovery, package discovery, similar vocabulary, or
an intended-but-unloaded route. For the ordinary route, a route announcement before current receipt, after
unrelated post-receipt narration, without an actual load, or under a different
child name is non-evidence. For a required completed boundary with unresolved
currentness, the actual-load announcement states that unresolved limit; it does
not claim a receipt or resume ordinary execution.

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

## Canonical generations and readers

The existing claim, projection and paired-reader owners load the exact captured
`canonical_custody.py` substrate for supported Windows handle custody and bounded
Git reads. It owns no ref publication, epoch, receipt, producer admission or
currentness. Each independent object lookup uses a fresh Git process; type,
size, hash and actual Git ref interpretation remain required. Windows custody
requires fixed local NTFS, SHA-1 objects and the supported files-ref backend;
unsupported capabilities refuse before selecting legacy or migrated authority.

`claim-run.sh` remains the sole continuity/current-pointer/receipt/marker writer.
Its private `claim-run-rotation.py` companion invokes `rotate-canonical-state.py`
for zero-model draft, anchored archive, final projection and typed retrieval;
that helper loads exact pinned `canonical_hot_projection.py` bytes. Neither
projection module publishes current authority. Source-bound interfaces and
limits live in `references/canonical-state-rotation.md`.

For a known controller, run `scripts/claim-run.sh --resolve-canonical-generation
<controller>`. Exit 0 returns `implementaudit.canonical-generation-resolution.v1`
with one pointer token, exact component paths, claim/run identity, receipt and
permanent marker, after the complete native JOIN. Exit 3 means physical absence
of BOTH pointer and migration marker. Exit 1 means malformed, incomplete, stale,
unsafe or unsupported custody: STOP, with no root-file fallback. A missing hint
is not absence of authority. Bind `.controller` to the explicit native
`--current-controller <controller>` result; never infer a current root from a
filename or an unqualified controller population.

Keep the resolved pointer token for both separate completed host reads:
`scripts/claim-run.sh --read-canonical-state <controller> --role STATE
--expected-pointer <ref>@<oid>` and, in the next completed host action,
`scripts/claim-run.sh --read-canonical-state <controller> --role ROADMAP
--expected-pointer <ref>@<oid>`. The owner re-verifies all hashes and refuses drift.
Before first migration only, its equivalent `--expected-pointer none` read
requires the exact current legacy v2 receipt. A structural validator accepting
an unbound legacy template establishes no continuity/currentness authority.

Automatic canonical validation uses `scripts/read-canonical-pair.py --run-root
<run-root> --output <empty-private-directory>`; this makes derivative-only exact
snapshots through those native owner calls. Add `--native-guards` for native
Markdown consumers. Both roles must carry protected `native_guards` groups,
owned by their exact STATE.md/ROADMAP.md role, with the
`implementaudit.native-guard-profile.v1` schema and exact native source lines.
The STATE status and next-action table rows match the protected continuation
exactly; native status vocabulary is preserved. Every native field remains
input to its original guard, including Andon recurrence, residual ownership,
model identity, cold-review evidence, instruction status and phase rows.

The adapter writes the exact canonical pair plus `native-STATE.md`,
`native-ROADMAP.md` and a private `native-records/` input directory. Only the
live epoch row is derived from the complete native JOIN: its effective epoch,
generation, invalidation, predecessor receipt and next action must match the
pointer. Preserved profiles cannot claim the live epoch heading or a row at
that epoch. Historical epoch rows, including rotation rows, retain their
original scope. Native resume uses its exact owner-bound host boundary.

`native-records/` carries all declared contained artifacts at their exact
hash-bound bytes. The direct Markdown population must be completely declared;
missing, extra, changed, aliased or unsafe dependencies refuse. The original
run-root validator, phase authority and direct cold-review record checker
consume these inputs without dropping their guards. Caller-supplied Markdown
checks, including authorization and closure/residual checks, use these selected
paths whenever their input represents current run state. After consumption,
repeat the same adapter command with `--verify-current`; it rereads STATE then
ROADMAP and compares the entire snapshot and native resolution before a result
is accepted. A snapshot grants no currentness or mutation authority.

No-profile typed pairs remain readable, but native validation refuses
`CANONICAL_NATIVE_GUARD_PROFILE_UNSUPPORTED`. Unsupported native fields are not
classified as history, and arbitrary typed JSON cannot bypass original guards.

`refs/implementaudit/current-generations/<controller>` is pointer authority over
`state-generations/<Gxxxx>/`. The permanent
`refs/implementaudit/current-generation-migrations/<controller>` marker records
first terminal v3 migration and remains unchanged. Missing either after migration
never restores root authority. Archives use exactly
`refs/implementaudit/state-archives/<controller>/<Gxxxx>` for the preparation
generation; nested `objects` or `epochs` paths are not archive anchors. The
role patterns are recorded in `canonical-state-ref-namespaces.json`; archives
remain outside controller/current discovery, fixtures and recursive archives.
Disabling future rotation retains readers, permanent markers, archive reachability,
typed retrieval, historical scope and all consumer obligations (TC06/TC11).

Rotation orders draft/archive before the fresh rotation invalidation and epoch,
then final bytes/manifests, expected-old pointer CAS, real v3 receipt and marker.
Future receipt/pointer object IDs are never upstream hash inputs. Compensation
uses a fresh recovery epoch and an exact available predecessor receipt; an
allocated failed epoch need not have a receipt. Unknown effects or a newer
boundary stop; they never justify receipt fabrication or stale compensation.

### Native resume after migration

After the fresh native invalidation, call
`claim-run.sh --resolve-resume-generation <controller>`. Its
`implementaudit.native-resume-source.v1` result is labelled
`PRE_RESUME_EVIDENCE`: it binds the exact prior pointer, original v3 receipt,
permanent marker, fresh invalidation token, actual host boundary and next epoch
and generation. It grants no currentness. Read its two immutable components
with both returned tokens, each command in its own completed host action:

```text
claim-run.sh --read-resume-state <controller> --role STATE --expected-pointer <pointer-token> --expected-invalidation <invalidation-token>
claim-run.sh --read-resume-state <controller> --role ROADMAP --expected-pointer <pointer-token> --expected-invalidation <invalidation-token>
```

Then call `claim-run.sh --resume-controller <controller> --boundary <actual-boundary>
--epoch <next_continuity_epoch> --expected-pointer <same-pointer-token>
--expected-invalidation <same-invalidation-token>`. The native owner preserves
the exact protected payload, publishes a fresh immutable pair and real v3
receipt, and uses the original host boundary without relabelling it as rotation.
Verify the returned receipt and require current continuity before ordinary
execution. The completed exact retry is idempotent. Uncertain partial native
publication stops with its retained descriptor; rotation compensation is not a
native-resume repair. The historical
`MIGRATED_RESUME_REQUIRES_CANONICAL_SUCCESSOR` refusal identified the missing
owner route; it never authorized root fallback or receipt fabrication.

Ordinary `--read-canonical-state` and `read-canonical-pair.py` remain strict
current readers. Neither the prior receipt nor `PRE_RESUME_EVIDENCE` discharges
their gate. Unsupported payload changes or erroneous-invalidation adjudication
need their actual owner route; this resume operation grants neither.

## Pending completed compaction and resume

An independently proved completed compaction/resume creates a mandatory bounded
`audit-state` execution obligation. R0033/continuity owns its requirement,
routing, observation and accepted consumption; rotation remains zero-model.
Missing measured epoch or unresolved currentness limits the result's authority;
it does not make execution optional, satisfied or absent. This is the sole
bounded cognition exception to the ordinary post-boundary execution STOP. It
does not permit unrelated narration, checks, writes or task effects.

Carry each pending boundary's identity, original evidence locator and physical
source binding, observation scope/cutoff, reservation and actual result, accepted
consumption witness or explicit absence, uncovered successors, historical
refusal, selected/prior occurrences and any supported retry. The governor's
required-boundary envelope binds that evidence and explicitly records unresolved
currentness and absent epoch. The child returns bounded cognition without
currentness, mutation, dispatch, lifecycle or closure authority. The native
owner must still accept the actual occurrence before consumption is recorded.

Two actual compactions with equal H0/currentness labels remain two occurrences.
A witness for the first leaves the second pending unless its actual observation
scope proves coverage. Dispatch, reservation, failed return, equal output, copied
command text, repeated call ID or a later correct answer cannot stand in for the
original successful occurrence and accepted JOIN. Preserve original-prefix
refusals and original historical scope (TC11); a later correction limits current
use without rewriting prior evidence. No new event store, observer, router or
steward is introduced here, and no reserved next owner is allocated.

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
