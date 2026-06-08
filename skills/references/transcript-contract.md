# Transcript Contract

Use this reference when a host, wrapper, or `/goal` evaluator needs to inspect
ImplementAudit transcript state without reading the full skill.

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

## Failure recovery markers

```text
FAILURE_PROBE
FAILURE_ESCALATE
FAILURE_HANDOFF
```

The three-strike sequence is ordered: FAILURE_PROBE → FAILURE_ESCALATE →
FAILURE_HANDOFF. Skipping to FAILURE_HANDOFF on the first failure is invalid.

- **FAILURE_PROBE** (Strike 1): emitted on the first criterion failure; names
  the failing criterion, failing command, observed output, and smallest
  reproducible step. STATE.md is updated. A targeted inline fix is attempted.
  If the fix succeeds, the phase resumes; no new marker is needed.

- **FAILURE_ESCALATE** (Strike 2): emitted when Strike 1's fix attempt also
  fails. Includes Hansei analysis. A `phase-N.fix.md` is written targeting
  only the failing criterion (no scope expansion). Fix spec ends with the
  original VERIFY gate. On success, phase resumes from IMPLEMENTAUDIT_PHASE_VERIFY.

- **FAILURE_HANDOFF** (Strike 3): emitted when Strike 2's fix spec also fails.
  Includes full probe history. STATE.md set to BLOCKED. Phase done with
  `Status: blocked`. Run stops. No subsequent phases execute.

`FAILURE_HANDOFF` is terminal for the current run. A transcript containing
`FAILURE_HANDOFF` must not also contain `IMPLEMENTAUDIT_RUN_COMPLETE`.
STATE.md `Status: BLOCKED` must be set before the run stops.

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
- `AUDIT_COMPLETE` means the audit object reached terminal verified closure; it
  does not merely mean the runtime performed an audit operation.
- `AUDIT_HANDOFF` appears only when gaps, blockers, or handoff-required caveats
  remain.
- `AUDIT_HANDOFF` must not appear with `IMPLEMENTAUDIT_RUN_COMPLETE`.
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

Run:

```bash
bash scripts/check-marker-order.sh fixtures/simple-audit/EXPECTED-TRANSCRIPT-SKELETON.md
```

The validator checks marker ordering and rejects handoff/failure transcripts
that also claim run completion.
