# Phase Design

Use phases when a supplied audit or synthesized goal is too large, risky, or
dependent to close as one atomic implementation pass. Execution continues
phase-by-phase until terminal audit closure (`AUDIT_COMPLETE`) or an explicit
audited handoff (`AUDIT_HANDOFF`); the run does not stop at a partial phase
boundary unless the handoff is explicit and recorded.

## Native integration support reference

Phase design supports native audit-object integration by preserving read-only audit-object
closure boundaries, repo-content-as-data security handling,
branch/diff classification, execute/review isolation, and reconciliation inside the run root. The primary
behavioral contracts live in `audit-category-matrix.md` and
`plan-lifecycle.md`; `terminology-integration.md` supplies only route/field/checker
terms that strengthen those native contracts. Phases carry those contracts into
executable specs.

## Phase rules

- Each phase must close one coherent slice of audit risk.
- Each phase mutates or verifies against the same `tdqyq-audit-object` unless an
  owner decision explicitly splits the work into a new audit object.
- Release-affecting or package-boundary phases must first update the audit
  object with the finding and allowed scope, then use `ydqyq-audit-action`
  operations to implement against that object, then verify the object's terminal
  state.
- Each phase needs an owner/source, acceptance criteria, Smoke A, Smoke B, and
  a rollback or deferral path.
- If an external term is used, each phase needs its native parent, runtime
  phase, route or lens, owner/source, evidence boundary, Andon trigger,
  fixture/checker or justified non-mechanical boundary, and final-audit check.
- Stage 4 derives the phase count from dependencies, risk, and evidence shape;
  do not merge unrelated work to fit an artificial count.
- Stage 5 writes a namespaced run root under
  `.IMPLEMENTAUDIT/runs/<task-slug>-<id>/` when phase planning is selected:
  `ROADMAP.md`, `STATE.md`, `THINKING.md`, `PROTOCOL.md`, `context.md`,
  `tools.md`, `sidecars.md`, `applied-context.md` or
  `applied-memories.md`, `repo-map.md` for brownfield work, and one
  `phases/phase-N.md` file per phase.
- Final audit and cleanliness checks use complete working-tree comparison
  against the phase baseline when available.
- `P0` work precedes `P1`; `P1` precedes `P2` unless a dependency demands a
  different order.
- Generated artifacts follow generator-first policy.
- Scope creep is logged instead of silently absorbed.
- A blocked dependency defers dependents; it does not license guesswork.
- There is no artificial phase-count cap. Use as many phases as evidence and
  rollback safety require.
- Namespaced planning artifacts prevent run artifact clobbering. They do not
  make simultaneous source edits safe; use separate git worktrees for true
  parallel implementation.

## Owner/source discipline

Patch the place that owns the behavior. A failing rendered doc, generated file,
or downstream checklist may identify the symptom, but the owner/source is the
canonical file, generator, manifest, policy, or runbook that controls it.

## Phase closure markers

Every executing phase must emit:

```text
IMPLEMENTAUDIT_PHASE_START
IMPLEMENTAUDIT_PHASE_VERIFY
AGENTS_UPDATE_DECISION
IMPLEMENTAUDIT_PHASE_DONE
```

Andon escalation uses:

```text
ANDON_PROBE
ANDON_ESCALATE
ANDON_HANDOFF
```

Final audit uses:

```text
AUDIT_START
AUDIT_VERIFY
AUDIT_GAPS
AUDIT_COMPLETE
IMPLEMENTAUDIT_RUN_COMPLETE
```

`AUDIT_COMPLETE` means the audit object reached terminal verified closure, not
merely that an auditing operation was attempted. `IMPLEMENTAUDIT_RUN_COMPLETE`
may appear only after `AUDIT_COMPLETE`.
`AUDIT_HANDOFF` is a handoff path only when gaps, blockers, or handoff-required caveats remain; do not print it with `IMPLEMENTAUDIT_RUN_COMPLETE`.

Use `"${IMPLEMENTAUDIT_SKILL_DIR:-skills}"/scripts/repo-state.sh` for deliverable and added-line checks when a
baseline is available. If the baseline is missing or invalid, mark the evidence
as weaker rather than claiming full release proof.

## Phase shape requirements

These rules apply to any plan that covers a full product, feature, or
operational-hardening objective. Single-surface or hotfix changes (one file,
one checker, one config tweak) may bypass them when the final audit documents
the decision.

**Rule P4-1 — Hardening phase required for full plans.**
Any plan that implements a new feature, migration, or multi-surface change must
include a final hardening phase (or operational-parity phase) unless the final
audit explicitly explains why none is needed and what covers each hardening
concern (cleanliness, error handling, fallback, identity hygiene, observability).
Absence without documentation is a gap, not a savings.

**Rule P4-2 — UI/UX visual polish evidence requirement.**
Any phase that produces visible user-facing output (web page, CLI output,
email template, generated diagram, badge) must include at least one visual
evidence requirement: screenshot, browser smoke, or visual inspection recorded
in the transcript. Passing unit tests alone are not sufficient visual proof.

**Rule P4-3 — Brownfield safety-net before risky mutation.**
Before any risky brownfield mutation — schema migration, public API change,
deletion of actively-used code, filesystem restructuring — a characterization
phase must run first. The characterization phase captures: current behavior
snapshot, coverage baseline, known-failing test catalog, and rollback proof
(`git stash pop` or `git checkout HEAD -- <paths>` tested dry). Only after that
baseline is recorded may the mutation phase proceed.

**Rule P4-4 — Package and release phases must be separate.**
Phases that *build* artifacts (compile, zip, sign) must not be merged with
phases that *publish* them (push to registry, create GitHub release, deploy).
Each has a distinct evidence boundary:
- Package evidence: locally-produced file + checksum
- Release evidence: live-registry confirmation or live-URL response
Merging these hides whether the release step actually ran.

**Rule P4-5 — Provenance boundary crossing requires fresh Smoke Before Claim.**
When work crosses a provenance boundary (local → package, package → release,
release → deployment), the receiving phase must run its own Smoke Before Claim.
It may not inherit the prior phase's evidence as proof of the new boundary.
Each boundary adds a "Remaining risk" entry if the live check is blocked.

**Rule P4-6 — Hardening phase scope restriction.**
A hardening phase must address operational concerns: cleanliness, identity
hygiene, error handling, fallback paths, monitoring hooks, or
operational-parity gaps. It must not introduce new features. If new feature
work is discovered during hardening, log it as scope creep and open a follow-up
finding. Merging feature work into a hardening phase breaks the risk boundary.

**Rule P4-7 — Skip documentation.**
Any plan that omits one of the above phase categories (hardening, safety-net,
visual polish, package/release split) must document the omission in the final
audit ledger with: category omitted, reason, and what alternative coverage
(or deliberate owner decision) justifies the skip. Undocumented omissions are
treated as unverified gaps.

**Rule P4-8 — Polish & Harden phase (optional terminal phase shape).**
A "Polish & Harden" phase is a native optional terminal phase shape in
IMPLEMENTAUDIT. It is default-recommended for:
- full plans covering a new feature, migration, or multi-surface change
- any run that produces public docs, UI, or generated artifacts
- package-boundary or release-adjacent work
- high-risk runs with many acceptance criteria

Polish & Harden phases must:
- address operational concerns only: cleanliness, generated artifact freshness,
  stale docs, dead/debug debris, UX/accessibility where relevant, proof-boundary
  wording, identity hygiene
- not introduce new feature scope (new features discovered during this phase are
  logged as scope creep and deferred)
- verify that no external comparator proper name, slash command, or marker
  appears in tracked surfaces
- run all smoke checks and mandatory commands from earlier phases

Skippable with explicit rationale in the final audit ledger documenting: what
was skipped, why, and what alternative coverage (or owner decision) justifies
the skip. Undocumented omission is treated as a gap per Rule P4-7.

Use `Type: polish-harden` in the `IMPLEMENTAUDIT_PHASE_START` block of a phase
spec to indicate this phase shape (see `skills/references/goal-format.md`).

**Rule P4-9 — Terminology cannot be orphaned.**
External method terms may appear only when attached to a native parent, phase,
route or lens, evidence boundary, Andon condition, and fixture/checker or
explicit non-mechanical boundary. Existing references own their concepts:
Lean owns A3/Poka-yoke/Standard Work/Jidoka/Andon, routing owns DMAIC/DMADV,
Plan Closure owns sustainment, and final audit owns proof. Orphan terms,
glossary-only lists, generic "apply SOLID" advice, numeric RPN theater, and
separate term lanes are phase-design defects and trigger Andon.

---

## Phase shape examples

See `fixtures/phase-design/` in the IMPLEMENTAUDIT source repo (repo-side;
not shipped in the installed package) for concrete multi-phase plan outlines:

| Fixture | Shape | Phases |
|---------|-------|--------|
| `simple-greenfield.md` | New isolated feature, no UI, no release | 3 |
| `brownfield-mutation.md` | Risky mutation of existing code | 4 |
| `ui-feature.md` | Feature with visible user output | 4 |
| `package-release.md` | Artifact build + registry publish | 4 |
| `full-hardening-run.md` | Operational parity / multi-gap hardening | 5 |

---

## Stage 6 self-critique

Before handoff or mutation through a generated phase plan, print
`Self-critique:` and check at least:

- falsifiable acceptance criteria
- phase atomicity
- weakest dependency
- owner/source clarity
- rollback/deferral path
- mandatory checks and evidence type
- generated-artifact ownership
- optional sidecar boundaries
- completion markers and final-audit path

Patch the phase artifacts before proceeding when the critique finds a gap.
Show the owner a concrete review menu before Stage 7: Start now; Adjust
assumption; Tweak a phase; Restructure phases; Abort / handoff. Do not print the
ready-to-paste handoff until Start now is explicitly selected.

## Stage 6.5 pre-flight

Deduplicate mandatory commands across phase specs and run the safe baseline set
once before Stage 7 handoff or phase-plan mutation. Print `PREFLIGHT_GREEN` or
`PREFLIGHT_RED`. Red pre-flight must classify failures as target, unrelated, or
unclear; unrelated or unclear failures require Andon or OWNER DECISION. Failed,
timed-out, hung, or substituted commands must be recorded as Andons before any
rerun/substitute is used as evidence.
