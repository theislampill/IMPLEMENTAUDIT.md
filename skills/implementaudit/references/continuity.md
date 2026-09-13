# Context-epoch continuity (#35)

The run root survives context loss. A reconstructed summary is an OBSERVATION OF HISTORY,
never authority. Reconcile a boundary; never replay a satisfied one-shot.

## Mandatory post-compaction reconciliation

`POST_COMPACTION_RECONCILIATION` distinguishes
`AUDIT_STATE_EXECUTION_ELIGIBILITY != AUDIT_STATE_RESULT_AUTHORITY`.
Completed compaction and governor resumption independently require audit-state.
Currentness, continuity, a valid measured epoch, causal abnormality and ordinary
native admission are not execution prerequisites. Unknowns limit returned
findings and downstream effects. No new state-dependent governor cognition or
effects proceed as reconciled until this audit RETURN is accepted and JOINed;
already-running independent lawful ordinary children continue.

```text
COMPACTION_IS_INDEPENDENT_AUDIT_STATE_TRIGGER=YES
POST_COMPACTION_AUDIT_STATE_REQUIRED=YES
AUDIT_STATE_EXECUTION_DOES_NOT_REQUIRE_CANONICAL_CURRENTNESS=YES
AUDIT_STATE_EXECUTION_DOES_NOT_REQUIRE_VALID_MEASURED_EPOCH=YES
MISSING_CURRENTNESS_OR_EPOCH_MAY_LIMIT_RESULT_NOT_ROUTE=YES
AUDIT_STATE_RESULT_AUTHORITY_REMAINS_EVIDENCE_GATED=YES
NO_AUDIT_STATE_AFTER_COMPLETED_COMPACTION_RESUME=CONFORMANCE_FAIL
RETROACTIVE_CHILD_CREDIT=NO
```

Prefer the actual `SessionStart(source=compact)` / `^compact$` hook. Its
`codex-compact-interlock.py` calls `compaction-audit-pending.py`'s `record_signal`
before old controller/currentness validation or invalidation can fail. This
mechanical recording performs no governor cognition, dispatch, native capsule
consumption or currentness publication. Under the existing explicit H0 store,
`compaction-audits-v1/<sha256(session)>/pending.json` retains the signal. Absent
or unusable store/identity yields an explicit unresolved recording result;
it does not create a store, invent an occurrence ID or suppress the audit.

The pending owner's `status` is nonmutating: it only reports retained work,
including `NO_PENDING_AUDIT`; it must not register a source, record a signal,
advance a version/cursor or reserve a child. Use observational `resume` only at
an actual post-compaction governor entry, never as a polling/status operation.
Without a hook receipt or registered corroboration, explicit `resume` retains
`UNRESOLVED_RESUME_OBSERVATION` and requires bounded audit-state with uncertainty.
A query or caller Boolean is not proof of a compaction occurrence. Do not mint
an event ID, measured epoch or currentness from this observation. Deduplication
of this delivery requires independent correlation to that exact proved occurrence;
source-descriptor identity or presence alone never correlates a delivery.
Existing hook/resume deliveries have no qualified per-delivery correlation:
retain their unresolved delivery/version even while older source proof remains
pending. Known source-boundary descriptors remain independently deduplicated;
that does not cover a later delivery beyond a child's observation cutoff.
Repeated uncertain observations retain versions and an
unknown logical occurrence count; later evidence requires an explicit relation
to a proved occurrence, never silent merging or retroactive credit.

Currentness and epoch observations are result inputs, never route gates.
The pending owner's assignments are scoped to boundary/version pairs. A failed
or unresolved assignment for A holds A, not every boundary in the session.
A distinct proved, unassigned B remains `AUDIT_STATE_REQUIRED` even while A is
assigned; `WAIT_EXISTING_AUDIT` applies to owned scope or uncertainty that cannot
safely be separated from an existing claim. Inspect `available_scope`,
`assigned_scope` and `active_children`; a compatibility `active_child` value
is not a session-wide dispatch gate.
Reservation uses the existing lock to prevent two children claiming the same
pair. Ambiguous signals cannot be relabelled as proved B to bypass A's fence.
If a hook receipt is unavailable, independently proved completed compaction and resumption
still requires audit-state. Bounded trusted transcript provenance may supply
that fallback or corroboration; no polling, host-ID invention, UI spinner,
summary mention or untrusted `transcript_path` establishes completion.
Missing source registration does not withhold bounded cognition with uncertainty.

The owner CLI requires explicit `--store`, `--session`, `--owner-id` and one
operation. `register-source` binds an owner-selected exact native session JSONL
path/physical identity/prefix under CODEX_HOME/sessions; it does not attest native
runtime equivalence. Host event paths and arbitrary trusted fields are ignored.
`reserve` binds a child, but pending survives dispatch and RETURN. After real
observation, `observe-child` binds an `observation_id` to the actual observation scope/cutoff,
source identity and covered boundary/version pairs. `return` must resolve that
child's actual evidence under the consumer contract below, then store bounded
findings and immutable result identity against the observation. Caller status
alone is not a realized return.
Only accepted exact successful RETURN/JOIN through `join` with `return_digest`
consumes those observed pairs. Logical JOIN requires actual same-child
LOAD/USE/RETURN/result evidence and explicit governor acceptance of that exact
scope. A caller `SUCCEEDED` is not a lifecycle witness, native DISPOSE receipt
or permission to consume pending. The owner revalidates available source cutoff
and scope evidence; absent provenance remains explicit uncertainty. Failed,
foreign, conflicting, unobserved or incomplete returns cannot consume pending.

B's JOIN cannot clear A or release A's assignment; A-dependent governor decisions
remain held. An active child may extend observation to a later unclaimed scope
only before its immutable RETURN and with actual observation/cutoff evidence.
A failed immutable RETURN cannot be extended or rewritten to claim later work.
Same-failed-scope retirement is `CONDITIONAL_UNQUALIFIED`: retrying that exact
scope needs a qualified consumer binding the real worker terminal state,
effect reconciliation and explicit release. Timeout, caller status, a fabricated
receipt or borrowed native abandonment rules cannot substitute. Until that
consumer and the actual lifecycle-to-logical-JOIN binding are qualified, retain
them as operative qualification gaps; local CLI success proves neither.
Decision results expose `actual_child_result_consumer=UNQUALIFIED` and
`same_failed_scope_retry=CONDITIONAL_UNQUALIFIED`; they are residuals, not
permission to retire A or declare its parent complete.

Independently correlated exact occurrence redelivery is idempotent independently
of H0 generation; descriptor deduplication does not establish that correlation.
Distinct compactions remain separate even in one session/binding. Unproved
identical signals retain delivery count/version with logical occurrence count
unknown; callback count is not a host identity. Reconnect, dispatch, partial
return and another compaction cannot erase pending. An active child covers a
later boundary only after actually observing it and binding that later scope
into its successful return; an uncovered boundary remains pending after JOIN.
Exact JOIN retry is idempotent; concurrency uses the existing writer lock and
atomic writer. Source bounds refuse qualification instead of truncating proof.

The governor visibly emits CHILD_TASK, GOVERNED_CHILD_SKILL, selected audit-state,
STATUS=OPEN and LOAD=UNVERIFIED before actual load; only after actual verified
load emits CHILD_SKILL_ROUTE=audit-state and LOAD=VERIFIED. State the bounded
post-compaction purpose, acknowledge LOAD, then release USE on the same child.
Keep USE, RETURN, DISPOSE, acceptance and consuming-parent JOIN distinct.
No retrospective route credit; actual work after a missed boundary stays
historical fact and is not replayed. After JOIN, rederive state/Auto-DAG and
continue INWARD/OUTWARD/FORWARD/BACKWARD from the reconciled lawful frontier.

This entry returns bounded identities, carriers, child/lifecycle and retention
dispositions, relevant refs/source/package evidence, topology and unresolved
authority facts. CURRENTNESS=UNRESOLVED and QUALIFIED_EPOCH=ABSENT are valid
findings. Execution/RETURN/JOIN cannot grant canonical currentness, recovery,
epoch, state mutation, native lifecycle, release or ordinary effect authority.
The native v2/v3/v4 capsule, `.used` OPEN anti-replay, admission and owner gates
below remain unchanged and separate. Pure source/tests do not prove installed
hook activation, real producer provenance or a qualified native episode.

### Actual result and governor acceptance consumer

Consume actual same-child result and separate later governor acceptance through
the existing pending owner. Caller status, hashes or authored witness JSON cannot
establish producer provenance. Actual source-profile qualification is required
before pending consumption; physical custody, parser success or a synthetic
fixture is not host-producer equivalence. Use owner-bound actual transport/task
sources and an admitted source-owned adapter, never caller-selected profiles or
borrowed native result/decision/receipt schemas. Retain qualification gaps until
actual positive evidence and the exact production path support their discharge.

For transcript and artifact payloads, bound physical read ranges before I/O.
Validate allowed physical path/identity, metadata range, pinned prefix and exact
offset/length limits before the corresponding read; reject aliases/reparse,
rewritten prefixes, partial/oversized ranges and unsupported profiles. Do not
read whole history then filter. Unknown offsets require an explicitly bounded
discovery contract. Read only authorized public records; inherited context,
private analysis and compaction replacement bodies are not execution witnesses.
Physical row labels and embedded ordinals are distinct: retain both with byte
locators and hashes, without normalization or inferred projection failure.
Actual child identity is not a shared session_id: resolve the host-produced
child identity and source parent/agent relation, keeping sender, receiver,
launch/call/output and result association distinct even with shared session data.

Resolve actual parent assistant pre-load OPEN; successful full skill LOAD on
that worker at the selected skill/package pins; subsequent visible parent
route/LOAD=VERIFIED; and a distinct USE acknowledgement delivered to the same
worker before actual USE. Wrong role/channel, quoted or late narration, foreign
ACK and parent-only LOAD fail. Opaque ACK association is not plaintext ACK
semantics: equal ciphertext, a digest, status or separate narration cannot
supply delivered authorization semantics. Require a qualified host-owned
cleartext observation or independently verifiable typed equivalent with exact
sender/receiver/message correlation. Do not infer private cognition from tool
order. Actual same-worker observation/read of the immutable assignment and its
boundary/version/cutoff scope is required; repeating observation_id is not proof.

Resolve the actual child final/return transport to immutable result bytes and
manifest members, checking the same child, call, source, code/adapter pins,
assignment, observation and covered versions. Resolve the separate governor
acceptance after that RETURN against the exact result digest and scope. The
consumer verifies actor/order/identity; the governor retains semantic judgement.
Missing, child-authored, foreign, early or mismatched acceptance and HOLD/REJECT
cannot authorize JOIN. A copied result with equal content does not transfer its
actor identity, source observation or acceptance to another child.

Production RETURN/JOIN must invoke the source-owned consumer; an unwired helper
or injected true test callback is insufficient. RETURN stores immutable actual
result identity without consumption. At JOIN re-resolve that result and distinct
acceptance, revalidate physical sources/cutoffs and owned scope under the existing
lock, then atomically update only accepted observed versions. RETURN and
acceptance alone leave pending; only a successful validated JOIN consumes accepted
observed versions. Exact result/acceptance/scope retries are idempotent without
new credit; races, crashes and conflicting substitutions preserve pending and
immutable evidence. Later/uncovered observations, including F01 deliveries, stay
pending. Failed A remains held when independent B completes.

Unsupported evidence holds consumption, not mandatory audit-state execution.
Missing currentness or epoch remains a bounded finding, never a route gate.
Consumer success grants no currentness, recovery, epoch, native lifecycle,
mutation, release or closure authority. Native DISPOSE and failed-scope retirement
remain separate; same-failed-scope retry remains CONDITIONAL_UNQUALIFIED.

#### Prospective O/U/observation/R/A chain

Use these internal packaged observation contracts through the existing pending
owner's reserve/observe-child/return/join paths. Each O/U/A record is closed JSON:
exactly the listed fields, fixed schema and literals, with dynamic values bound
to the source-owned assignment/profile types. No extra fields, caller-selected
adapter or freeform explanation is a control input. U and A each appear as one
source-defined typed JSON block in actual parent assistant commentary, resolved
from the bound physical source record and role/channel by the pure extractor.
The table defines the records; it is not itself an authorization or witness.

| Record | Schema | Closed fields | Fixed literals |
|---|---|---|---|
| O | `implementaudit.compaction-obligation.v1` | `schema, parent_identity, actual_child_identity, selected_child, observation_id, covered_boundary_versions, observation_source_cutoff, code_and_skill_pins, bounded_purpose, authority_ceiling` | `selected_child=audit-state; authority_ceiling=NONE` |
| U | `implementaudit.compaction-use-authorization.v1` | `schema, action, parent_identity, actual_child_identity, obligation_digest, observation_id, load_observation_identity, selected_child, skill_source_pin, authority_ceiling` | `action=AUTHORIZE_BOUNDED_POST_COMPACTION_RECONCILIATION; selected_child=audit-state; authority_ceiling=NONE` |
| A | `implementaudit.compaction-reconciliation-acceptance.v1` | `schema, action, parent_identity, actual_child_identity, obligation_digest, observation_id, child_observation_exchange_identity, actual_result_digest, accepted_boundary_versions, observation_source_cutoff, authority_ceiling` | `action=ACCEPT_BOUNDED_RECONCILIATION; authority_ceiling=NONE` |

O is immutable before USE and contains no result or acceptance. The existing
pending owner projects O from its actual reserved assignment/observation; a
caller cannot invent scope. Freeze exact bytes, identities, skill/code pins and
cutoff; unresolved event/currentness/epoch facts remain unresolved.

U is an actual public parent assistant commentary record after independently
observed full same-child LOAD and the separate visible CHILD_SKILL_ROUTE and
LOAD=VERIFIED announcement. The ordinary pre-load OPEN remains required. U binds
that LOAD and O and expresses bounded parent authorization; writing U does not
prove child observation. Quoted records, wrong actors/channels, late announcements
or a hash/status assertion cannot substitute for the actual record.

The held child mechanically obtains complete immutable O and validated public U
bytes through a real host tool/read exchange after LOAD. Actual same-child host
call/result association is required, including child/turn identity and complete
untruncated response content. The full untruncated O/U host response precedes
observe-child validation and substantive USE. Only after the existing
observe-child path independently resolves that completed exchange against exact
bounded source ranges, pending O and actual public U may substantive USE begin.
A helper cannot certify its own not-yet-produced host response. Child claims,
echoes, copied hashes, local witness JSON, tool status and encrypted-message
equality do not qualify the exchange. Encrypted messages may notify the child
to perform this mechanical read; no plaintext authorization credit is inferred.

R binds obligation_digest, observation_id, child_observation_exchange_identity,
exact observed versions and result identity through the same child's actual
host-observed final/return and immutable artifact/member bytes. Subsequent USE
must bind the checked exchange. R neither accepts itself nor consumes pending.

A is a distinct public parent assistant commentary record after actual R
delivery and evaluation. Resolve exact actor/source/message/range and the whole
O/observation/exchange/result tuple. accepted_boundary_versions exactly equals
R's immutable observed scope; no wildcard, superset or retroactive extension is
allowed. Any future partial-result variant needs its own exact observed scope.
Missing, vague, early, foreign, contradictory, child-authored or HOLD/REJECT
acceptance cannot consume. Mechanical verification proves actor/order/identity
and record meaning; semantic judgement remains the governor's.

JOIN resolves exact O, U, completed child observation/USE, R and A under the
existing lock/atomic writer and requires qualified actual source/adapter evidence
for production consumption. Writing O/U/A, dispatch and RETURN cannot consume.
Exact accepted-chain rereads are idempotent without extra credit; new or
conflicting U/A records require explicit reconciliation, never silent overwrite.
Later/uncovered versions and failed A's scope remain pending when independent B
completes. No native receipt, currentness, epoch, cleanup or release authority is
created or borrowed.

Source fixtures may exercise this production path with producer authentication
false; they do not qualify the actual host profile. Live positive qualification
requires a future genuine required boundary; no retroactive 14996 credit. After
applicable source adoption, independently verify actual O/U exchange, subsequent
same-child work, R, exact A and scoped consumption from allowed public ranges.
Do not manufacture compaction, replay an old child, retrofit U/A or upgrade an
opaque ACK by assertion. Missing storage/profile/full response evidence keeps
consumption unqualified, not mandatory audit-state execution ineligible.

#### Fixed policy P, qualification Q and episode E

P fixes executable policy and selector identity before O: pin executing
code/skills, parser/acquirer/consumer behavior, profile/grammar and the allowed
source-owner acquisition policy. The selector chooses that immutable policy
descriptor, not a changing episode verdict. Retain selector/policy hashing;
policy or selector changes still fail CHILD_OR_SOURCE_CHANGED. Do not silently
rebind obligations created under older code or remove the unchanged-source guard.

Q is later immutable qualification data, not executable policy. It binds exact
P, supported producer/environment and qualification scope, actual acquisition
evidence, independent review and governor qualification selection, with authority
ceiling NONE. E admits only this exact episode under P and applicable Q: bind
parent/actual child, assignment, O digest, observation, versions, O/U/exchange/
USE/R/A identities, physical sources/cutoffs, actual acquisition/custody validation
and exact result/acceptance digests. These are internal record recommendations
bound by implemented owners, not existing host APIs or caller permission fields.
Global P/Q qualification does not authenticate arbitrary profile-shaped files.
`production_profile` reports policy/qualification status only; a separate exact
episode consumer must resolve and validate E and current source evidence before
consumption. Any admitted/authenticated disposition is scoped to that exact E.

Keep Q/E as separately content-identified immutable data in existing attributed
external pending/H0 custody, outside executable/package source. Q/E arrival does
not change assignment.code or O bytes/digest, selected child, R or A. Q/E lookup
uses deterministic owner-held keys, not request/env overrides or arbitrary paths;
bind those keys to P/session/child/assignment/observation/result/acceptance.
Indexes only locate immutable records. H0 attribution, locks and record storage
do not authenticate transcript writers or observations. Owner flags, PASS labels
and hashes are not source-origin authentication. Resolve actual actor/source
handles from independently established host observation/custody and validate
bounded authentic source ranges, prefixes and the full current episode chain.

Bootstrap without a qualification cycle: freeze P and O, perform prospective U,
full same-child observation, USE, R and exact A, then acquire candidate physical
evidence C with evidence-only ceilings and no consumption. C alone grants no
episode admission. Independently establish actual source origin/custody and
review Q(P,C). Q may qualify from actual unconsumed C without prior E or successful
JOIN. The source-owned admission consumer then validates current C under P/Q and
first-creates exact E from that acquisition evidence; reviewed format alone is
insufficient. The same unchanged assignment may promote its original logical
result/acceptance after exact E arrives, without rerunning the child or rewriting
O/R/A. Revalidate original code, physical prefixes and covered versions under the
existing lock, then atomically consume only those versions. Retain the prior
proposal and admission identity. Exact retry is idempotent; conflicting evidence,
results, acceptances, scopes, crashes or races cannot overwrite history or partly
consume. Later uncovered versions and failed A remain pending when valid B joins.

No existing qualified host authenticator is established by this contract or
its source fixtures; this is not a whole-host absence claim. Actual acquisition
qualification remains open until a genuine prospective episode demonstrates the
source/acquisition owner's provenance, actual full O/U response, subsequent USE/
R/A and exact admission/consumption. An available host observation service may be
used only after its outputs and independent source association are qualified;
do not invent an API, signature, export, decryption facility or authenticated
owner. Implement and wire the real acquisition/JOIN path; an unwired validator,
injected true callback, fixture or permanent refusal is not its qualification.

Mandatory audit-state does not require Q or E, canonical currentness or a measured
epoch. Missing qualification/admission holds consumption and affected decisions,
not required cognition or independent lawful work. No native lifecycle, cleanup,
failed-scope retirement or release authority follows from P/Q/E; retain result
authority NONE and same_failed_scope_retry=CONDITIONAL_UNQUALIFIED. Use repaired P
prospectively at a genuine new boundary, without manufactured compaction or replay.
Any exceptional older-assignment migration needs separate immutable owner
reconciliation and evidence; no automatic migration is supplied here.

## Native authoritative recovery: explicit v3 admission

The following v3 variant is scoped to NATIVE_AUTHORITATIVE_RECOVERY. It changes
ordinary native admission/lifecycle currentness and v2 capsule clauses only as
stated, preserving every ordinary effect gate. It does not gate independent
POST_COMPACTION_RECONCILIATION execution above.

The explicit v3 substitution applies throughout recovery decision, OPEN,
RETURN, COMPLETE and exact terminal idempotent readback: revalidate the native
occurrence, physical H0, original subject/ref custody and bound source/input
bytes instead of asserting ordinary current continuity. Its actual OPEN and
LOAD permit the identity-bound audit-state route announcement. This grants no
ordinary effect, recovered-frontier task narration or historical cause attestation. The
separate state owner must complete publication/receipt/H0 lineage and prove
ordinary currentness before ordinary re-entry; its partial/completed retries
use that owner's exact predecessor and successor readbacks.

When ordinary mechanical currentness fails because an existing invalidation
still owns the unchanged predecessor, the explicitly selected R0033 recovery
transaction variant may admit only `audit-state`. It requires an exact
`implementaudit.post-compaction-recovery.v3` capsule produced and revalidated by
the source-pinned native reader plus physical recovery custody owner. The v3
capsule distinguishes the old invalidation SUBJECT from the new genuine
UserPromptSubmit invocation; it does not attest the historical cause. The
ordinary currentness gate remains unchanged for every ordinary route/effect.

The governor must not substantively reconstruct STATE/ROADMAP/WORK_GRAPH before
this isolated OPEN. Scope comes only from the capsule's minimum frontier. The
record names predecessor custody without ordinary current-continuity fields.
Each lifecycle phase revalidates native occurrence, H0, package/child sources,
hot-input digests and exact subject/ref custody. One native invocation may OPEN
only once in the existing consumed-capsule store. RETURN requires actual
LOAD/USE/DISPOSE receipt resolution; COMPLETE accepts exactly one governor
decision over the exact return bytes.

Recovery SATISFIED accepts cognition with `continuity_current=false`,
`advance_allowed=false` and `ordinary_effect_authority=NONE`. Its bounded
`canonical_reconciliation` proposal binds predecessor STATE digest, explicit
RETAIN_PREDECESSOR or REPLACE_NEXT_ACTION policy and exact single-line next
action text. Only the separately qualified canonical state owner may apply
that accepted proposal after fresh terminal recovery proof. That owner must
complete its separate publication/receipt/H0 lineage before ordinary re-entry.
The child never mutates state or grants currentness.

## Native authoritative boundary contract

A native-authoritative boundary starts a CONTEXT EPOCH through the STATE owner with provenance
`host-reported-compaction`, `new-session`, `handoff-resume`, `manual-resume`, or
`inferred-context-gap`. Never fabricate compaction; doubtful continuity without
a host signal is `inferred-context-gap`. An uninterrupted turn adds no ceremony.

These fence markers apply to the affected authority-sensitive execution edge,
including narration claiming its recovered frontier. They are not a global
compute mutex or permission to borrow stale authority for independent work.

```text
POST_BOUNDARY_FIRST_SUBSTANTIVE_MESSAGE=VERIFIED_CONTINUITY_RECEIPT
POST_BOUNDARY_NEW_EXECUTION=REFUSE_UNTIL_CURRENT
PREBOUNDARY_PROCESS=WAIT_OR_TERMINATE_ONLY
STANDING_CONSTRAINT_ROLE=DO_NOT_PROMOTE_WITHOUT_LIVE_STATE
```

The boundary stops work that consumes the missing currentness. Discover the
controller and use the installed boundary owner to record the real boundary
with `claim-run.sh --invalidate-continuity <id> --boundary <provenance> --event
<opaque-event-id>` before affected commands, state writes or effects. Preserve
an already recorded exact event and inspect partial effects before retry; do
not create a second invalidation for the same occurrence. An older receipt
cannot let reconstructed history route work. A process whose inputs, authority
or effect containment depend on recovered state may only be waited on or
terminated for containment. Inspect actual process/candidate and output custody
before replacement; no terminal output promotes itself.

P0 recovery is authority priority, not global compute exclusion. An already
admitted sibling may continue only if its exact inputs, authority ceiling,
writer/resource isolation and effect containment remain proved unchanged and
independent of the failed edge. A new bounded preparation task needs an already
valid scope/admission basis outside that edge; a stale summary or this exception
cannot create one. Bind that basis and inputs in the existing child capsule/lane
report (`child-agents.md`), keep preparation non-authoritative, and permit no
canonical state, route, currentness or release effects from it. If independence
is unknown, block that task; do not label stale-context semantic reconstruction
mechanical preparation. No pre-OPEN substantive STATE/ROADMAP/WORK_GRAPH read is
allowed by this exception. Record outputs without acceptance and revalidate
their exact applicability at the consuming JOIN. Changed or unknown inputs
invalidate only their affected consumers. Recompute unaffected capacity from
its own valid inputs; do not rebuild the protected frontier to justify it.

For native authority at boundaries other than genuine host-reported compaction, before repository
mutation:

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

NATIVE_AUTHORITATIVE_RECOVERY after genuine `host-reported-compaction` is stricter. On that native edge,
before a fresh isolated `audit-state` OPEN, the governor may perform only the mechanical sequence
`INVALIDATE` → `MECHANICAL_CURRENTNESS` → `OPEN_AUDIT_STATE`; the helpers may
hash or validate canonical inputs internally, but the governor must not read or
reconstruct substantive STATE, ROADMAP, WORK_GRAPH, history or transcript
content. The compact hook emits one
`implementaudit.post-compaction-recovery.v2` capsule carrying its exact event
identity, event digest and canonical capsule digest. The R0033 request cites
those exact capsule bytes as an observed input, so the derived transaction is
bound to them; OPEN consumes that capsule once. Absent, stale, foreign,
mismatched or reused capsules stop before child dispatch. Fresh `audit-state` then
reconstructs only the `MINIMUM_APPLICABLE_FRONTIER` in isolated cognition and
returns identity plus the exact next typed edge, never raw canonical content.
Its worker context is discarded after RETURN. The return remains buffered
evidence with no stale or canonical credit until governor reconciliation and
post-return currentness complete. A second genuine compaction derives a second
capsule and transaction; it never reuses the earlier worker or route credit.

For a selected whole-governor recovery qualification claim, bind one meaningful
interval in the existing recovery/action-selection record: before the first
attributable bootstrap/discovery input through dispatch, execution, compact
RETURN consumption, governor reconciliation and required post-return
owner/currentness readback. Measure retained governor context and relevant
context, dispatch, execution and reconciliation costs. Include installation
and maintenance costs where applicable with an explicit applicability basis;
unknown is not zero. Evidence must support headroom for the remaining
continuation through reconciliation, not merely the next probe. Reuse
sufficient unchanged existing mechanical continuation; changed evidence or
dependencies can justify new investigation, without an unbounded
recovery-of-recovery stack or idle repeated archaeology.

Worker packet bytes, token estimates and Boolean receiver headroom do not
measure that governor interval. Worker-local pressure does not establish a
governor compaction; genuine root-event provenance and proved dependency radius
still govern boundary and invalidation decisions. Missing required observations
leave the selected claim unqualified. Keep proposed measurements and structural
fixture assurance separate from an actual qualified episode; the E fixture
(`fixtures/a-to-g/post-compaction-isolation.json`) retains this distinction.
This adds no restart or pre-OPEN gate. Reuse sufficient unchanged evidence under
`planning-depth.md`'s Engineering-value admission and control lifecycle.

At a boundary call `claim-run.sh --invalidate-continuity <id> --boundary
<provenance> --event <opaque-event-id>`. A caller that already holds an exact
observed receipt may add `--expected-current <receipt-token>` as a guard
assertion; the token is not authority, and `claim-run.sh` independently resolves
and validates the live controller/currentness tuple. A native host signal is a
trigger, never continuity authority. The generic no-native-hook fallback uses
the same command for new-session, handoff/manual-resume, or
inferred-context-gap. One portable gate governs with or without native support.

Invalidation publication is one deterministic Git transaction. Its sorted
read set verifies the controller ref, selected receipt, current-generation
pointer or exact absence, migration marker or exact absence, and any required
root-successor absence; the invalidation update's expected-old field guards the
sole write ref. Guard/CAS loss leaves the invalidation unchanged. An uncertain
process result is classified only by exact readback as candidate committed,
old unchanged, or unknown/foreign. Unknown never authorizes retry, rollback,
continuation, or lifecycle credit.

After separate reads mint `--resume-controller <id> --boundary <provenance>
--epoch <epoch>`, then `--verify-resume-receipt`. This binds controller/claim,
HEAD/tree, STATE/ROADMAP hashes, invalidation, boundary, epoch, and Next action.
New continuity generations use `G` plus four uppercase hexadecimal digits
(`G0001`, `G000A`, `G0040`). A legacy `eNN` input is accepted only as an alias
and is canonicalised before a new receipt is minted; unchanged historical
`eNN` state and receipt records remain exact legacy evidence rather than being
rewritten in place.
`--require-current-continuity <id>` verifies the raw binding under the shared
writer gate for reconciliation and route construction; it does not by itself
authorize an ordinary governed effect. The first substantive recovered-frontier message reports the
verified receipt, controller/epoch, exact ACTIVE/READY/BLOCKED frontier and any
discrepancy. Only then may affected ordinary task narration or execution resume;
independent preparation above never earned that authority.
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
currentness writer. The marker is thereafter an immutable genesis sentinel: it
continues to bind that first pointer and receipt while a proved immediate
successor advances the current pointer and selected v3 receipt. R0011 validates
the marker's genesis join separately from the current pointer/receipt join and
never republishes or rebinds the marker during resume.

The final `implementaudit.continuity-receipt.v3` has one byte form: 18 nonempty
UTF-8 fields separated by exactly 17 tabs and terminated by exactly one LF,
with no CR, interior LF, NUL, other C0 control, or DEL. Missing/extra LF, CRLF,
trailing tabs, an extra empty field, or any forbidden byte are not receipts.
The Bash and Python owners apply this byte grammar before field semantics; raw
v3 bytes are never normalized through shell command substitution. It binds
controller, claim, bound run name,
source epoch, invalidation OID, pointer ref, pointer OID/digest, hot
STATE/ROADMAP digests, WORK_GRAPH path/digest, generation manifest OID/digest,
cold high-water, exact next action, and the immediately preceding receipt token.
Every v3 verifier derives the exact `G(n-1)` receipt ref, requires token equality,
then validates that predecessor record; a valid record aliased under any other
generation ref is not a predecessor. For a v3 predecessor, that bounded record
check also requires the exact canonical current-generation pointer ref, every
typed authority/state field, and an own-predecessor token whose ref is
structurally `G(n-2)` with a typed OID. It does not resolve `G(n-2)` or recurse
through older receipts. R0011 preserves and verifies the raw bytes after
expected-zero publication. The reader matrix is fail closed:

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
  when the marker forms an exact immutable genesis join and the selected current
  pointer/receipt schemas and every authority, pointer, hot, graph, manifest,
  high-water, predecessor, and next-action field form their exact current join.

Unknown records, mixed v2/v3 state, wrong object types, owner/run/schema drift,
or a stale pointer/receipt join are STOP. These are reader rules only: reading
does not publish, repair, delete, or otherwise update a pointer, receipt, or
migration marker.

### Cooperating protected-sink generation fence

`apply-observed-mutation.sh` treats a phase/step
`mutation-fences/phase-<phase>-step-<step>.json` as a protected-sink contract.
The current generation is never caller-selected: the helper obtains the exact
receipt token from `--require-current-continuity`, and for receipt v3 binds the
already-verified pointer ref, pointer OID/digest, receipt ref/OID and generation.
It combines that generation binding with an immutable target fingerprint made
from the authorized repository path and the supplied preimage's SHA-256 and
byte length. Operation, attempt, effect-plan, controller, generation and target
identities remain separate fields in the authority, journal and result records.

Controller bind, R0039 pointer/marker publication, and a protected mutation
share the create-exclusive absolute
`<git-common-dir>/implementaudit-r0039-publication.lock` domain. Linked
worktrees therefore cannot obtain distinct leases. The protected sink and
controller bind wait for the common lease; R0039 publication preserves its
fail-fast `R0039 publication writer lease is held` result. Read-only claim
routes called by a lease holder do not reacquire it. A divergent legacy
worktree-local lease is version skew and fails closed.

The protected sink acquires the common lease before its local namespace gate,
then takes sorted target locks, rechecks the exact controller and
pointer/receipt generation after transaction setup and all pre-effect hooks,
and performs the first protected effect without releasing the common lease.
The final check also requires the declared authority/protected generations,
verified receipt token, authorized path and target preimage to match. The sink
holds the common lease through effect, rollback/recovery, durable terminal
result, target-lock release, and local-gate release, then releases it last.
Controller bind holds it through expected-old controller CAS; R0039 holds it
through pointer or marker CAS and readback. Stale or wrong generation, wrong
controller, pointer/receipt drift, wrong target or preimage leaves the
protected target unchanged; rejections before setup report an empty
actual-effect set, while a final-boundary rejection durably records only its
transaction/control effects. A declared sink that cannot reject and report the
fence returns `UNKNOWN` / `MANUAL_RECONCILIATION`, with retry prohibited and no
terminal closure claim. This coordination covers only governed cooperating
writers; direct/raw Git and other non-cooperating writers remain outside it.

Routine v3 recovery is bounded: it reads the current pointer, hot STATE and
ROADMAP pair, `WORK_GRAPH` path/digest, selected receipt, invalidation and
marker. Historical event segments are not read. A corrupt referenced segment
therefore does not invalidate an otherwise exact routine currentness check; it
fails only when the explicit immutable-history query reads and validates that
segment. Recovery after an interrupted first publication uses a fresh R0011
invalidation/epoch and either completes the same verified pointer transaction
or publishes a proved immediate successor. A no-argument R0039 assembler may
produce an empty event delta only when the exact predecessor manifest and
unchanged high-water are retained; empty genesis remains forbidden. R0011 then
mints the successor receipt with the permanent marker still anchored to
genesis. Recovery never hydrates wholesale history or restores root-v2 after a
marker exists.

Continuity currentness does not itself authorize the next route. After the
receipt is current, load `route-obligations.md` and classify the exact boundary,
scope and action through `scripts/route-transaction.py`. The canonical result
is only `PENDING`, `NOT_REQUIRED`, or `REQUIRED`. Missing/malformed authority or
`PENDING` blocks. A scoped `NOT_REQUIRED` receipt must be rechecked immediately
before its exact action; a `REQUIRED/UNSATISFIED` record blocks until the H2B
child lifecycle returns and completes it. STATE is a projection, never the
decision authority.

Before an ordinary governed source, graph/lifecycle, dispatch, package,
release or external effect, use request-free `claim-run.sh
--require-current-route <controller> <active-binding-args>`. It derives the
current request from canonical route authority and exits zero only for exact
current `NOT_REQUIRED`, with its no-child projection, or exact current
`REQUIRED/SATISFIED` after the mapped child lifecycle and post-return
currentness. Route writers and recovery internals continue to use the raw
continuity verifier; they do not recursively call the effect gate.

Routine route recovery proves its bounded read with
`history_read_performed: false`; unrelated immutable event segments are not
enumerated or hydrated. If hot state names one exact unresolved
`iaevt-v1-<sha256>` identity, the exact `QUERY_HISTORY_THEN_RESUME` action emits
one normalized `implementaudit.history-query-request.v1` with requirement
`REQUIRED` and that identity as its sole `evidence_ids` member. R0033 records
the request but does not run or satisfy it; the later R0038 query owner performs
the selective read. A mirror/ActiveGraph satisfaction claim is reported as an
ignored observation and cannot override canonical `PENDING` or another route
state.

The H2B lifecycle is a CAS chain from `REQUIRED/UNSATISFIED` through `OPEN` and
`RETURNED` to `SATISFIED`. The exact required reason maps stale-context,
independent-review, maintainer-qualification and nontrivial-Andon work to
`audit-state`, `audit-assess`, `audit-implement` and `audit-andon`
respectively. It resolves and delivers the complete mapped child bytes and
immutable route packet, accepts only the return bound to that packet, rereads
ordinary post-return currentness (v3 uses the exact native/custody gate) and those same live bytes, semantically revalidates the
embedded artifacts against the exact original authority and current mapped
child, and records exactly one governor decision. Identical completion is
idempotent. Compaction replay uses host-bound source-event identity plus body,
kind, reactivation, and provenance rather than text equality: reconstructed
satisfied one-shot `E1` has zero effects; a host-bound distinct `E2` remains
distinct but cannot reopen a terminal target without explicit
reopen/change/invalidating evidence; missing, unreadable, malformed, unbound,
or conflicting provenance returns a typed zero-effect `ambiguous` STOP. A
still-active standing instruction continues to apply without gaining a
duplicate row.

Each transition result also projects the identity-bound visible sequence
`OPEN` → `LOAD` → `USE` → `RETURN` → `DISPOSE` → `RECONCILE`. Route state alone
proves only OPEN, canonical RETURN storage and governor RECONCILE. LOAD, USE and
DISPOSE require three exact immutable host-owned stage receipts, independently
resolved through the current store and bound to the same owner, host/session,
binding generation, child, packet, obligation and transaction; child-supplied
hashes alone establish nothing. Without that resolution the stages remain
listed as `unverified` and grant no canonical lifecycle credit. Child-bound
decisions and OPEN/RETURN/RECONCILE custody use the canonical transaction ref,
not the controller decision ref. Admission is persisted per route transaction
at OPEN. Disjoint same-controller transactions coexist; a second child in one
transaction stops, writer and dependency collisions retain distinct typed
conflict results, and identity-fenced failed-open/terminal cleanup prevents
stale conflicts.

`audit-state` NATIVE_AUTHORITATIVE_RECOVERY is downstream cognition: its ordinary native admission requires
a mechanically current receipt when stale-context reconstruction still needs
model judgement. It cannot mint the invalidation/receipt or authorise an effect.
If that boundary made an earlier `OPEN` or `RETURNED` route stale, R0033 may
supersede it only through the exact immediate continuity and H0 binding
successor described in `route-obligations.md`. The old lifecycle remains an
immutable incomplete record and grants no return, completion or satisfaction
credit to the fresh audit-state transaction.
The fresh return is accepted only as the closed
`implementaudit.audit-state-minimum-frontier-return.v1` record bound to the
exact event, consumed capsule, child, packet, obligation and transaction. It
contains the exact ordered `EVENT`, `CAPSULE`, `PACKET`, `OBLIGATION` and
`ROUTE_TRANSACTION` digest identities; closed unresolved-obligation and
contradiction references; and one closed typed edge with a digest target. It
carries `DISCARD_AFTER_RETURN`. Top-level or nested raw canonical content,
encoded JSON/YAML/Markdown, multiline or oversized scalars, aliases, foreign
references and replayed identities stop before canonical RETURN or
reconciliation.
When the governor then resolves and actually loads `audit-state`, the first
permitted route narration must include `CHILD_SKILL_ROUTE=audit-state` and a
plain-language reason for the selection. Do not emit that line for a
deterministic/governor-only recovery, package discovery, similar vocabulary, or
an intended-but-unloaded route. An ordinary route announcement before current receipt,
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

## Host-session attribution

Controller and continuity currentness remain the owners above host-event
attribution. When governed activation associates a host session with the
current object, or an admitted host event needs that attribution, load
`host-session-binding.md` and use `scripts/host-session-binding.py` against an
explicit plugin-owned or host-owned store. Bind the exact host session,
controller, claim, run, repository, Git-common directory, worktree, continuity
generation and receipts. Rebinding is expected-generation CAS.

No binding is the zero-scan cheap path: do not inspect cwd, enumerate run roots,
select a controller singleton, read target prose or child output, or execute a
validator. A stale, foreign, superseded, tombstoned, ambiguous, disabled,
untrusted or malformed binding is unavailable. R003A attribution cannot mint a
continuity receipt, satisfy a route obligation, close an object, authorise an
effect or prove native host activation. SessionEnd may tombstone attribution;
it cannot close the governed object.

### Codex compact actuator

The canonical plugin's default `hooks/hooks.json` matches only
`SessionStart(source=compact)` and invokes
`scripts/codex-compact-interlock.py`. The adapter owns the fixed lower-case
namespace `codex`, takes only the host-supplied `session_id`, and derives the
one existing H0 store as the fixed versioned child
`PLUGIN_DATA/host-session-binding-v1`. It never accepts a store, controller,
run, repository or executable path from the event or caller.

`startup`, `resume`, and `clear` are no-effect hook responses. A compact signal
is retained by the independent pending owner above before the unchanged native
validation/invalidation path. Absent H0 is still the zero-scan native non-trigger
and does not create the store; missing custody does not suppress audit-state. A present binding is
validated against the exact live controller/claim/run and its applicable
continuity receipt, then the deterministic compact event is sent through the
same atomic `--invalidate-continuity` path with `host-reported-compaction`.
Success returns hook JSON with `continue:false`, so Codex ends the turn before
another model request. Duplicate delivery of the same bound boundary returns
the same invalidation; a successor binding/receipt derives a distinct event.

Missing `PLUGIN_DATA`, malformed input, or disabled, untrusted, inaccessible,
ambiguous, stale, foreign, superseded, tombstoned or mismatched binding state
returns a fail-closed stop without guessing. Event `cwd`, transcript, target
prose, ambient PATH, newest-run and controller enumeration are not authority.
The hook records nonauthorizing pending signals and reads/validates/invalidates; it cannot initialise or bind H0,
resume, mint a continuity receipt, invoke a child skill or route transaction,
advance lifecycle, or close work. Source/package tests prove only the adapter
and archive projection; installed, enabled, trusted-definition and fired-event
proof remain separate host evidence.

## Turn disposition after attribution

R003A attribution identifies the governed object but does not decide whether a
host turn may end. The host-neutral core is
`scripts/evaluate-turn-disposition.py`: it strictly decodes one request, binds
the exact `validate-event` correlation to the explicit run root, consumes the
current `route-transaction.py check` result, and verifies the claimed closure,
audited handoff, or nonterminal-yield evidence already owned by STATE and the
run-root validator. An in-scope `REQUIRED/UNSATISFIED` obligation blocks; STATE
projection alone cannot satisfy it.

No active audit object is the only zero-object cheap path and performs no
binding, route, or run-root scan. A valid nonterminal yield retains the existing
lifecycle state, records a durable Next action, and emits no terminal/handoff
marker. The evaluator creates no receipt, route decision, closure, lifecycle
state, package/install evidence, or host-activation claim.

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


## Prospective native authoritative recovery attempt and refusal contract

Prospective R0033/R0037 recovery attempts and refusal

This NATIVE_AUTHORITATIVE_RECOVERY amendment applies only under the newly qualified source/package pins. It
does not change the rule under which any old capsule, OPEN or worker ran. Keep
all historical misses, source pins, old immutable records, actual outputs and
one-use custody. Existing v2 currentness and ordinary effect gates are unchanged.
New native-attempt custody uses implementaudit.post-compaction-recovery.v4 and
R0033.recovery-cognition.v2 within the existing transaction container. Its
successful child return is implementaudit.audit-state-minimum-frontier-return.v2.
Historical v2/v3 capsules and v1 frontier returns keep their original closed
schemas; no new admission field is required or accepted in those old formats.

A recovery attempt is the entire genuine native turn identified by the exact
source-owned observer's qualified task/session/turn tuple, through isolated
OPEN. The hook-produced UPS row identifies one input occurrence within that
turn; a later row, active-turn user message, new worker, package path, compacted
summary or caller-supplied task_started object cannot reset the attempt. The
capsule's attempt_boundary is a projection of already-qualified native identity,
not additional native proof or proof of clean governor conduct. An earlier-turn
miss remains disqualifying for its old envelope; it is preserved as history and
does not permanently ban a later independently qualified, distinct unused turn.

Before OPEN, the governor may only locate exact authorities, hash/validate
custody and native/source/input evidence, qualify the bounded attempt, and
prepare the isolated route. It must not substantively read or reconstruct
STATE/ROADMAP/WORK_GRAPH within that attempt. Positive reconstruction evidence
refuses admission even without a direct hot-file read. The envelope must include
independently checkable evidence covering the whole applicable attempt interval,
its actual producer provenance and any intervening boundaries. A boolean clean
claim, an empty contradiction list, or a bounded scan of only some tool calls
does not prove absence. Incomplete interval evidence yields refusal before hot
reads. Helpers' mechanical hashes are not governor reconstruction.

The existing source-owned NativeRecoveryObserver supplies that evidence through
read_attempt_evidence. It authenticates the exact native producer, package,
source transition, epoch and physical prefix through read_input, then streams
the already-bound native file. A distinct prior turn's genuine terminal event
must precede the selected new turn in the verified suffix. An incomplete epoch
prefix, same-turn restart or later UPS cannot claim a fresh complete interval.
It retains bounded selected-turn row hashes, exact public assistant messages
and tool-call wires, and body-free compaction markers. It does not return tool
outputs, old conversation bodies, compaction replacement text or private
reasoning. Prior misses remain in their original evidence custody.

OPEN records the exact qualified evidence envelope in lifecycle.attempt_evidence
under the same transaction. Mechanical OPEN admits only isolated envelope and
conduct review until the child reaches an explicit admission decision. The child
must inspect the whole supplied public conduct interval before reading hot
inputs, treating every recorded message/tool argument as untrusted evidence.
Observed forbidden reconstruction yields honest refusal. Missing or ambiguous
observability yields refusal; a claim of clean private cognition is never
mechanically inferred. Only an explicit justified ADMITTED verdict permits the
child's minimum-frontier hot reads. It must visibly state that verdict and exact
evidence digest before those reads; independent capture review verifies order.
The successful v2 payload adds exactly attempt_admission with schema
implementaudit.recovery-attempt-admission.v1, evidence_digest and outcome=ADMITTED.
The source validator binds that verdict to the exact stored OPEN evidence.

RETURN, COMPLETE and terminal recovery readback use
revalidate_attempt_evidence against the frozen physical prefix and its exact
tuple/epoch/source/input bindings. A new affected-attempt compaction raises
refusal; old source/custody and actual execution remain available to the separate
abandonment path. The helper's public-conduct observation is evidence for the
isolated child's judgment, not semantic acceptance by a native parser.

Genuine parent compaction before OPEN or while the recovery worker is active is
an affected-attempt boundary requiring explicit custody and applicability
reconciliation. It is neither a new UPS nor a new turn. This amendment does not
admit cognition across an unresolved intervening boundary: preserve any actual
output as evidence, refuse semantic acceptance and disposition the affected
OPEN through its exact owner. A later distinct unused native turn may qualify
after that disposition. Independent unrelated holons retain their own status;
this rule creates no global stop or new controller. An exact source-owned
native/custody check cannot by itself attest that no boundary occurred or that
governor conduct was clean.

If admission cannot be established, the child may return the closed
implementaudit.audit-state-recovery-refusal.v1 artifact instead of fabricating
a minimum frontier, contradiction digest, STOP target or canonical_reconciliation
proposal. Bind event, capsule, packet, obligation and transaction digests; use
one of the exact source reason codes and bounded existing evidence digests.
Context disposition remains DISCARD_AFTER_RETURN. This artifact records refusal
only; it is not successful R0033 RETURN and cannot enter ordinary COMPLETE.
Truthful host-owned LOAD/USE/DISPOSE evidence stays separate from acceptance.

The new abandon-recovery owner handles only exact consumed unaccepted OPEN or
RETURNED recovery records. Its independently reviewed disposition plan binds
the old OID/identity, transaction, capsule, admission identity, factual evidence
bytes, reviewed native source-transition specification and exact successor
package/child. It rehashes retained original source pins without executing those
old bytes; it does not substitute successor source for original source. Before
installation removes an old cache, retain those exact old source members in an
independently reviewed custody root. The disposition may bind that absolute
preserved_source_root; all old pins must rehash there while original record path
identities stay unchanged. If exact retained bytes are unavailable, stop for
source-custody repair. Future source
comparison must explicitly include the admission-contract deltas; neither the
plan digest nor its review-subject field authenticates its own review.

Under the existing route namespace gate, the owner freshly checks exact claim,
H0 correlation, original invalidation/subject/ref/hot-input custody, old native
occurrence, retained old sources, executing successor sources and unchanged
one-use bytes. It independently resolves actual LOAD/USE/DISPOSE stage receipts
before releasing a running worker's admission. Abandonment with no provable
execution/disposal is deliberately unavailable in this bounded variant; retain
admission and stop, without inventing stage events or inferring disposal.

Expected-old CAS publishes ABANDONED on the same transaction ref. The successor
keeps the entire original lifecycle unchanged and adds a typed nonacceptance
disposition plus predecessor link. It retains old source/package/capsule fields;
new source identity is separately named in the disposition. After exact terminal
readback and repeated proof, only the matched admission changes to TERMINAL.
The consumed invocation is never deleted or reopened. ABANDONED grants no
cognition, currentness, ordinary effect, state publication or closure credit.

CAS uncertainty or proof drift never permits release, rollback or blind retry.
An interrupted post-CAS cleanup may continue only when the exact expected old
record and exact candidate terminal are freshly revalidated under the same
reviewed disposition. Different disposition, foreign terminal, double-abandon
of a terminal as though it were a new OPEN, stale CAS and mismatched ownership
refuse. Admission cleanup is idempotent under its existing identity fence.

After independent review, qualification, supported installation and lawful old
OPEN disposition, wait for the current task's actual turn to finish. Only then
may a new ordinary user message provide a prospective input. The native owner
must independently prove the new tuple is distinct and unused; message delivery
alone is not proof. No capsule, turn, event or worker credit may be reused.

Acceptance burden: source/package/install readbacks, complete qualified attempt
interval and boundary evidence, isolated no-pre-read child behavior, exact
native/H0/source/one-use comparisons, truthful stage receipts, terminal CAS and
admission readback all remain separate. Pure tests and this source preparation
do not satisfy those native or installed obligations.

## Repaired native carrier coverage and historical evidence

Prospective native attempt evidence v2 distinguishes source-framed incoming
AgentMessage input from unqualified conduct carriers. Within the authenticated
native task/turn prefix, a closed native
inter_agent_communication_metadata(trigger_turn:boolean) row must immediately
precede its associated AgentMessage at the next ordinal. The message must have
the source-stamped turn/time/id and exact bounded native plaintext or encrypted
envelope framing, with no caller-authored envelope metadata. The paired body is
excluded whether plaintext or encrypted; only row identities and a typed incoming
descriptor survive. Author/recipient labels establish no task identity, public
visibility, or governor conduct. Ambiguous/unpaired carriers refuse the affected
completeness assertion with a body-free row identity. Properly paired incoming
input is not blanket-refused, decrypted or promoted to public conduct.

The evidence radius is host-visible messages/calls and explicit incoming or
capability context, not private cognition or all capability-change semantics.
additional_tools is validated as bounded source-shaped capability context and
recorded only by descriptor/digest, with no invocation claim or schema exposure.
Unsupported durable compaction_trigger and Other/unrecognized response items
refuse coverage without inventing a compaction event. Genuine compact markers,
including response_item/context_compaction, retain their separate boundary rule.
Initial admission classifies the selected attempt. Retained-OPEN revalidation
rehashes and recomputes frozen v2 evidence, then applies source-pair and coverage
checks to the later same-parent interval; a later turn cannot hide an unresolved
boundary or unknown coverage. These refusals affect that retained OPEN, not other
tasks. Existing private-reasoning/tool-output exclusion and byte/row ceilings
remain; excess or incomplete evidence refuses rather than truncating.

Inner native evidence v2 adds closed incoming_inputs and capability_context
fields. Historical inner v1 remains exactly shape-readable; repaired live
admission produces v2 and live revalidation refuses v1 before invoking the native
reader. No historical v1 evidence is retrospectively credited with this repair.
The outer route envelope/version remains owned by the source integration owner.

All pure evidence retains UNQUALIFIED_WITHOUT_AUTHENTICATED_CALLER. The existing
authenticated observer, source/epoch/native/caller/custody and owner gates remain
mandatory; supplied rows or matching JSON digests do not authenticate a producer.
The pinned reference sources explain the carrier grammar and producer path;
they do not establish running-binary equivalence or actual native emission.
