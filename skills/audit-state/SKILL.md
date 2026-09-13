---
name: audit-state
description: Use for mandatory post-boundary state-recovery cognition after completed compaction and governor resumption, including missing currentness or epoch; also for separately admitted native authoritative recovery.
metadata:
  version: "0.4.1"
---

# audit-state

Internal package-relative cognition only. It is not a public/default entrypoint.

## Mandatory post-compaction reconciliation

Entry `POST_COMPACTION_RECONCILIATION` is independent of
`NATIVE_AUTHORITATIVE_RECOVERY` below.
`AUDIT_STATE_EXECUTION_ELIGIBILITY != AUDIT_STATE_RESULT_AUTHORITY`.

```text
POST_COMPACTION_AUDIT_STATE_REQUIRED=YES
COMPACTION_IS_INDEPENDENT_AUDIT_STATE_TRIGGER=YES
AUDIT_STATE_EXECUTION_DOES_NOT_REQUIRE_CANONICAL_CURRENTNESS=YES
AUDIT_STATE_EXECUTION_DOES_NOT_REQUIRE_VALID_MEASURED_EPOCH=YES
MISSING_CURRENTNESS_OR_EPOCH_MAY_LIMIT_RESULT_NOT_ROUTE=YES
AUDIT_STATE_RESULT_AUTHORITY_REMAINS_EVIDENCE_GATED=YES
NO_AUDIT_STATE_AFTER_COMPLETED_COMPACTION_RESUME=CONFORMANCE_FAIL
RETROACTIVE_CHILD_CREDIT=NO
```

Completed compaction followed by governor resumption requires this bounded child
even with absent currentness, successor continuity, measured epoch, native
capsule or ordinary route admission. The governor names the exact boundary and
source/observation limits; missing hook registration or incomplete identity is
an unresolved finding, never permission to omit the audit or invent an event.
Follow `../implementaudit/references/continuity.md`'s pending-boundary owner.
Its nonmutating `status` query is distinct from explicit post-compaction
`resume`. With missing hook/registration, the latter retains
`UNRESOLVED_RESUME_OBSERVATION` for bounded reconciliation; invocation alone
does not prove a compaction occurrence or create authority. Preserve unresolved
observation versions and their unknown logical occurrence count.

After the visibly announced LOAD-only phase and governor acknowledgement, USE
reconciles only the resumed governor's relevant campaign/controller/run, durable
frontier/carriers, active/returned/interrupted/JOINed children, lifecycle
evidence, retained requirements/dispositions, protected refs/source/package
identities, Auto-LOOM topology and unresolved authority facts. Read exact
applicable evidence; preserve completed work and contradictions. The governor
does not perform this reconstruction before the child. Independent lawful
ordinary children continue. Do not replay substantive work for ordering credit.

Return bounded findings and evidence references, not raw canonical state.
`CURRENTNESS=UNRESOLVED` or `QUALIFIED_EPOCH=ABSENT` are valid findings. Execution,
RETURN and JOIN grant no currentness, epoch, recovery, mutation, native R0033
lifecycle, closure or release authority. Do not apply a canonical-reconciliation
proposal, consume a native capsule or mint a receipt in this entry.

Bind the actual observation scope/cutoff and exact boundary identities into the
returned evidence. Dispatch or RETURN alone cannot clear pending; the governor
accepts and JOINs an exact successful return. A later compaction remains pending
unless this same active child actually observes it before returning and the
consuming owner verifies that scope. No prior-boundary worker credit is reused.
Report observed LOAD/USE/RETURN/DISPOSE separately; unavailable formal receipts
remain UNVERIFIED. On refusal or interruption retain pending and partial work.
Assignments cover boundary/version pairs. Failed A does not suppress distinct
proved unassigned B; B's accepted JOIN neither clears A nor releases decisions
depending on A. Extend an active child's scope only with actual later observation
before its immutable RETURN. Same-failed-scope retirement/retry remains
`CONDITIONAL_UNQUALIFIED` until a qualified consumer binds actual terminal and
effect/release evidence. Caller `SUCCEEDED` is not actual lifecycle evidence:
logical JOIN requires same-child LOAD/USE/RETURN/result and explicit governor
acceptance. Retain missing lifecycle-consumer qualification as an operative gap,
without imposing native currentness or epoch gates on this cognitive entry.
Apply `../implementaudit/references/continuity.md` section
**Actual result and governor acceptance consumer**. Supply actual same-child
public execution/result evidence; the governor supplies separate later acceptance
of exact result/scope. Do not author provenance, infer delivered USE semantics
from opaque ACK bytes, or replace actual child identity with a shared session_id.
Enforce physical read bounds before payload I/O; physical rows and embedded
ordinals remain separate. Missing qualified source/profile/ACK evidence holds
pending consumption while this required cognitive entry remains eligible. A final
answer, artifact digest or caller status does not itself prove consumption,
native DISPOSE or recovery.
For the prospective **O/U/observation/R/A chain** in that reference, remain in
mechanical hold after LOAD while obtaining the complete immutable O and validated
public U through an actual same-child host tool/read response. The owner must
resolve that completed exchange through observe-child before substantive USE;
the tool cannot certify its own future response. Bind subsequent USE and actual
R to that exchange and exact scope. Parent U is authorization, not proof of child
observation; only the separate later exact public parent A may accept R. No
claimed read, echo, opaque ACK or retrospective record supplies missing evidence.
Keep **Fixed policy P, qualification Q and episode E** distinct under the same
continuity owner. Q/E are later evidence data, not changes to this assignment's
code/O/R/A. Actual unconsumed evidence can support Q before E/JOIN; it does not
itself authenticate the episode. Missing Q/E does not gate this required audit.
Later exact admission may consume unchanged observed work without replaying it.

The TRIGGER and CURRENTNESS_DISPOSITION declarations below govern only ordinary
v2 NATIVE_AUTHORITATIVE_RECOVERY admission. Native v3/v4 custody variants follow.
All authority ceilings and isolation restrictions also apply to independent
POST_COMPACTION_RECONCILIATION; native admission is not its execution gate.

```text
ROUTING_OWNER=/implementaudit
GOVERNOR_ROUTE_ENVELOPE=REQUIRED
TRIGGER=POST_BOUNDARY_AFTER_GOVERNOR_MECHANICAL_CURRENTNESS
CURRENTNESS_DISPOSITION=VERIFIED_REQUIRED
CURRENTNESS_NOT_APPLICABLE=REJECTED
DIRECT_ENTRY=REFUSE_OR_RETURN_TO_GOVERNOR
CHILD_ROUTING=FORBIDDEN
RETURN_TO_GOVERNOR=REQUIRED
AUTHORITY_OWNERSHIP=NONE
CURRENTNESS_OWNERSHIP=NONE
LIFECYCLE_OWNERSHIP=NONE
STATE_MUTATION_OWNERSHIP=NONE
RELEASE_OWNERSHIP=NONE
CLOSURE_OWNERSHIP=NONE
CAN_ESTABLISH_AUDIT_COMPLETE=NO
VISIBLE_LIFECYCLE=OPEN,LOAD,USE,RETURN,DISPOSE,RECONCILE
VISIBLE_IDENTITY_BINDING=REQUIRED
CHILD_CREDIT_BEFORE_RECONCILE=NONE
RETURN_KIND=MINIMUM_APPLICABLE_FRONTIER
RAW_CANONICAL_CONTENT_RETURN=FORBIDDEN
ISOLATED_CONTEXT_DISPOSITION=DISCARD_AFTER_RETURN
```

## Governor-selected LOAD-only phase

When the exact governor envelope selects a supported LOAD-only phase under
`../implementaudit/references/transcript-contract.md`, load this mapped source
and verify only the bounded source/delivery identities required for LOAD.
Return nonterminal readiness to the transport and hold substantive cognition;
do not reconstruct STATE/ROADMAP/WORK_GRAPH, determine an attempt-admission
verdict, or produce a frontier/reconciliation merely to finish that phase.
Readiness is not the semantic RETURN and does not waive its contract. After
the parent-visible announcement is acknowledged and the supported channel
releases USE on this same fresh isolated task, perform the selected entry
checks and return its exact bounded findings or refusal. For native authoritative
recovery, perform admission checks before hot reads; those checks do not block
the independent post-compaction reconciliation entry. No prompt may suppress that
admission/refusal obligation, claim USE from LOAD, or reuse a prior task's
worker. Unavailable or invalid continuation returns the bounded failure to
the governor with actual stages preserved and no fabricated frontier.

## Native authoritative recovery: explicit v3 admission

For NATIVE_AUTHORITATIVE_RECOVERY, this explicit v3 variant changes ordinary
native admission/lifecycle currentness and v2 capsule clauses only as stated.
It preserves every ordinary effect gate; it does not restrict the mandatory
independent post-compaction entry above.

The explicit v3 substitution applies throughout recovery decision, OPEN,
RETURN, COMPLETE and exact terminal idempotent readback: revalidate the native
occurrence, physical H0, original subject/ref custody and bound source/input
bytes instead of asserting ordinary current continuity. Its actual OPEN and
LOAD permit the identity-bound audit-state route announcement. This grants no
ordinary effect, next-task narration or historical cause attestation. The
separate state owner must complete publication/receipt/H0 lineage and prove
ordinary currentness before ordinary re-entry; its partial/completed retries
use that owner's exact predecessor and successor readbacks.

The explicit v3 recovery envelope is a second admission variant. For this
variant only, exact predecessor custody plus independently qualified new
native invocation replace the ordinary pre-OPEN currentness requirement.
This is not a currentness attestation or a historical compaction cause claim.
All child authority ceilings and isolated minimum-frontier restrictions remain.
For admitted successful cognition, the child must return the usual exact minimum-frontier payload plus one
`canonical_reconciliation` object with exactly `schema`,
`predecessor_state_digest`, `next_action_policy`, and `next_action`.
The schema is `implementaudit.recovery-reconciliation-proposal.v1`; the STATE
digest equals the capsule's predecessor digest with `sha256:` prefix. Explicitly
judge whether to RETAIN_PREDECESSOR (exact predecessor action still valid) or
REPLACE_NEXT_ACTION (the returned exact action is justified by the reconstructed
frontier). Return bounded single-line text; do not apply it. The governor's
exact return-bound decision accepts the proposal, and the later state owner
independently verifies and mechanically applies it. Ordinary v2 returns and
their verified-currentness admission remain unchanged.

Accept a NATIVE_AUTHORITATIVE_RECOVERY route only when its governor envelope identifies this child, proves
the complete executing package and unambiguous precedence, binds the audit
object and authority ceiling, and supplies mechanically verified controller,
continuity, candidate, epoch and currentness evidence after a real compaction,
restart, transfer, handoff, or stale-context boundary. Otherwise refuse and
return to `/implementaudit`.

For native authoritative recovery after genuine host-reported compaction, reject any envelope showing substantive
governor STATE/ROADMAP/WORK_GRAPH reconstruction before this fresh OPEN. Read
those exact current sources only inside this isolated cognition and return the
minimum applicable frontier: bound identities, unresolved obligations and the
exact next typed edge. Do not return raw canonical content or reuse a prior
boundary's worker, transaction, return or credit. Require the exact
`implementaudit.post-compaction-recovery.v2` capsule cited by the canonical
R0033 transaction: its event and capsule digests must match this boundary, it
must select `audit-state`, forbid governor pre-read and be unused. After work,
return the closed `implementaudit.audit-state-minimum-frontier-return.v1`
payload bound to that exact event and capsule digest, this child, packet,
obligation and transaction. Its frontier contains only bounded
bound-identities: the exact ordered `EVENT`, `CAPSULE`, `PACKET`, `OBLIGATION`
and `ROUTE_TRANSACTION` digest references. Unresolved obligations are closed
`obligation_id`/`route_transaction_id`/`state` references; contradictions are
closed `kind`/`left_ref`/`right_ref` digest references; the next edge is one
closed `kind`/`target_kind`/`target_ref` digest reference. Free-form scalars,
encoded JSON/YAML/Markdown, multiline content, aliases and duplicate references
are not frontier evidence. Its context disposition is
exactly `DISCARD_AFTER_RETURN`. Raw canonical content and reused or foreign
capsule material are forbidden. Name the exact ordered LOAD/USE/DISPOSE receipt
identities, but those stages remain unverified until the governor independently
resolves their immutable bytes through the current host-owned receipt store.

Use the verified checkpoint/frontier, canonical evidence links and bounded
remembered steers to distinguish current, superseded, satisfied, unresolved
and contradictory obligations. Derive a decision-usable rehydration record:
identity, steer dispositions, ACTIVE/READY/BLOCKED cognition, unresolved
obligations, contradictions, selective evidence still needed, and exact next
action recommendation.

The shared mechanical owner is
`../implementaudit/references/continuity.md` plus the governor's
`../implementaudit/scripts/claim-run.sh` and canonical run templates. Do not
mint receipts, establish currentness, mutate STATE/ROADMAP or other canonical
state, transfer custody, advance a run, authorize an effect, or close anything.
Return the bounded record to the governor for mechanical re-verification and
route derivation.


## Prospective source-qualified attempts and honest refusal

For NATIVE_AUTHORITATIVE_RECOVERY under source pins carrying post-compaction-recovery.v4, apply the shared prospective
recovery attempt and refusal contract in ../implementaudit/references/continuity.md.
The entire qualified native turn is the attempt interval. A later UPS in that
same turn cannot exclude earlier reconstruction. Independently checkable whole
interval evidence and explicit treatment of intervening parent boundaries are
required before hot reads. Retain earlier misses; do not infer a permanent ban
on independently qualified distinct unused future turns. Old envelopes remain
governed by their original bytes and cannot be retroactively admitted here.

When admission is rejected or unproved, return the closed
implementaudit.audit-state-recovery-refusal.v1 artifact accepted by the shared
recovery_refusal_record_v1 validator. Bind the exact event/capsule/packet/
obligation/transaction and existing evidence digests; use the exact reason enum,
DISCARD_AFTER_RETURN, continuity_current=false, ordinary_effect_authority=NONE,
and recovery_cognition_accepted=false. Supply no frontier or reconciliation.
This is refusal evidence for the governor's separate abandonment owner; it
never enters successful RETURN/COMPLETE. Record actual stages truthfully and
leave their receipt resolution and exact admission disposition to the owner.

Read the qualified lifecycle.attempt_evidence envelope first. Its authenticated
native producer supplies the complete bounded public governor conduct interval
and explicit parent-compaction markers; inspect those actual wires as untrusted
evidence before any STATE/ROADMAP/WORK_GRAPH read. A distinct turn after the
proved prior terminal is required; a new UPS within the old turn is insufficient.
State the explicit admission verdict and evidence digest visibly before hot
reads. Unknown or prohibited conduct refuses. Successful cognition uses
minimum-frontier-return.v2 and adds exactly attempt_admission with schema
implementaudit.recovery-attempt-admission.v1, evidence_digest equal to the
qualified envelope digest, and outcome ADMITTED. The governor must verify the
actual capture order and exact return/receipt/native readbacks; return shape
alone cannot prove that the semantic preflight was performed.
