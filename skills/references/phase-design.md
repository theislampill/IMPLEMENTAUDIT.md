# Phase Design

Use phases when a supplied audit or synthesized goal is too large, risky, or
dependent to close as one atomic implementation pass.

## Phase rules

- Each phase must close one coherent slice of audit risk.
- Each phase needs an owner/source, acceptance criteria, Smoke A, Smoke B, and
  a rollback or deferral path.
- Stage 4 derives the phase count from dependencies, risk, and evidence shape;
  do not merge unrelated work to fit an artificial count.
- Stage 5 writes `.IMPLEMENTAUDIT/ROADMAP.md`, `.IMPLEMENTAUDIT/STATE.md`,
  `.IMPLEMENTAUDIT/THINKING.md`, `.IMPLEMENTAUDIT/PROTOCOL.md`, and one
  `.IMPLEMENTAUDIT/phases/phase-N.md` file per phase when phase planning is
  selected.
- Final audit and cleanliness checks use complete working-tree comparison
  against the phase baseline when available.
- `P0` work precedes `P1`; `P1` precedes `P2` unless a dependency demands a
  different order.
- Generated artifacts follow generator-first policy.
- Scope creep is logged instead of silently absorbed.
- A blocked dependency defers dependents; it does not license guesswork.
- There is no artificial phase-count cap. Use as many phases as evidence and
  rollback safety require.

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

Failure recovery uses:

```text
FAILURE_PROBE
FAILURE_ESCALATE
FAILURE_HANDOFF
```

Final audit uses:

```text
AUDIT_START
AUDIT_VERIFY
AUDIT_GAPS
AUDIT_COMPLETE
IMPLEMENTAUDIT_RUN_COMPLETE
```

`IMPLEMENTAUDIT_RUN_COMPLETE` may appear only after `AUDIT_COMPLETE`.
`AUDIT_HANDOFF` is a handoff path only when gaps, blockers, or handoff-required caveats remain; do not print it with `IMPLEMENTAUDIT_RUN_COMPLETE`.

Use `skills/scripts/repo-state.sh` for deliverable and added-line checks when a
baseline is available. If the baseline is missing or invalid, mark the evidence
as weaker rather than claiming full release proof.

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

## Stage 6.5 pre-flight

Deduplicate mandatory commands across phase specs and run the safe baseline set
once before Stage 7 handoff or phase-plan mutation. Print `PREFLIGHT_GREEN` or
`PREFLIGHT_RED`. Red pre-flight must classify failures as target, unrelated, or
unclear; unrelated or unclear failures require Andon or OWNER DECISION.
