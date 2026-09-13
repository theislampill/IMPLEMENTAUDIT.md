# Planning Depth

Use this reference when `/implementaudit` must decide whether to govern a
supplied target or synthesize a better bounded work target first.

## Native integration support reference

Planning depth supports native audit-object integration by routing read-only audit-object
closure requests, repo-content-as-data security boundaries, and
handoff planning into the audit object. The primary integration contracts live in
`audit-category-matrix.md`, `plan-lifecycle.md`, and
`terminology-integration.md`; this file decides whether those contracts close
directly, through a run-root phase plan, or through a bounded handoff.

When a material residual or future objective may outlive its current carrier,
apply `issue-ready-work-orders.md`'s continuation sufficiency test. This selects
local drafting depth across audit, brownfield, greenfield, planning, research
and architecture; it does not select durable IDs or grant publication authority.
A sufficient compact carrier and an ordinary bounded task retain the cheap path.

## Invocation shapes

### Embedded governance

The user has already supplied a host goal, task, plan, or `/goal` runner target.
ImplementAudit inherits that run's audit object and applies auditing actions
inside it. Do not print a second `/goal`.

Use when the prompt already contains:

- the repo or worktree
- the target artifact or finding set
- the intended outcome
- safety boundaries
- enough verification shape to begin

### Direct governance

The user invokes `/implementaudit` with a concrete audit, handoff, checklist,
review, or bounded implementation plan. Normalize the artifact into a ledger and
execute with Smoke A/B, owner/source patching, and terminal audit-object closure.

### Goal synthesis

The user gives an idea, gap, incomplete target, or asks for the next best
implementation prompt. Do enough Gemba and strategy alignment to return a
bounded, evidence-aware Kaizen handoff. If the host should continue under a goal runner,
construct the audit object and print one ready-to-paste `/goal Using
/implementaudit ...` line.
This is plain strategy alignment, not Hoshin Kanri / policy deployment
vocabulary.

### Governed casual-build intake

The user supplies natural-language repo-build intent (e.g., "add a login page",
"wire up CI", "ship the CLI tool") without an audit object, plan, or structured
goal. ImplementAudit synthesizes a `tdqyq-audit-object` from the intent before
routing.

Use when the input is:
- a natural-language description of a repo-build goal
- not yet structured as a handoff, checklist, or implementation plan
- not empty, unsafe, non-repo, or impossible

**Casual-build planning bar:** at minimum, clarify scope, owner/source
candidates, acceptance criteria, and rollback path before mutation. Ask up to
four batched questions when material gaps remain. Do not proceed until the audit
object is defined. Do not skip the input gate, Smoke A/B, or the final audit.

IMPLEMENTAUDIT is an audit-governed implementation skill that routes natural-
language build intent through the same audit contract as any other invocation
mode. Casual-build intake is not a bypass; it is a synthesis step.

## Depth rule

Use the smallest planning layer that makes the work safe:

- single finding, clear owner/source: direct ledger row
- multiple dependent findings: phase plan
- unclear objective or missing evidence: synthesize a bounded goal first
- conflicting repo policy: OWNER DECISION

Do not add a planning layer merely because the work is large. Add it when the
extra structure improves evidence, sequencing, rollback, or owner decisions.
Do not add external terminology merely because it is familiar. Add VOC/CTQ/SIPOC,
FMEA-lite, STRIDE, Strangler/ACL, Bounded Context, or Poka-yoke/Control Plan
wording only when it changes a native route, required field, Andon trigger,
evidence boundary, or Plan Closure control. SOLID/GRASP remains a
checker/fixture negative guard only in v0.3.0.0; do not add it as a planning
depth reason or design lens.

For high-risk, release-affecting, package-boundary, provenance, or public-claim
work, the planning layer must preserve the double-audit pattern: create or
normalize the audit object, act against it, then verify terminal object closure.

## Action-selection contract

Every ordinary task-shaped invocation derives the warranted
`ydqyq-audit-action` set from the live factors of the request and repo:

- scope
- uncertainty
- risk
- dependencies
- evidence gaps
- authorization state
- intended executor

Depth never requires an activation keyword. Do not wait for wording such as
"deep", "plan", or "review" before selecting reconnaissance, dependency
analysis, planning depth, or decomposition actions; the factors alone decide.
The same factors also bound restraint: when a narrow, already-bounded
owner/source repair gains no safety, evidence, sequencing, or executor
reconstructibility from deeper structure, stay direct.

Selection is recorded, both ways. Write an action-selection record into the
audit object: the `## Action selection` section of the run-root `THINKING.md`
when a run root exists, otherwise an equivalent transcript row. The record
names:

- input shape and intended executor;
- uncertainty, dependency density, and evidence gaps;
- authorization state;
- selected `ydqyq-audit-actions`;
- considered-but-omitted actions with the reason each was not warranted;
- why deeper planning was or was not warranted.

Reference loading follows selection. The selected action set names the
owner/source references it needs: load `phase-design.md` when decomposition is
selected, `child-agents.md` when bounded specialist review is selected, and
`plan-lifecycle.md` when a handoff artifact will be emitted. A weak or
fresh-context intended executor, material dependency density, ambiguity, or
risk deepens the action set automatically; request size alone never does.

An absent or hand-wavy action-selection record is a plan-quality defect, not a
style preference.

### Conditional systems-security selection

The same live factors select the conditional profile in
`audit-playbook.md` when there is a material protected consequence, an exposed
or untrusted capability, a changed trust, privilege, or delegation boundary,
consequential security authority, a provenance-dependent claim,
adaptive-adversary or common-mode risk, weak detection or recovery, or a
consequential security, privacy, safety, availability, or usability decision.
Record why the profile was selected or omitted and the cheapest sufficient
evidence layer. It remains attached to the current audit-object owner, with no
separate security mode, workflow, or planning artifact.

Low-exposure reversible work inside a current proven envelope stays on the
cheap path: record the protected consequence, one plausible-abuse or trust
check, exact current identity, and rollback. If neither a profile trigger nor
that cheap-path condition exists, record the omission reason and retain the
ordinary security pressure; do not manufacture a profile.

### Verifier-plan selection

For a proposed change, derive the verifier plan in this order: exact change
identity -> authoritative changed semantic owners and effects -> affected
evidence obligations and consumers -> cheapest sufficient verifier plan ->
escalation or omission rationale. Record the affected generated, runtime,
package, registry, release, public, and external consumers; the evidence layer;
residual risk; rollback; the cheapest sufficient decision-changing verifier;
and the equivalent-protection evidence and current owner authority for every
omitted verifier.

A trivial local reversible change with a current owner, effect, consumer,
evidence layer, residual, rollback, and equivalent protection stays on the
serial cheap path. A generated, transitive runtime, package, or public/external
consumer selects the verifier for that affected consumer. Do not select full
verification from diff size, a fixed command count, or a generic review mandate;
select it only for the named owner, consumer, or risk that needs it.

Unknown owner or relation, a changed registry, package or release ambiguity,
or a stale projection invalidates a narrow plan: stop, reclassify, and escalate
conservatively. Do not create a permanent graph, worksheet, model call, or
second action-selection owner for ordinary cheap work.

## Engineering-value admission and control lifecycle

Preserve the gate or engineering obligation where warranted, while omitting
candidate work inside it that has no discriminating payoff for the current
state. When proposing, repeating, or standardising process work, reuse the
action-selection or Muda/Mura/Muri record. No retain, admit, or owner-decision disposition is complete unless it names the live driver; authoritative owner; consumer existence and authoritative consumer; protected consequence; cheapest sufficient discriminator; expected evidence and material marginal cost; activation and non-trigger path; and stopping, retirement, or reclassification condition. Incomplete evidence defers the lifecycle mutation and leaves the controlling gate intact.

For reuse in a successor decision, declare the operative decision family in
the existing action-selection, finding/repair or continuation record. Justify
unchanged decision-relevant meanings or an explicit evidence-transfer relation,
including scope, permissions, ownership, prohibitions, activation conditions
and evidence limits. Keep remaining possibilities requiring different lawful
actions distinguishable. Positive admission is permitted only if every
remaining possibility permits that admission; otherwise defer the affected
admission and retain its first missing discriminator. A digest, earlier PASS
or handoff label supplies neither present sufficiency nor authority. Keep
richer evidence accessible for later questions; justified unchanged meaning
permits reuse without replay.

If the controlling evaluator is revised, bind predecessor-governed
justification through the existing R0023 owner/contract/effective-boundary and
independent-property controls in `phase-design.md` P4-16/P4-17; the revised
evaluator cannot be its own sole warrant. Extend only the applicable existing
record; this creates no separate lifecycle, universal dossier or replay rule.

Activate for a proposed permanent gate or artefact; repeated unchanged
evidence, planning, or reporting; unclear artefact consumption; unexplained
process-heavy work; avoidable serialisation; live-control retirement; or
IMPLEMENTAUDIT self-modification. No activation factor means no R0022 diagnostic or artefact.
Ordinary bounded work keeps its existing minimum Smoke A/B and
self-check path without a worksheet, meta-work ratio, or per-command defence.

Select feedback cadence, finite slack or buffers, sustainable recovery
capacity, temporary option preservation, and control depth proportionately to
variability, information value, actionability, consequence, reversibility,
recovery need, and carrying cost. Protective slack or a buffer is not waste
when it has an authoritative consumer, protects a named consequence, and its
benefit exceeds its bounded carrying cost. Feedback value depends on actionable
information rather than frequency alone. Temporary option value is retained
only while expected information value exceeds carrying cost and an exit or
reclassification condition remains live. Preserve sustainable recovery
capacity instead of treating maximum utilisation as value.

Material retry, recovery, or redispatch admission is conjunctive. Require
semantic retry eligibility from the durable `FAILED_NO_EFFECT` state, a live
deadline, queue age within policy, downstream capacity for the requested work,
and recovery headroom for the requested work. Unknown effect state or any
missing input refuses admission. Host/free executor slots and queue depth are
observations, not downstream/recovery capacity or retry authority. Definitive,
untriggered local work remains the serial cheap path and creates no retry queue.
`CHEAP_PATH` requires canonical `NOT_STARTED`, no semantic retry eligibility,
and zero requested work, deadline, queue-age, downstream, and recovery fields.

No universal rule makes shorter feedback, lower work in progress, smaller
batches, higher utilisation, more slack, or less slack correct. Stronger
control depth is warranted by material consequence or hard-to-reverse action,
not by a methodology label. Reuse the native action-selection record; do not
add lifecycle ceremonies, mandatory buffers, sprint machinery, traceability
matrices, or methodology-specific modes. When no proportionality pressure is
live, create no R0022 artefact.

Assess consequential/degraded work for coordination/peak-attention burden,
information/recovery capacity and current intervention capability/authority.
High consequence needs a current target state, feedback, containment and
recovery; nominal override or labels are insufficient. Degrade only if stopping
is hazardous and the degraded envelope is bounded and observable. An
authorised safe stop and no material trigger make a bounded control `CHEAP_PATH`
although the material proposal is `BLOCK`; they differ. Retire the control when
its consumer/driver ends. Reversible low-consequence work with
direct readback is the serial cheap path.

### Auto-LOOM development and continuing improvement

These developmental stages describe abstraction and maturity, separately from
the runtime directions in `child-agents.md`. The first maturation proceeds
through the following stages in order.

| Stage | Developmental meaning |
|---|---|
| PRODROMAL | Emerging proto-practice from work already being done. |
| SUBLIMATION | Explicit coherent abstraction of the emerging practice. |
| CONDENSATION | Concrete contracts, mechanisms, properties, cells, tests, source loci and acceptance criteria. |
| ACTUALISATION | Actual implementation, integration, installation, qualification and release, each at its applicable evidence and authority boundary. |

PRODROMAL is not FORWARD; SUBLIMATION is not state re-derivation; CONDENSATION
is not JOIN. A proposal or retained contract is not ACTUALISATION.

PRODROMAL practice bootstraps reflexive, evidence-driven self-improvement that
continues after ACTUALISATION. Improvement cycle:

```text
executed Auto-LOOM n
-> observed anomaly/opportunity
-> improvement candidate
-> SUBLIMATION
-> CONDENSATION
-> existing authority/review/tests/qualification
-> ACTUALISATION Auto-LOOM n+1
```

Apply the engineering-value admission and control lifecycle above to each
candidate: require its live driver, owner, consumer, cheapest sufficient
discriminator, marginal value and stopping condition. Preserve reject, defer
and no-change outcomes; recurrence or a candidate never mandates a change.
Use existing authority, currentness, review, tests and qualification controls;
this loop adds no controller or gate and permits no unattended self-rewrite.

## Conditional delegation and work-conserving execution

Use **conditional planner/executor separation** when material engineering
judgement would otherwise be confirmed by the same role that mutates it and
self-confirmation risk, a contested interpretation, or a high-consequence
change is live. Freeze the planning/adjudication role against source mutation,
dispatch a separately bounded executor, and require an independent reviewer to
reread the resulting source and evidence. Executor output is candidate evidence,
not acceptance authority. If the independent execution or review route is
unavailable, block or obtain an owner decision; do not silently collapse the
roles. Ordinary narrow, reversible work with one obvious route stays on the
same-root cheap path.

When several authorised executor routes are valid, select the least-cost
sufficiently capable route after checking context completeness, privacy,
tooling, authority, and acceptance needs. Compile the necessary owner/source,
scope, constraints, acceptance, rollback, and STOP conditions into the durable
handoff. A delegate that encounters missing context or insufficient capability
stops and escalates; cost never overrides correctness or evidence.

For three or more material cells with closed dependency, write, acceptance,
resource, and authority boundaries, maintain a work-conserving ready-cell
frontier. Activate worthwhile independent ready cells up to safe host capacity
and any positive **operator-supplied ceiling**; recompute after a cell completes
or blocks, capacity or authorization changes, or drift is observed. Unknown
independence, shared boundaries, and irreversible external work serialize until
proved safe. An unchanged reminder is not a scheduling transition and does not
justify redispatch. Fewer than three material cells, unavailable parallelism,
or an effective capacity below two uses the serial cheap path. The ceiling is a
maximum resource envelope, not a fixed agent quota or utilization target, and
does not replace factor-derived depth or marginal-value stopping.

Before activation, reconcile every governed cell exactly once into an
evidence-current DONE, ACTIVE, READY, or BLOCKED state. Unknown or stale state
defers dispatch. READY requires its actual dependency edges satisfied; compute
free capacity only after subtracting ACTIVE occupancy.

When the canonical WORK_GRAPH v1 owner exists,
derive the bounded ready-cell projection with `compile-work-graph.py` before
dispatch. Reject stale counts/digests, an absent or malformed declared
writer/resource hold index, dependency gaps, cycles, and unknown states
instead of reconstructing authority from narrative STATE, ROADMAP, a sidecar,
or model estimates. Empty `{}` truthfully means the graph declares no holds. The
projection transcribes every declared hold losslessly and deterministically; it
does not attest undeclared relationships or semantic completeness. Upstream
graph construction, review, and currentness own that completeness. The
projection is read-only evidence; it does not mint currentness, transition
cells, or write lifecycle state.

When the graph carries complete positive declarations, derive
`PREPARATION_FRONTIER` and `PRODUCT_FRONTIER` beside—not in place of—the exact
legacy execution projection. Preparation is effect-free, assumption-bound,
selectively invalidated, and no-credit: preparation never satisfies a
dependency, creates dispatch, authorizes source, substitutes for activation
RED, or changes lifecycle. Omit the extra projection on the legacy empty path
so its execution bytes remain identical.

Preparation predecessor observations are closed over the target's dependencies
and live holders. Qualified predecessors bind their exact graph-owned
commit/tree/review identity; all others carry a mechanically derived unavailable
reason. Activation recompiles current graph bytes instead of accepting stored
predecessor values supplied again by the caller and requires the record's exact
graph binding. This contract has no unchanged-slice reuse receipt for a changed
graph.

Every source-bearing DONE cell must expose one exact qualified product and one
current disposition through its existing result owner. Non-cell owner
amendments remain under existing integration topology rather than entering the
cell population. Reject null, free-form, stale, multi-disposition, unknown, or
unowned results. Report deterministic consumed/composed/integrated/
superseded/rejected/deferred counts, integration debt, and a real potentially
stranded count. A named future join is an owned deferral; zero stranded means
the product-idle P0 is not triggered, not that the mechanical control is
unnecessary.

A governed product contract is not a per-cell opt-in. Its verified authority
document classifies every DONE cell, exhaustively maps every qualified cell and
non-cell owner to an exact product and one kind-specific disposition, and binds
join, proposal, review, receipt, and future-consumer identities. The compiler
requires and hashes the authoritative source bytes independently of graph
shape, and the CLI binds the actual supplied authority path to the declaration
after canonical resolution relative to the graph directory. Governed
two-argument input and the graph authority owner are themselves product
signals. Missing/falsified classification or shaped-but-unbound evidence
rejects; runtime debt/P0 is derived from the complete governed population.
Only one-argument input with no product or authority signal takes the
byte-identical legacy path.

A product-aware preference only orders otherwise equal work already admitted
by current dependencies, writer/resource holds, qualification independence,
integration authority, and the execution or preparation gate. It cannot create READY,
ACTIVE, DONE, JOIN, currentness, route, merge, lifecycle, package, release, or
closure authority. Any newly safe composition remains a proposal for its
existing integration owner, never a hidden graph edge or lifecycle transition.

### Proximal diagnostic scheduling

### Native A/B/G preparation consumers

Native preparation consumes current typed facts rather than fixture verdicts.
`MAY_AFFECT` exposes safe learning work early but is never an execution
predecessor; only `MUST_FINISH_BEFORE` is one. Shared writes serialize only
their overlapping writers, unknown impact blocks only the affected work, and
host capacity is a resource queue rather than a semantic edge. Invalidation is
the exact semantic/write/test/package radius: preserve proved-disjoint evidence,
show unknown affected consumers as blocked, expand package membership only to
the package/install projection, and keep harness-only change to harness proof.
Before ordinary work begins, select one owner: governor mechanical work,
child task work, a named child skill for specialist cognition, or `BLOCK` on
unknown/contradictory evidence. A child-to-child dispatch request stops. The
sole governor retains join, acceptance, lifecycle, and release authority.
Native scheduling is preparation-only and fail-closed: represent local write,
acceptance, resource, irreversible-effect, and authority boundaries; do not
replace any of them with controller-wide serialization. Require current
authorization and currentness before a cell is selected, retain `NONE` for
lifecycle and acceptance credit, and preserve safe disjoint cells as parallel.
Compute usable capacity as the minimum of host capacity and operator ceiling,
subtract active resource demand, then select the highest-ranked ready work that
fits remaining demand without a local write/resource conflict. The native owner
record has a paired closed requester/action vocabulary: `GOVERNOR`/`ASSIGN` is
the ordinary entry; `CHILD`/`DISPATCH_CHILD` stops; missing, unpaired, or
unknown tokens fail closed.

At a frozen candidate boundary, classify dependency type rather than inferring
it from workflow prose. Hard execution prerequisites and shared writer/resource
exclusions block execution; acceptance prerequisites block lifecycle credit;
informational/differential coupling changes interpretation but is not itself an
edge. `INFORMATIONAL_DIFFERENTIAL` remains an explicit parallel topology, not
`INDEPENDENT`. Every generic workflow action selection supplies one exact,
bounded action/effect population; R0035 derives applicability from its count and
target rather than accepting a caller boolean. An applicable decision must
execute the R0035 proximal classifier and bind its projection to an
immediate-decision advance token. The existing Stop continuation interlock then
runs `--proximal-action-selection` from the fixed run-root R0035 artifacts and
atomically consumes the canonical selection identity in the fixed external
host-session store before ordinary continuation. Absence, partial transport,
drift, forgery, copied/renamed/concurrent replay, or unknown completion stops.
The explicit no-pair path returns
`NOT_REQUIRED:FEWER_THAN_TWO_BOUNDED_ACTIONS`; absence of the population is not
that cheap path. Review-before-smoke wording alone cannot strengthen the
authoritative DAG; workflow-local order is not an execution dependency.

R0022 weighs both action risk and the risk or cost of delayed information. A
bounded, recoverable, isolated, authority-free diagnostic may run beside fresh
acceptance review only when its exact identity/currentness and minimum gate are
current; blast radius/non-targets, retreat, before/after evidence, and
unknown-completion containment are proved; and a higher-fidelity live discriminator
has material decision value. Also record the marginal defensive
complexity, coupling, latent-failure, and delay cost; more pre-flight is not
intrinsically safer. The derived safety strategy is visibly one of
`PREVENTION_FULL_PREFLIGHT`, `EARLY_DETECTION_ACTIVE_DEFENSE`,
`CONTAIN_AND_RECOVER`, `ORDINARY_PARALLEL`, or `STOP_RECONCILE`.
At least one material marginal defensive-cost basis is required to override
acceptance-first serialization; the projection lists the exact contributing
complexity, coupling, latent-failure, or feedback-delay fields. Those costs never
override a failed safety, containment, currentness, or authority predicate.

Qualification depth is a separate output of that same mandatory action
selection, not a workflow default. Bind the exact change/dependency slice,
affected contracts, evidence-applicability tuple, semantic invalidation radius,
next effect, reversibility/blast radius, intermediate-versus-frozen-product
class, and meaningful-JOIN availability. Derive only the causal/adversarial
slice and fresh component review for a local correction; dependency-derived
component evidence for a shared currentness/authority substrate; no terminal
whole-product claim for an accepted intermediate moving toward JOIN; and
whole-projection review plus full pre-flight for a frozen install/cutover or
irreversible authority effect. A post-review edit is classified by applicability
and semantic radius, never diff size. Exact unchanged tuples may be retained,
and every broad rerun or reuse reports its evidence-backed reason. The advance
token binds this qualification result; one-use authority belongs to the
external host-session consumption receipt, never a sibling token marker.

Project downstream qualification work backward without pulling its authority
backward. Here, lowercase backward describes projecting future work earlier:
it is runtime FORWARD preparation, not BACKWARD return/JOIN.
Precompute applicable future ancestor-JOIN prerequisites now when their actual
preparation inputs and authority permit; block only the affected edge.
Apply the full-campaign traversal and event binding in `child-agents.md`, beyond
the local recovery subtree. Reconsider sibling and future admission, census,
qualification, source/package and release inputs at every known ancestor;
retain each pending owner, consumer/JOIN, exact missing input and reconsideration
trigger. Unknown independence stays unknown; an effect's native/currentness gate
does not blanket-block independent preparation. Retention is not reconsideration,
and completed evidence is reused only at its established scope without replay.
A frozen exact input may make its long evidence gate runnable now,
and a future whole review may prepare its invariant matrix, gate inventory,
held-outs, harness, applicability map, and independent-review requirements now.
The final whole verdict and identity-specific checks remain blocked until the
actual integrated identity is frozen. Early evidence is explicitly
`EVIDENCE_AVAILABLE_NOT_CONSUMABLE` with authority `NONE`. At the consuming
JOIN, reread product/input, dependency slice, fixture, toolchain, contract,
scope/effect, currentness, and final identity, then explain `REUSE`,
`PARTIAL_RERUN`, or `DISCARD`. Preparation must not contain a review conclusion,
preselect the independent reviewer, guess final bytes, substitute a mock as
final, or perform an irreversible/public effect.

The diagnostic lane is evidence gathering, never acceptance. Reconcile both
lanes by supplying the original request plus projection and results so the
projection is rederived against the same commit/tree/input/current receipt and
minimum gate. Preserve independent
controller/currentness, fixture-coverage, product, review, and containment
contributors; disagreement raises the existing R0037 Andon, and R0038 drift
invalidates stale evidence. A decisive early result may reprioritize the other
lane only after assessing its remaining information value.

Evidence-based omission preserves the controlling obligation, establishes the
current decision with a narrower discriminator, records the residual, and
retains escalation when risk changes. Omission for convenience or cost alone is
optional-by-whim and does not waive a warranted gate.

## Unit independence and change class

At three or more enumerated work units, record:

```text
unit_independence: independent | ordered(<reason>)
change_class: <approved class>
```

Independent means no unit needs another's uncommitted output; ordered names the
dependency. Batch independent units to host concurrency and rollback margin,
then run the class-earned ceremony once per batch. Fewer than three units use
ordinary planning. Scaling never waives review, rollback, or external gates.

For a materially decomposable run, distinguish actual dependency, write,
acceptance, resource, authority, and composed-only boundaries before scheduling.
A shared issue, milestone, branch train, eventual package, or public surface is
not itself a dependency. Route known-independent units to the work-conserving
ready-cell frontier in `child-agents.md`; unknown or overlapping boundaries
remain ordered. This adds no frontier artefact to the ordinary serial path.

| `change_class` | Ceremony floor |
|---|---|
| `reversible-local` | Smoke A/B + Stage 6; no repetition-only cold review. |
| `reversible-local-multi` | Smoke A/B + phase validation; one review/batch. |
| `reversible-deployed` | Local floor + rollback proof + one cold review/batch. |
| `irreversible-local` | P4-3 characterization + rollback proof/unit. |
| `irreversible-external` | Full ceremony/review/external gates + rollback or rehearsal/unit; no amortization. |
| `unknown` | Treat as `irreversible-external` until evidence narrows it. |

The most consequential action sets the class; external mutation forbids a local
class. On change, stop, reclassify, and re-plan.

Regardless of planning depth, execution continues phase-by-phase until terminal
audit closure (`AUDIT_COMPLETE`) or an explicit audited handoff
(`AUDIT_HANDOFF`). Blocked work ends in handoff, not fake completion.

## Native planner stage rule

When goal synthesis or phased audit closure is selected, the stage contract in
`SKILL.md` is load-bearing:

```text
Stage 0 - Context/tool/repo-state detection
Stage 1 - Audit-governed intake and routing
Stage 2 - Recon / Gemba
Stage 3 - Deep think / risk and dependency analysis
Stage 4 - Phase decomposition
Stage 5 - Write .IMPLEMENTAUDIT/runs/<task-slug>-<id> runtime artifacts
Stage 6 - Plan review and self-critique
Stage 6.i - Independent cold review
Stage 6.ii - Pre-flight smoke
Stage 7 - One ready-to-paste /goal handoff when not already embedded
```

New first-party artifacts use `6.i` and `6.ii`. Historical `6.2` and `6.5`
normalize as aliases for those same two substages; they do not create extra
stages or change order or semantics.

The stages are native IMPLEMENTAUDIT behavior. They do not import another
package's identity, artifact paths, or completion markers. The execution spine
still governs the actual work inside each phase.

## Planning artifacts

When phase planning is selected, do not leave the plan only in chat. Create or
update:

- `.IMPLEMENTAUDIT/ROADMAP.md`
- `.IMPLEMENTAUDIT/STATE.md`
- `.IMPLEMENTAUDIT/THINKING.md`
- `.IMPLEMENTAUDIT/PROTOCOL.md`
- `.IMPLEMENTAUDIT/phases/phase-N.md`

For new planned runs, prefer a namespaced run root claimed by
`"${IMPLEMENTAUDIT_SKILL_DIR:-skills/implementaudit}"/scripts/claim-run.sh`:

```text
.IMPLEMENTAUDIT/runs/<task-slug>-<id>/ROADMAP.md
.IMPLEMENTAUDIT/runs/<task-slug>-<id>/STATE.md
.IMPLEMENTAUDIT/runs/<task-slug>-<id>/THINKING.md
.IMPLEMENTAUDIT/runs/<task-slug>-<id>/PROTOCOL.md
.IMPLEMENTAUDIT/runs/<task-slug>-<id>/context.md
.IMPLEMENTAUDIT/runs/<task-slug>-<id>/tools.md
.IMPLEMENTAUDIT/runs/<task-slug>-<id>/sidecars.md
.IMPLEMENTAUDIT/runs/<task-slug>-<id>/applied-context.md
.IMPLEMENTAUDIT/runs/<task-slug>-<id>/repo-map.md
.IMPLEMENTAUDIT/runs/<task-slug>-<id>/phases/phase-N.md
```

Flat `.IMPLEMENTAUDIT/*` files remain legacy resume/audit compatibility, not
the preferred target for new run artifacts. Namespacing protects planning
artifacts from clobbering; use separate git worktrees for true parallel source
editing.

`THINKING.md` is reviewable planning evidence: objective, route, owner/source,
risks, dependencies, rollback, evidence strategy, generated-artifact plan,
sidecar boundaries, and owner decisions. It is not private chain-of-thought.
When terminology integration fires, `THINKING.md` must attach it to native parent,
phase, route or lens, owner/source, inputs, outputs, evidence boundary, Andon
trigger, and fixture/checker or justified non-mechanical boundary.
