# IMPLEMENTAUDIT Protocol

Runtime copy target: `.IMPLEMENTAUDIT/PROTOCOL.md`

## Phase loop

Before executing phase 1, read:

```text
.IMPLEMENTAUDIT/ROADMAP.md
.IMPLEMENTAUDIT/STATE.md
.IMPLEMENTAUDIT/THINKING.md
.IMPLEMENTAUDIT/PROTOCOL.md
```

Use `THINKING.md` as reviewable planning evidence for objective, route,
owner/source, risks, dependencies, rollback, evidence strategy, generated
artifacts, optional sidecar boundaries, and owner decisions. It is not proof by
itself.

Each phase prints these transcript markers:

```text
IMPLEMENTAUDIT_PHASE_START
IMPLEMENTAUDIT_PHASE_VERIFY
AGENTS_UPDATE_DECISION
IMPLEMENTAUDIT_PHASE_DONE
```

`IMPLEMENTAUDIT_PHASE_VERIFY` includes acceptance criteria, checks, evidence
types, and a cleanliness readback against the baseline ref.

Use complete working-tree comparison for cleanliness when the helper is
available:

```bash
bash skills/scripts/repo-state.sh added-lines <Baseline ref>
bash skills/scripts/repo-state.sh changed-files <Baseline ref>
```

This includes committed-after-baseline, staged, unstaged, deleted, and
untracked text changes. If the helper or baseline is unavailable, state the
weaker evidence type and remaining risk.

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
IMPLEMENTAUDIT_RUN_COMPLETE
```

Handoff path:

```text
AUDIT_HANDOFF
```

Rules:

- `AUDIT_COMPLETE` must precede `IMPLEMENTAUDIT_RUN_COMPLETE`.
- `AUDIT_HANDOFF` is conditional: print it only when gaps, blockers, or handoff-required caveats remain.
- Do not print `AUDIT_HANDOFF` with `IMPLEMENTAUDIT_RUN_COMPLETE`.
- `IMPLEMENTAUDIT_RUN_COMPLETE` appears only when every phase and ledger item is
  terminally closed.
- If final audit finds gaps, write `.IMPLEMENTAUDIT/phases/audit-fix-<round>.md`
  when phase planning was used.
- Check deliverables with `bash skills/scripts/repo-state.sh deliverable <Baseline ref> <path>` when available.
- Warn when more than 30% of checks are `trust-prior-verify`.
- If any final-audit command fails, hangs, times out, or is replaced by a rerun
  or substitute path, record an Andon before closing it as blocking or
  non-blocking.
