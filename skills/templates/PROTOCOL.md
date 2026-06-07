# IMPLEMENTAUDIT Protocol

Runtime copy target: `.IMPLEMENTAUDIT/runs/<task-slug>-<id>/PROTOCOL.md`

## Phase loop

Before executing phase 1, read:

```text
<run-root>/ROADMAP.md
<run-root>/STATE.md
<run-root>/THINKING.md
<run-root>/PROTOCOL.md
<run-root>/context.md
<run-root>/tools.md
<run-root>/sidecars.md
<run-root>/applied-context.md or <run-root>/applied-memories.md
```

Use `THINKING.md` as reviewable planning evidence for objective, route,
owner/source, risks, dependencies, rollback, evidence strategy, generated
artifacts, optional sidecar boundaries, and owner decisions. It is not proof by
itself.

The runtime audit object, `tdqyq-audit-object`, is the evidence-bearing record
for this run: roadmap, state, phase specs, ledger items, owner/source decisions,
Smoke A/B evidence, Andons, handoffs, and terminal verification state.
`ydqyq-audit-action` operations mutate, verify, classify, close, or hand off
against that object.

For release-affecting, multi-phase, package-boundary, provenance, or public-claim
work, use the double-audit pattern:

1. Produce or update the audit object with findings, owner/source, allowed
   scope, evidence needs, and release/package/claim boundaries.
2. Act against that audit object through implementation, rebuild, repair,
   rejection, or handoff.
3. Run final auditing operations to verify the object's terminal state before
   `AUDIT_COMPLETE`.

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

## Sidecars and continuity

Read `<run-root>/sidecars.md` before using Graphify or ActiveGraph. Graphify
output is orientation evidence, not proof. ActiveGraph custody is not correctness
proof. Missing, stale, or unauthorized sidecars must route to Markdown fallback
and ordinary Gemba; they must not block the run.

At each phase boundary, print `CONTINUITY_DECISION` only when a non-obvious,
future-useful learning is found. Durable repo-local rules belong in `AGENTS.md`
only when stable and repo-specific. Memory/continuity writeback is read-only
until warranted, evidence-bound, and safe; never write secrets, raw logs,
private diagnostics, transient dirty state, or unsupported claims.

Capability Ledger entries, when ActiveGraph is configured and authorized, are
derived only from recorded gate passages, Smoke A/B, Andons, authorization
decisions, ledger closures, and final audit evidence. Do not claim broad
competence from one run.

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
- `AUDIT_COMPLETE` means the audit object reached terminal verified closure; it
  is not merely a label for having done another review pass.
- `AUDIT_HANDOFF` is conditional: print it only when gaps, blockers, or handoff-required caveats remain.
- Do not print `AUDIT_HANDOFF` with `IMPLEMENTAUDIT_RUN_COMPLETE`.
- `IMPLEMENTAUDIT_RUN_COMPLETE` appears only when every phase and ledger item is
  terminally closed.
- If final audit finds gaps, write `<run-root>/phases/audit-fix-<round>.md`
  when phase planning was used.
- Check deliverables with `bash skills/scripts/repo-state.sh deliverable <Baseline ref> <path>` when available.
- Warn when more than 30% of checks are `trust-prior-verify`.
- If any final-audit command fails, hangs, times out, or is replaced by a rerun
  or substitute path, record an Andon before closing it as blocking or
  non-blocking.
