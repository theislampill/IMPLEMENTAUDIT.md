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

## Planner markers

Planner markers appear before a user starts a generated `/goal` handoff.
They are emitted by Stage 6 and Stage 6.5 of the native IMPLEMENTAUDIT planner.

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
`## Andon log` (`# | Phase | Class | Abnormality | Countermeasure |
Rerun evidence | Outcome`). `Class` is exactly one official abnormality class:

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
| Authorized reviewer returns no verdict (platform filter blocked the review) | `transport-infrastructure` | review-channel failure; preserve non-verdict, reissue to same reviewer identity |

Same-class recurrence — not a try count — is what drives escalation. The log
has no row limit.

These markers and classes apply to any governed run, phased or not. When no
run root exists (direct in-session governance), the Markdown findings ledger
serves as the Andon log substrate: record the abnormality class on the ledger
row and cite prior same-class rows on escalation.

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
  conditions.

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

- `AUDIT_START` carries `Skill version:` — the plugin manifest version of the
  payload that produced the run (`unknown` when unresolvable, never guessed) —
  so any transcript can be attributed to its contract version.
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
