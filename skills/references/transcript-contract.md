# Transcript Contract

Use this reference when a host, wrapper, or `/goal` evaluator needs to inspect
ImplementAudit transcript state without reading the full skill.

The transcript contract is an execution boundary. It is not a release,
publication, provenance, install, Graphify indexing, or ActiveGraph export
claim.

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
- `IMPLEMENTAUDIT_PHASE_DONE` closes the phase.

## Failure recovery markers

```text
FAILURE_PROBE
FAILURE_ESCALATE
FAILURE_HANDOFF
```

`FAILURE_HANDOFF` is terminal for the current run. A transcript containing
`FAILURE_HANDOFF` must not also contain `IMPLEMENTAUDIT_RUN_COMPLETE`.

## Final audit markers

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
- `AUDIT_HANDOFF` appears only when gaps, blockers, or handoff-required caveats
  remain.
- `AUDIT_HANDOFF` must not appear with `IMPLEMENTAUDIT_RUN_COMPLETE`.
- `IMPLEMENTAUDIT_RUN_COMPLETE` appears only after final audit has closed every
  in-scope ledger item terminally.
- If the final audit finds gaps, use an audit-fix round or handoff instead of
  printing completion.

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

Run:

```bash
bash scripts/check-marker-order.sh fixtures/simple-audit/EXPECTED-TRANSCRIPT-SKELETON.md
```

The validator checks marker ordering and rejects handoff/failure transcripts
that also claim run completion.
