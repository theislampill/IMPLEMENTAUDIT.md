# IMPLEMENTAUDIT State

Runtime copy target: `.IMPLEMENTAUDIT/runs/<task-slug>-<id>/STATE.md`

## Current phase

| Field | Value |
|---|---|
| Run root |  |
| Phase |  |
| Status | open |
| Audit object state | open |
| Route |  |
| Owner/source |  |
| Baseline ref |  |
| Last check |  |
| Next action |  |
| Continuity decision | pending |
| Authorization state | no commit / no push / no tag / no release / no provenance unless separately authorized |

Status values: `open` / `READY_TO_DISPATCH` / `IN_PHASE` / `PAUSED` /
`BLOCKED` / `INTERRUPTED` / `DONE`. Use these exact tokens; do not invent
run-state vocabulary.

## Audit object state

Audit object / record / surface:

Mnemonic: tdqyq-audit-object

Audit object produced/updated by:

Latest auditing operation:

Mnemonic: ydqyq-audit-action

Implementation action against object:

Final auditing operation:

Terminal closure condition:

Handoff state, if any:

Graphify status:

ActiveGraph status:

Markdown fallback:

Capability Ledger:

## Runtime artifacts

| Artifact | Status | Notes |
|---|---|---|
| `<run-root>/ROADMAP.md` | open |  |
| `<run-root>/STATE.md` | open |  |
| `<run-root>/THINKING.md` | open |  |
| `<run-root>/PROTOCOL.md` | open |  |
| `<run-root>/context.md` | open |  |
| `<run-root>/tools.md` | open |  |
| `<run-root>/sidecars.md` | open |  |
| `<run-root>/applied-context.md` or `<run-root>/applied-memories.md` | open |  |
| `<run-root>/repo-map.md` for brownfield | open |  |
| `<run-root>/phases/phase-N.md` | open |  |

## Ledger

| # | Finding | Priority | Action | Status | Evidence | Depends on | Follow-up |
|---|---|---:|---|---|---|---|---|

Evidence cells for newly recorded rows include the anchor
`@<full-40-hex-sha>` of the commit the evidence was captured at (legacy
rows without anchors remain valid). An artifact anchored to a different
state is never substituted for current-state evidence.

New external-state rows use the canonical prefixes `external-kind`,
`external-mutation-record`, `artifact-identity`, `collision-receipt`, and
`external-evidence`; legacy rows that do not opt in remain valid. Keep content
identity in the same ledger row as its human-readable name:

```text
artifact-identity: <case-sensitive-trimmed-name> | sha256: <64-lowercase-hex>
collision-receipt: <same-name> | hashes: <complete-comma-separated-hash-set> | reason: <nonempty>
external-evidence: <id> | bytes: <nonnegative-integer> | mtime: <RFC3339-UTC-whole-second> | liveness: snapshot|terminal | still-producing: true|false | use: orientation|terminal | closure-bytes: <integer|none> | closure-mtime: <timestamp|none>
```

Same-name distinct-hash artifacts require one exact collision receipt.
Terminal external evidence requires a matching closure re-stat; a
still-producing snapshot supports orientation only.

## Andon log

One row per ANDON_PROBE, ANDON_ESCALATE, or ANDON_HANDOFF event. `Class` is
exactly one official abnormality class from
`references/transcript-contract.md` §Andon escalation markers. One class
per row; one or more linked rows per occurrence: a single occurrence that
carries several independent defects records one row per class, sharing the
same `Occ` id (short occurrence id, e.g. `o1`), so co-occurring defects
keep their linkage and each remedy is tracked to closure.
ANDON_ESCALATE cites prior same-class rows by `#` before claiming
recurrence (per-class citation semantics unchanged by linkage).
There is no row-count limit: escalation is driven by same-class recurrence and
blocked closure, never by how many rows exist.

| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |
|---|---|---|---|---|---|---|---|

Outcome values: `resolved` / `escalated (cites #N)` / `blocked (handoff condition)` /
`open (rerun pending)`.

## Occurrence resolution and residuals

Occurrence resolution: not-applicable

(Values: `not-applicable` / `unresolved` / `partially-resolved` /
`resolved`. Route-sufficient rule: established hazard + admissible safe
route => contain first, record `partially-resolved` with named residual
rows — not a failure, not closure.)

One row per residual. Disposition values: `unresolved` / `deferred` /
`transferred` (name the receiving owner) / `owner-assigned` /
`risk-accepted` (cite the policy) / `validated-resolved` /
`SUPERSEDED_BY_CONCURRENT_MUTATION` (closure re-anchor proves the finding's
target changed). AUDIT_COMPLETE
requires every consequential residual to carry a non-`unresolved`
disposition, and completion language claims audit-completion only.

Decision-time deferrals are appended immediately to sibling
`deferrals.jsonl` using the canonical PROTOCOL order. Print that file verbatim
at phase end. Its rows point into this table, which remains the single closure
surface; a `pending` or `unresolved` row blocks closure, and only owner or
policy authority assigns a terminal disposition.

Final closure checker inputs:

- Superseded plans: none
- Cycle-accounted plans: none
- Steer directory: `<run-root>`

Replace `none` with every applicable path and pass the same paths through the
canonical PROTOCOL final-audit invocation. This table is an inventory, not a
substitute for executing the checker with those arguments.

| Residual | Consequential | Disposition | Owner / policy ref | Evidence |
|---|---|---|---|---|

## Execution identity

Legacy roots may omit this row. New phases record the canonical sibling-harness
names; `executing_model_resolved` and reviewer requested/resolved prose map to
these names and are not additional fields:

```text
schema: model-identity: requested_model: <model> | actual_model: <model> | evidence: self-report|host-event:<id> | claims: bound|IDENTITY_UNBOUND
```

A mismatch requires `claims: IDENTITY_UNBOUND` and an Andon row whose class is
`transport-infrastructure`; that row's evidence cell equals the identity row's
`self-report` or `host-event:<id>` value. Re-produce or re-verify those claims
under the requested identity before marking them bound.

## Context epochs and instruction applicability

Current epoch: e1

One row per continuity boundary (see `references/continuity.md` and
PROTOCOL.md §Continuity boundaries). Provenance is exactly one of:
`host-reported-compaction` / `new-session` / `handoff-resume` /
`manual-resume` / `inferred-context-gap` — never a fabricated compaction.
At most one writer claims a new epoch. Legacy run roots without this
section remain valid; new epochs after the feature version require it.

| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |
|---|---|---|---|---|---|

One row per continuity-critical instruction. Kind: `one-shot-action` /
`standing-constraint` / `standing-authorization` / `persistent-objective` /
`query-or-information-request`. Status: `active` / `satisfied` /
`superseded` / `revoked` / `expired` / `ambiguous`. Only a one-shot action
normally becomes `satisfied`; standing constraints/authorizations survive
until revoked/superseded/expired or their declared scope ends. Reference
is a source event id / content hash — never raw conversation text.

| Instr | Reference | Kind | Authority | Subject | Issued epoch | Status | Status evidence | Supersedes/by | Scope end |
|---|---|---|---|---|---|---|---|---|---|

## AGENTS_UPDATE_DECISION

Status: pending

Reason:

Scope:

Evidence location:

Final audit rule: this must be `updated`, `not warranted`, or `OWNER DECISION` before `IMPLEMENTAUDIT_RUN_COMPLETE`.

## CONTINUITY_DECISION

Status: pending

Reason:

Destination: none / AGENTS.md / memory note / OWNER DECISION

Evidence boundary:

Final audit rule: this must be `none`, `updated`, `deferred`, or `OWNER DECISION` before `IMPLEMENTAUDIT_RUN_COMPLETE`.

## Local git trace

Commit authorized: no

Push authorized: no

Tag/release/publication/provenance authorized: no

## Run terminal disposition

Append the emitted terminal marker as the final nonblank line of this file.
