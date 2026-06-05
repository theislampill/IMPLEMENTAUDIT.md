# Phase Design

Use phases when a supplied audit or synthesized goal is too large, risky, or
dependent to close as one atomic implementation pass.

## Phase rules

- Each phase must close one coherent slice of audit risk.
- Each phase needs an owner/source, acceptance criteria, Smoke A, Smoke B, and
  a rollback or deferral path.
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
AUDIT_HANDOFF
IMPLEMENTAUDIT_RUN_COMPLETE
```

`IMPLEMENTAUDIT_RUN_COMPLETE` may appear only after `AUDIT_COMPLETE`.
