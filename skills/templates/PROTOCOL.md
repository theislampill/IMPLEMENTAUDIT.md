# IMPLEMENTAUDIT Protocol

Runtime copy target: `.IMPLEMENTAUDIT/PROTOCOL.md`

## Phase loop

Each phase prints these transcript markers:

```text
IMPLEMENTAUDIT_PHASE_START
IMPLEMENTAUDIT_PHASE_VERIFY
AGENTS_UPDATE_DECISION
IMPLEMENTAUDIT_PHASE_DONE
```

`IMPLEMENTAUDIT_PHASE_VERIFY` includes acceptance criteria, checks, evidence
types, and a cleanliness readback against the baseline ref.

## Failure recovery

Use the three-strike recovery ladder when a phase criterion cannot honestly
close:

```text
FAILURE_PROBE
FAILURE_ESCALATE
FAILURE_HANDOFF
```

- `FAILURE_PROBE`: inspect owner/source and smallest failing check.
- `FAILURE_ESCALATE`: run Hansei, identify the countermeasure or owner decision.
- `FAILURE_HANDOFF`: stop the phase with evidence, blocker, and next action.

## Final audit

The final audit prints:

```text
AUDIT_START
AUDIT_VERIFY
AUDIT_GAPS
AUDIT_COMPLETE
AUDIT_HANDOFF
IMPLEMENTAUDIT_RUN_COMPLETE
```

Rules:

- `AUDIT_COMPLETE` must precede `IMPLEMENTAUDIT_RUN_COMPLETE`.
- `IMPLEMENTAUDIT_RUN_COMPLETE` appears only when every phase and ledger item is
  terminally closed.
- If final audit finds gaps, write `.IMPLEMENTAUDIT/phases/audit-fix-<round>.md`
  when phase planning was used.
- Warn when more than 30% of checks are `trust-prior-verify`.
