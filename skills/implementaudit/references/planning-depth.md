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

## Engineering-value admission and control lifecycle

Preserve the gate or engineering obligation where warranted, while omitting
candidate work inside it that has no discriminating payoff for the current
state. When proposing, repeating, or standardising process work, reuse the
action-selection or Muda/Mura/Muri record. No retain, admit, or owner-decision disposition is complete unless it names the live driver; authoritative owner; consumer existence and authoritative consumer; protected consequence; cheapest sufficient discriminator; expected evidence and material marginal cost; activation and non-trigger path; and stopping, retirement, or reclassification condition. Incomplete evidence defers the lifecycle mutation and leaves the controlling gate intact.

Activate for a proposed permanent gate or artefact; repeated unchanged
evidence, planning, or reporting; unclear artefact consumption; unexplained
process-heavy work; avoidable serialisation; live-control retirement; or
IMPLEMENTAUDIT self-modification. No activation factor means no R34 diagnostic or artefact.
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

No universal rule makes shorter feedback, lower work in progress, smaller
batches, higher utilisation, more slack, or less slack correct. Stronger
control depth is warranted by material consequence or hard-to-reverse action,
not by a methodology label. Reuse the native action-selection record; do not
add lifecycle ceremonies, mandatory buffers, sprint machinery, traceability
matrices, or methodology-specific modes. When no proportionality pressure is
live, create no R34 artefact.

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
