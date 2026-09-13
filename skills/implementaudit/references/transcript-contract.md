# Transcript Contract

Use this reference when a host, wrapper, or `/goal` evaluator needs to inspect
ImplementAudit transcript state without reading the full skill.

## Native integration support reference

The transcript contract supports native audit-object integration by making
read-only audit-object closure boundaries, repo-content-as-data security handling, branch/diff scope,
execute/review decisions, and reconciliation visible to host evaluators. The
primary integration contracts live in `audit-category-matrix.md` and
`plan-lifecycle.md`; transcript markers prove those contracts reached terminal
audit-object state.

The transcript contract is an execution boundary. It is not a release,
publication, provenance, install, Graphify indexing, or ActiveGraph export
claim.

The transcript records audit object lifecycle state. The `tdqyq-audit-object`
is the evidence-bearing record for the run: input, ledger, phase artifacts,
owner/source decisions, checks, Andons, handoffs, and terminal verification
state. `ydqyq-audit-action` operations may happen repeatedly, but the run closes
only when marker state proves the audit object reached terminal verified
closure.

For release-affecting, multi-phase, package-boundary, provenance, or public-claim
work, the transcript must preserve the double-audit sequence:

```text
AUDIT_START          -> creates or normalizes the tdqyq-audit-object
ydqyq-audit-action   -> acts against that object before mutation or handoff
AUDIT_VERIFY         -> checks object state against evidence
AUDIT_COMPLETE       -> terminal verified closure of the object
```

## RC self-dogfood evidence contract

Only exact RC/self-release `SELF_DOGFOOD_TRIGGER` loads this;
`ORDINARY_IMPLEMENTAUDIT_CONTROL` loads no dogfood owner/broker/schema. Runner
creates a temporary `CODEX_HOME`, binds candidate commit, candidate tree, package SHA-256, and installed runtime SHA-256, and isolates context/journal/key from model roots; an event cannot qualify itself. Repo-only broker is the runner-owned action boundary, never installed/ordinary I/O.

`implementaudit.dogfood-event.v1` records session, monotonically increasing sequence, unique sequence/correlation/event identity, previous event identity, actor/action/role/phase/result, target/content identity, and an HMAC produced with runner custody unavailable to the audited model. Validation fails closed on a missing event/action, duplicate/reorder, broken chain, invalid HMAC/schema, blocked/ambiguous result, pre-baseline/real-home read, or identity mismatch. Order: trigger -> contract/broker/schema -> successful machine-readable clean status/HEAD/HEAD^{tree} -> temp activation -> targeted read/search; independent corroboration reruns those fixed Git observations against the runner-bound source root.

Typed runner events are the primary semantic evidence, not sole authority; transcript remains independently parsed adversarial corroboration. Require bijective correlations and equal action facts; mismatch is `Andon: typed dogfood evidence contradicts independent observation`.

Host activation is not readback. Read only owners; prove package/checksum/install parity. Real-home installed skill readback is non-evidence; later temp proof cannot cure it. Policy rejection blocks; never bypass policy, use real home/broad globs, or weaken proof.

## Planner markers

Planner markers appear before a user starts a generated `/goal` handoff.
They are emitted by Stage 6 and Stage 6.ii of the native IMPLEMENTAUDIT planner.

```text
Self-critique:
PREFLIGHT_GREEN
PREFLIGHT_RED
```

- `Self-critique:` records the Stage 6 plan-review result.
- `PREFLIGHT_GREEN` means the deduplicated mandatory checks passed before
  dispatching a generated handoff.
- `PREFLIGHT_RED` means the pre-flight check failed or needs owner review.
- `PREFLIGHT_RED` is not a bypass. It must classify the failed baseline as
  target, unrelated, or unclear before any handoff or mutation continues.

## Stage handoff boundary

When Stage 7 prints a ready-to-paste `/goal`, the handoff is valid only if it
names the runtime protocol, sequential phase execution, final audit before
completion, and the handoff/failure exclusion rules. If the current session is
already inside `/goal using /implementaudit ...`, no second `/goal` should be
printed.

## Phase markers

Phase-loop markers appear in this order for each executed phase:

```text
IMPLEMENTAUDIT_PHASE_START
IMPLEMENTAUDIT_PHASE_VERIFY
AGENTS_UPDATE_DECISION
IMPLEMENTAUDIT_PHASE_DONE
```

- `IMPLEMENTAUDIT_PHASE_START` opens the phase and names the owner/source.
- `IMPLEMENTAUDIT_PHASE_VERIFY` records criteria, checks, evidence type, and
  cleanliness readback.
- `AGENTS_UPDATE_DECISION` states whether a durable repo-local rule was added,
  not warranted, or requires owner decision.
- `CONTINUITY_DECISION`, when printed, states whether a non-obvious learning
  warrants a bounded repo-local rule, memory note, deferral, or no writeback.
  It does not replace `AGENTS_UPDATE_DECISION`.
- `IMPLEMENTAUDIT_PHASE_DONE` closes the phase.

## Andon escalation markers

```text
ANDON_PROBE
ANDON_ESCALATE
ANDON_HANDOFF
```

Andon escalation implements Jidoka: abnormality -> stop -> understand why ->
countermeasure -> rerun evidence. The sequence is ordered: ANDON_PROBE →
ANDON_ESCALATE → ANDON_HANDOFF. Skipping to ANDON_HANDOFF on the first
abnormality is invalid. Escalation is driven by repeated same-class failure
and blocked closure, not by a try counter. There is no arbitrary three-try or
three-round cap.

Every Andon event is recorded as one classed row in the run-root STATE.md
`## Andon log` (`# | Occ | Phase | Class | Abnormality | Countermeasure |
Rerun evidence | Outcome`). One class per row; one or more linked rows per
occurrence: an occurrence carrying several independent defects records one
row per class sharing the same `Occ` id, so co-occurring defects stay
linked while per-class recurrence citation is unchanged. Legacy run roots
using the previous table shape (no `Occ` column) remain valid and resume
safely. `Class` is exactly one official abnormality class:

```text
failed-criterion
regression
hung-command
substituted-command
owner-unclear
generated-artifact-mismatch
stale-sidecar
policy-conflict
impossible-criterion
evidence-mismatch
transport-infrastructure
misplacement
false-closure
```

Definitions and boundaries for the three environment/accounting classes:

- `transport-infrastructure` — environment-level failure: network outage
  windows, process-initialization exit codes (e.g. 0xC0000142), host
  resource loss, or simultaneous failures across independent lanes.
  Boundary vs `hung-command`: `hung-command` is a single command failing to
  return/progress on an otherwise healthy, responsive host; discriminating
  evidence for infra is cross-lane simultaneity, OS-level init/exit
  signatures, or a known outage window. A failure of the REVIEW/ADVISORY
  CHANNEL itself (e.g. a platform-side filter blocking an authorized
  reviewer before any verdict) is `transport-infrastructure`, never
  evidence about the reviewed tree: preserve the non-verdict, reissue to
  the SAME authorized reviewer identity with a narrowed prompt, and never
  treat a blocked review as an accept or a reject.
- Resource exhaustion is `Class: transport-infrastructure | Blocker:
  resource-exhausted`. Label `reported_reset` `ADVISORY`; set `next_probe_at =
  min(reported_reset, backoff_probe_at)` and run a cheap capacity probe then.
  Success resumes early; only a recorded failed probe supports `blocked`.
- Supervision overrun is `Class: hung-command | Blocker:
  supervision-overrun (poll_budget N exceeded)`. Neither discriminator is a
  new class token.
- `misplacement` — right layer, wrong INSTANCE: a correct finding or fix
  attached to the wrong copy, version, file, component, or occurrence.
  Boundary vs `generated-artifact-mismatch`: that class is the wrong LAYER
  of a generator relationship (patching generated output instead of the
  source owner, or attributing generated state to source).
- `false-closure` — the closure-state ACCOUNTING is wrong: a completion
  claim collapses unresolved / unvalidated / deferred / transferred /
  risk-accepted items into "fully resolved", even when every individually
  cited piece of evidence is genuine. Boundary vs `evidence-mismatch`:
  that class is one specific claim whose cited evidence does not support
  it.

Boundary fixtures (expected classification + rationale):

| Fixture | Expected class | Rationale |
| --- | --- | --- |
| Adapter exits 0xC0000142 during a known network outage; sibling lane fails in the same window | `transport-infrastructure` | environment-level signature + cross-lane simultaneity, not a single stalled command |
| One `grep` never returns on a responsive host; siblings unaffected | `hung-command` | process-level stall in a healthy environment |
| Fix applied to the deployed copy while the source copy still carries the defect | `misplacement` | right layer (source-owned pair), wrong instance/copy |
| Patch written into a generated bundle instead of its source owner | `generated-artifact-mismatch` | wrong layer of a generator relationship |
| Run declared "fully resolved" while two ledger rows are risk-accepted and one is transferred | `false-closure` | closure accounting collapsed non-resolved states |
| A claim cites a passing test that does not cover the claimed behavior | `evidence-mismatch` | one claim, unsupporting evidence |
| Authorized reviewer returns no verdict (transient channel failure: rate limit, 5xx, or interruption) | `transport-infrastructure` | review-channel failure; preserve non-verdict and reissue the allowed packet to a fresh reviewer context |
| Authorized reviewer returns no verdict (content-deterministic refusal: provider policy or schema rejection caused by packet text) | `transport-infrastructure` | review-channel failure; preserve non-verdict, record the origin, and do not reissue an unaltered packet — alter scope or wording first |

Same-class recurrence — not a try count — is what drives escalation. The log
has no row limit.

These markers and classes apply to any governed run, phased or not. When no
run root exists (direct in-session governance), the Markdown findings ledger
serves as the Andon log substrate: record the abnormality class on the ledger
row and cite prior same-class rows on escalation. The source-repo checker
applies the recurrence rule to that substrate with
`validate-run-root.sh --ledger <markdown-ledger>`.

- **ANDON_PROBE**: emitted on the first abnormality of any class above. It
  must record: the abnormality and its class; the failing criterion, command,
  or artifact; owner/source; containment decision; a 5 Whys root-cause drill
  proportional to the issue; Hansei (gap, cause, countermeasure, follow-up
  evidence); the countermeasure selected; and the rerun evidence required.
  The classed `## Andon log` row is appended and STATE.md is updated. A fix
  may not be attempted merely because a symptom is visible; the fix must
  follow from the probe. If the countermeasure passes its rerun evidence, the
  phase resumes; no new marker is needed.

- **ANDON_ESCALATE**: emitted when the first countermeasure fails, the
  same-class abnormality recurs, the root cause remains unclear, the fix would
  expand scope, or the owner/source is disputed. A same-class recurrence claim
  must cite the prior same-class `## Andon log` rows by `#`; a recurrence
  claim without a cited same-class row is invalid. It must record: the prior
  ANDON_PROBE history; why the first countermeasure failed; a revised or
  deeper 5 Whys; `New evidence:` and/or `Changed approach:` — if neither can
  be truthfully filled, evaluate the ANDON_HANDOFF conditions instead of
  escalating; the chosen path — split, reframe, rollback, owner decision,
  or a bounded fix-spec (`phase-N.fix.md` targeting only the failing
  criterion, no scope expansion, ending with the original VERIFY gate); and
  rerun evidence. On success, the phase resumes from
  IMPLEMENTAUDIT_PHASE_VERIFY. Escalation may repeat with new evidence;
  repeating it without new evidence or progress routes to the ANDON_HANDOFF
  conditions. When three distinct linked occurrences share one class and the
  last two repairs name the same `owner/source=<path>` in their Countermeasure
  cells, append a `Mechanism-replacement decision:` after the last triggering
  row and before closure. The accepted decisions are `replace-mechanism
  (<what>)`, `continue (<justification>)`, and
  `escalate-to-convergence-mode (<shared invariant>)`; none stops another
  bounded repair.

- **ANDON_HANDOFF**: emitted only when closure is blocked by an owner
  decision, unsafe scope, missing authorization, an external dependency,
  irreproducibility, a missing required tool or access, or when no bounded
  countermeasure remains. It is not "third try failed." Includes the full
  probe and escalation history, the remaining blocker, and the smallest next
  concrete action for a human owner. STATE.md set to BLOCKED. Phase done with
  `Status: blocked`. Phases that depend on the blocked surface do not execute;
  independent in-scope phases may continue when safe, and the run ends in an
  audited handoff rather than completion.

`ANDON_HANDOFF` is terminal for the blocked surface. A transcript containing
`ANDON_HANDOFF` must not also contain `IMPLEMENTAUDIT_RUN_COMPLETE`.
STATE.md `Status: BLOCKED` must be set before the run stops or hands off.
Legacy transcripts may contain the older FAILURE-prefixed marker spellings;
hosts must apply the same exclusivity rule to them, but new runs emit only the
ANDON-prefixed markers.

## Interruption and continuity markers

```text
IMPLEMENTAUDIT_PAUSE
IMPLEMENTAUDIT_CONTINUITY_SAVED
```

- `IMPLEMENTAUDIT_PAUSE` is emitted when a user message interrupts a phase in
  progress (after IMPLEMENTAUDIT_PHASE_START, before IMPLEMENTAUDIT_PHASE_DONE).
  It records: phase number, paused-at-boundary or paused-mid-step, last
  completed step, and whether STATE.md was updated. A transcript containing
  IMPLEMENTAUDIT_PAUSE must contain a preceding IMPLEMENTAUDIT_PHASE_START.
  Resume follows the run-root PROTOCOL.md resume contract: re-read state and
  spec from disk, re-validate the phase spec, and continue from the paused
  step without re-printing IMPLEMENTAUDIT_PHASE_START.
- `IMPLEMENTAUDIT_CONTINUITY_SAVED` is emitted only when a bounded continuity
  writeback is actually performed (SKILL.md Stage 0; PROTOCOL.md continuity
  steps). It must carry all six fields: Target, Reason, Evidence, Boundary,
  Authorization, Not saved. Saved continuity never overrides live files,
  AGENTS.md, Smoke A/B evidence, or the final audit.

Neither marker is a completion or handoff signal; both may appear in
transcripts that later reach AUDIT_COMPLETE or an audited handoff.

## Host-turn disposition

A host turn may end only as no active audit object, valid terminal closure,
valid audited handoff, or valid nonterminal yield. These are disposition
classes, not lifecycle states. `scripts/evaluate-turn-disposition.py` consumes
the exact current R003A attribution result, its correlation inputs, the current
R0033 check result, and the bound run root. Stale, ambiguous, foreign, or
malformed attribution and `PENDING` or `REQUIRED/UNSATISFIED` route state block.

A nonterminal yield retains one existing STATE status (`open`,
`READY_TO_DISPATCH`, `IN_PHASE`, `PAUSED`, `BLOCKED`, or `INTERRUPTED`) and
durable continuation evidence. It emits no terminal or handoff marker. Bare
abandonment is therefore invalid, while progress, a question, or a bounded
wait with a recorded Next action remains allowable. No-active-object is the
only path that omits binding, route, and run-root reads. Source classification
is not actual host activation evidence; HC-H7B or another separately qualified
adapter remains responsible for host translation and firing claims.

Context-epoch continuity (#35) deliberately introduces NO new marker: a
continuity boundary is recorded as a new epoch row in STATE.md `## Context
epochs and instruction applicability` (provenance exactly one of
`host-reported-compaction` / `new-session` / `handoff-resume` /
`manual-resume` / `inferred-context-gap`). Reconciliation precedes affected
authority-sensitive repository effects (PROTOCOL.md §Continuity boundaries;
`references/continuity.md`). An affected mutation without its currentness or
reconciliation, or replay of a `satisfied` one-shot, violates this contract even
when markers are ordered. Preserve the exact existing invalidation occurrence;
this wording does not require another event for the same boundary.

The first substantive recovered-frontier assistant message is the verified
continuity receipt/current-frontier report. Waiting on or terminating a process
whose authority or inputs depend on that recovery is containment, not restored
authority. A new affected command, check, state write, package effect or commit
before required recovery/currentness is a violation. Separately admitted
unchanged-input sibling preparation may continue only on its own already-valid
scope, authority and containment basis under `continuity.md`; unknown
independence blocks that task. This exception permits no pre-OPEN substantive
STATE/ROADMAP/WORK_GRAPH reconstruction, canonical effect, borrowed currentness
or acceptance. Buffer its products and revalidate them at the consuming JOIN.
P0 recovery priority is not a global compute mutex. A remembered standing
constraint remains binding but cannot become the frontier from stale context.

## Child-skill routing observability

Pre-action selection is required separately by `child-agents.md` before actual
load. It uses CHILD_SKILL_SELECTED and never claims verified LOAD or a
CHILD_SKILL_ROUTE; the verified route narration below still waits for real LOAD.

### Generic full-skill LOAD

This generic form is for independently required compaction or direct cognition
outside actual native delivery, when no native READY tuple exists. Actual full
selected skill LOAD and prospective visible parent acknowledgement are required
before bounded use. It grants no native delivery, host-stage, currentness, epoch,
recovery, lifecycle, mutation, release or closure authority and cannot release
actual native USE. Missing currentness, epoch or native qualification does not
block the independently required bounded entry.

```ini
CHILD_TASK=<id>
CHILD_SKILL_ROUTE=<selected-child>
LOAD=VERIFIED
```

I'm using the `<CHILD_TASK>` holon with the `<CHILD_SKILL_ROUTE>` skill to <bounded reason for this route>.

### Actual native delivery

This native form applies only to actual native delivery after independently
verified full selected skill LOAD. WORKER_TASK and LOAD_READY_SHA256 must bind
the true native worker and complete READY record. The generic form never
satisfies native readiness, liveness, ACK, same-worker USE or host-stage proof.
All existing native qualification, admission and result-authority gates remain
required in this context.

A governed child route is user-visible only after the exact package gate,
resolver selection, and actual full child load have occurred. Follow the event form
in `child-agents.md`: one literal `ini` block, then its bounded named sentence.
The verified route event is separate from the earlier OPEN/LOAD=UNVERIFIED event:

```ini
CHILD_TASK=<id>
CHILD_SKILL_ROUTE=<selected-child>
LOAD=VERIFIED
WORKER_TASK=<actual worker>
LOAD_READY_SHA256=<full READY digest>
```

I'm using the `<CHILD_TASK>` holon with the `<CHILD_SKILL_ROUTE>` skill to <bounded reason for this route>.

The selected child is exactly one of `audit-state`, `audit-assess`,
`audit-implement`, or `audit-andon`, and the announced identity must equal the
resolved and loaded child. Child files merely being packaged or discoverable,
or governor reasoning producing similar words or conclusions, is not a route.
Those governor-only cases emit no selected-child announcement. Exact current
`NOT_REQUIRED` instead emits the explicit no-child projection:

```ini
PARENT_HOLON=<parent>
CONSUMING_FRONTIER=<exact frontier>
CHILD_SKILL_ROUTE=NOT_REQUIRED
```

The `<PARENT_HOLON>` parent uses no internal child at `<CONSUMING_FRONTIER>` because the exact current R0033 route is NOT_REQUIRED.

That branch performs no resolver, load, OPEN, return or completion. An actual child load
without the announcement, an announcement without a load, a mismatched child,
duplicate child announcements, or a retroactive announcement is a routing
observability failure; none creates authority or closure.

The visible identity-bound lifecycle is exactly `OPEN` → `LOAD` → `USE` →
`RETURN` → `DISPOSE` → `RECONCILE` for all four governed holons. RETURN and
DISPOSE do not create canonical credit: only the governor's one exact
reconciliation plus post-return currentness completes the sequence. Every
stage remains bound to the same child, obligation and route transaction.
OPEN/RETURN/RECONCILE route state must not be used to infer LOAD, USE or
DISPOSE: those three stages require exact immutable host-owned receipts,
independently resolved to the current host/session, child, packet, obligation
and route transaction. Child-supplied hashes do not suffice, and the
transcript/result must name every missing stage as `unverified`.

For ordinary continuity boundaries, the verified receipt precedes the
`audit-state` load and its first permitted route narration. For explicitly
selected source-qualified v3 recovery and its prospective v4 successor only,
the ordinary receipt/currentness clauses in this transcript use the exact
native/custody substitution in `continuity.md` and `route-obligations.md`,
including required post-return revalidation. Preserve v4's additional qualified
attempt-evidence and child-admission requirements before hot reads; a version
label does not admit a route. Actual OPEN and verified LOAD permit only the
bounded recovery announcement, not ordinary currentness, next-task effects or
recovery acceptance. The separate state/publication/receipt/H0 owners must
still establish ordinary currentness before ordinary re-entry. The actual-LOAD,
matching parent announcement and acknowledged same-worker USE-release contract
remains unchanged. Other audit-* children retain their ordinary currentness
gates; no old execution or late announcement gains retrospective credit.

Verification inside a child may report an already-known cheap deterministic failure;
after return, the governor may handle that result without another model child.
If verification establishes that a new constraint defeats the selected countermeasure
and materially changes the warranted response, the active child returns to the
governor, the governor re-derives current state, and only then may it select and load a
fresh `audit-andon` route. If that diagnosis warrants another bounded repair,
`audit-andon` returns to the governor before a fresh `audit-implement` route. A direct
child-to-child transition is a routing failure.

The host event supplies exactly one closed
`implementaudit.host-abnormality-classification.v1` record bound to that Stop
event. It classifies the turn as `NONE`, `MECHANICAL` or `SUBSTANTIVE`; Stop
does not lexically infer semantic completeness from assistant prose. The
packaged standard Stop hook currently has no trusted producer for the record,
so an ordinary installed Stop event remains `UNCLASSIFIED` and
non-authorizing. `NONE`
and deterministic stop, containment, preservation, rehash or known
countermeasure execution remain cheap. `SUBSTANTIVE` is admitted only after a
fresh reconciled `audit-andon` route. Missing, mixed-shaped, stale, foreign or
unsupported classification is non-authorizing, as is `SUBSTANTIVE` without the
current identity-bound lifecycle. A governed child requester always returns to
the governor and is rejected by the live dispatch gate.

### Isolated qualification presentation

Separately authorized transport qualification uses the exact source-owned
`ISOLATED_QUALIFICATION` purpose, a null `selected_child`, and a stable
`logical_task`. It is not a governed route, skill invocation, OPEN, assessment,
adoption or currentness result. Its actual READY carries that same purpose and
the existing exact source, worker/PID/birth, LOAD and raw-prefix identities.

The shared/native formatter emits an `ini` qualification block with those
identities and the full READY digest, followed by one bounded named sentence.
It emits no `CHILD_SKILL_ROUTE` or skill-USE declaration. The bound isolated
parent consumer verifies the actual parent row and ACK in that mode only;
normal governed presentation cannot release isolated USE, and qualification
presentation cannot satisfy governed admission. Missing or inconsistent mode
bindings refuse. Discriminators and explicit CLI calls grant no effect authority.
Normal governed marker, route/currentness, source and admission requirements
remain unchanged. Future evidence must come from actual execution.

### LOAD visibility before USE

The governed dispatch consumer must hold substantive USE until verified actual
LOAD has reached the parent governor, the governor has emitted the one matching
announcement above in its own assistant transcript, and the supported transport
has acknowledged that exact presentation before releasing the same worker.
Bind this ordering in the existing task/route custody: parent identity, worker
and process/context identity, executing package and selected-child source,
OPEN, packet, obligation, transaction, applicable host/session generation,
LOAD evidence locator/digest, and the actual parent-message locator/digest.
The acknowledgement is presentation sequencing, never admission, currentness,
a host-stage receipt or a new lifecycle state. A typed claim or echoed marker
does not establish the parent's actual message or its timing.

Use a qualified LOAD-only phase or supported equivalent that exposes exact
source/delivery witnesses, relays their independently verified LOAD evidence
promptly, and withholds substantive input use pending acknowledgement. Where
the route requires host-owned LOAD receipt resolution, perform that existing
stage-owner check; a raw prefix is not a receipt. Readiness is nonterminal
transport evidence, not the child's semantic RETURN. USE and DISPOSE remain
unverified. A second transport turn may continue the same fresh isolated task
only with unchanged bound identity and applicable gates; it is not a second
child, fresh route or permission to reuse an older worker context.

If the selected channel cannot hold USE, or the exact child's loaded contract
cannot honor this phase, hold that automated governed path as unsupported.
Do not deliver an immediate full-cognition prompt and rely on later polling.
Timeout, parent loss, uncertain acknowledgement, a conflicting duplicate or
identity drift requires exact partial-effect reconciliation and containment.
An exact transport replay may resolve idempotently; it may never emit a second
announcement or launch USE twice. USE before announcement/acknowledgement is
an observability failure even if execution, later receipts or RETURN succeed;
preserve the facts without backdating, replay or retrospective credit.

R0033 presentation/lifecycle and R0036 dispatch/custody acceptance must bind the
actual consumer to seven controls: hidden, noLOAD, wrongID, duplicate and
retroactive refuse; correct ordered same-worker release passes this boundary;
ordinarynoannouncement passes without a selected audit-* marker. Ordinary work
retains its existing task visibility and any genuinely current NOT_REQUIRED
projection. No new specialist trigger or ordinary-task acknowledgement gate
is created. Source clauses, fixtures and helper checks do not establish these
actual host/model/parent-presentation controls or semantic acceptance.

## Final audit markers

```text
AUDIT_START
AUDIT_VERIFY
AUDIT_GAPS
AUDIT_WARNING
AUDIT_COMPLETE
AUDIT_HANDOFF
IMPLEMENTAUDIT_RUN_COMPLETE
```

Rules:

- Emit each final audit marker exactly once per run.
  Do not replay a completion marker in a later summary or final response. Once
  emitted at its transition, later prose may describe the state but must not
  print that marker again.
- `AUDIT_START` carries `Skill version:` — the package identity version of the
  payload that produced the run, resolved by
  `scripts/detect-env.sh --package-version` across canonical-plugin,
  standalone-compatibility, or source layouts. Contradictory/malformed package
  identities stop the gate; `unknown` is reserved for an unresolvable identity
  or unavailable JSON-capable interpreter and is never guessed. This keeps the
  transcript attributable without making a host manifest the semantic owner.
- `AUDIT_COMPLETE` must precede `IMPLEMENTAUDIT_RUN_COMPLETE`.
- `AUDIT_COMPLETE` means the audit object reached terminal verified closure; it
  does not merely mean the runtime performed an audit operation.
- `AUDIT_HANDOFF` appears only when gaps, blockers, or handoff-required caveats
  remain.
- `AUDIT_HANDOFF` must not appear with `IMPLEMENTAUDIT_RUN_COMPLETE`.
- `AUDIT_WARNING` names a confidence caveat that did not block closure, such
  as accepted earlier evidence exceeding the trust-prior threshold. It is not
  a completion marker and must not hide weakened evidence.
- `IMPLEMENTAUDIT_RUN_COMPLETE` appears only after final audit has closed every
  in-scope ledger item terminally.
- If the final audit finds gaps, use an audit-fix round or handoff instead of
  printing completion.
- The final audit must check the namespaced run root when one exists:
  `ROADMAP.md`, `STATE.md`, `THINKING.md`, `PROTOCOL.md`, `sidecars.md`,
  phase specs, audit-fix specs, baseline ref, sidecar boundaries, and
  completion marker ordering.

## STOP / Andon / Hansei blocks

These blocks may appear when safety, evidence, ownership, or regression gates
fail.

```text
STOP:
Andon:
Hansei:
5 Whys:
```

They are evidence and recovery signals. They are not proof of closure by
themselves.

## Machine check

In the IMPLEMENTAUDIT source repo (the validator and its fixtures are
repo-side and do not ship in the installed package), run:

```bash
bash scripts/check-marker-order.sh  # source repo only; validates the tracked skeletons
```

The validator checks marker ordering, the Andon escalation rules (probe-first,
escalation-progress fields), and rejects handoff/failure transcripts that also
claim run completion. Installed consumers without the source repo validate
transcripts against the rules in this document.
