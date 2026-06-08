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

### Concrete per-phase execution loop

Execute these steps for every phase N, in order:

**Step 1 — Read STATE.md.**
Confirm `Current phase` matches N. If STATE.md shows a different current phase,
do not execute phase N; instead report the discrepancy and wait for owner
clarification.

**Step 2 — Read phase spec.**
Read `<run-root>/phases/phase-N.md` in full. Confirm `IMPLEMENTAUDIT_PHASE_START`
block is present. If the file is missing or the marker is absent, stop and
report Andon with the missing artifact path.

**Step 3 — Validate phase spec.**
Run `bash skills/scripts/validate-phase.sh <run-root>/phases/phase-N.md`.
Exit code must be 0. If not, stop and report the validation error before
proceeding. Do not execute a phase against an invalid spec.

**Step 4 — Print IMPLEMENTAUDIT_PHASE_START.**
Echo the Phase N header line, Task, Type, Run root, Baseline ref, Owner/source,
and Audit object from the spec. This signals the start of verifiable transcript
evidence for this phase.

**Step 5 — Smoke A (before-state evidence).**
Run or inspect the before-state for the owner/source. Record exactly:
Command, Result, Evidence type, Remaining risk. Do not upgrade static evidence
to live proof.

**Step 6 — Execute the work.**
Implement or verify as described in the `## Work` section. Patch the
owner/source, not the nearest symptom. Follow generator-first policy for
generated artifacts. Log scope creep as new findings rather than absorbing it.

**Step 7 — Run mandatory commands.**
For each command in `## Mandatory commands`, run it and surface the last ~10
lines of output plus the exit code. Record each result as pass or fail.
A failed, timed-out, hung, or substituted command is not pass evidence; record
an Andon before using any rerun or substitute.

**Step 8 — Evaluate acceptance criteria.**
For each item in `## Acceptance criteria`, record `[pass]` or `[fail]` with
evidence. A criterion fails if the evidence is absent, weaker than stated, or
requires an undisclosed assumption. Failures trigger the failure recovery
ladder (see below) before proceeding.

**Step 9 — Cleanliness check.**
Run:
```bash
bash skills/scripts/repo-state.sh added-lines <Baseline ref>
bash skills/scripts/repo-state.sh changed-files <Baseline ref>
```
This covers committed-after-baseline, staged, unstaged, deleted, and untracked
changes. Record: debug prints added, session debug-markers added
(todo/fixme/xxx), dead imports added. If the helper or baseline is unavailable,
state the weaker evidence type and remaining risk.

**Step 10 — Smoke B (after-state evidence).**
Re-run or re-inspect the owner/source after all changes. Compare with Smoke A.
Record the delta as the evidence that the phase work actually landed.

**Step 11 — Print IMPLEMENTAUDIT_PHASE_VERIFY.**
Include: per-criterion verdicts, mandatory-command outputs, cleanliness
readback, sidecar status (Graphify used/skipped/avoided; ActiveGraph
used/skipped/avoided; Markdown fallback yes/no), remaining risk, trust-prior
count, re-verified count.

**Step 12 — Evaluate AGENTS_UPDATE_DECISION.**
Ask: does this phase produce a durable, repo-local rule stable enough for
`AGENTS.md`? If yes, write or update the entry. If no, write "not warranted."
Speculative or session-specific observations do not qualify.

**Step 13 — Print AGENTS_UPDATE_DECISION.**
Record: Decision, Reason, Scope, Evidence location, Conflict or owner-decision
note.

**Step 14 — Evaluate CONTINUITY_DECISION.**
Ask: is there a non-obvious cross-session learning worth persisting beyond
`AGENTS.md`? Durable repo-local rules already written in Step 12 do not need
a second continuity entry.

**Step 15 — Print CONTINUITY_DECISION.**
Record: Decision, Reason, Evidence boundary.

**Step 16 — Print IMPLEMENTAUDIT_PHASE_DONE.**
Record: Status (done / changed / blocked / deferred / unverified), Evidence,
Follow-up. Then update STATE.md: mark phase N as done, set Current phase to
N+1. Check for mid-run interruption (see §"Mid-run interruption" below) before
continuing to phase N+1.

## Mid-run interruption

A mid-run interruption is any user message that arrives while a phase is in
progress (after IMPLEMENTAUDIT_PHASE_START but before IMPLEMENTAUDIT_PHASE_DONE).

### Pause at the nearest safe boundary

Do not abandon work mid-phase. Finish the current phase step if it is
near-complete and the step is safe (read-only, idempotent, or already committed).
Then stop at the phase boundary and report status before handling the
interruption.

Print:

```text
IMPLEMENTAUDIT_PAUSE
Phase: N
Status: paused at boundary / paused mid-step
Last completed step: <step name from per-phase loop>
STATE.md: updated / not updated (reason)
```

Update STATE.md to reflect the pause state before responding to the interruption.

### Handle the interruption

Respond to the user's message. Options the agent must offer:

1. **Resume** — continue from the paused step; re-read phase spec from disk.
2. **Revise spec** — the user changes `phases/phase-N.md`; agent re-validates
   with `validate-phase.sh` before resuming.
3. **Skip phase** — owner decision; mark the phase as `deferred` in STATE.md
   with reason; continue to phase N+1.
4. **Stop** — owner requests halt; set STATE.md `Status: INTERRUPTED`; record
   the interruption point in `## Failure log`.

Do not restart from phase 1 unless the user explicitly requests it.

### Resume contract

When resuming after interruption:
1. Re-read `<run-root>/STATE.md`, `<run-root>/phases/phase-N.md`, and
   `<run-root>/THINKING.md` from disk.
2. Re-validate the phase spec with `validate-phase.sh`.
3. Re-state where the loop is resuming from (which numbered step).
4. Do not re-print IMPLEMENTAUDIT_PHASE_START; it was already printed.
5. Continue from the paused step, not from Step 1.

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
close. Each strike is sequential; do not skip to FAILURE_HANDOFF on the first
failure.

```text
FAILURE_PROBE
FAILURE_ESCALATE
FAILURE_HANDOFF
```

### Strike 1 — FAILURE_PROBE

Trigger: any acceptance criterion in `## Acceptance criteria` cannot be met
after the first execution attempt.

Steps:
1. Print `FAILURE_PROBE` with: phase number, failing criterion, failing command
   or check, observed output, and smallest reproducible step.
2. Append a Failure entry to `<run-root>/STATE.md` under `## Failure log`:
   phase, criterion, probe summary, timestamp or sequence number.
3. Inspect the owner/source file directly (Gemba). Do not infer from summaries.
4. Attempt the smallest safe fix targeting only the failing criterion.
5. Re-run the failing mandatory command and evaluate the criterion again.
6. If the criterion now passes, resume the phase from Step 8 (evaluate
   acceptance criteria) of the per-phase loop. Do not restart the full phase.
7. If the criterion still fails, escalate to Strike 2.

### Strike 2 — FAILURE_ESCALATE

Trigger: the criterion still fails after Strike 1's fix attempt.

Steps:
1. Print `FAILURE_ESCALATE` with: phase number, failing criterion, Strike 1
   fix attempted, Strike 1 result, Hansei analysis (gap, cause, countermeasure,
   follow-up evidence).
2. Write `<run-root>/phases/phase-N.fix.md`:
   - Target only the failing criterion; do not expand scope.
   - Forbidden: adding new features, restructuring unrelated code, or changing
     passing criteria.
   - The fix spec must end with the original `IMPLEMENTAUDIT_PHASE_VERIFY`
     gate from phase-N.md (same criteria, same commands).
3. Execute the fix spec inline (read it from disk, do not rely on chat context).
4. Re-run the original mandatory commands from phase-N.md.
5. Re-evaluate all acceptance criteria (including the one that was failing).
6. If all criteria now pass, resume from Step 11 (print IMPLEMENTAUDIT_PHASE_VERIFY)
   of the per-phase loop. Record the fix in STATE.md.
7. If any criterion still fails, escalate to Strike 3.

### Strike 3 — FAILURE_HANDOFF

Trigger: the criterion still fails after Strike 2's fix spec execution.

Steps:
1. Print `FAILURE_HANDOFF` with: phase number, failing criterion, full probe
   history (Strike 1 + Strike 2 attempts and results), remaining blocker, and
   smallest next concrete action for a human owner.
2. Set `<run-root>/STATE.md` `Status: BLOCKED` and record the failure in
   `## Failure log`.
3. Print `IMPLEMENTAUDIT_PHASE_DONE` with `Status: blocked`.
4. Stop. Do not continue to subsequent phases.
5. Do not print `IMPLEMENTAUDIT_RUN_COMPLETE` after `FAILURE_HANDOFF`.

The phase remains `blocked` until the owner resolves the underlying cause and
restarts the phase.

## Final audit

Execute after the last phase completes. The final audit may run up to 3 rounds.
Each round prints one of: `AUDIT_COMPLETE` (success) or `AUDIT_GAPS` (gaps
found, triggering an audit-fix round).

### AUDIT_START

Print `AUDIT_START` with:
- Round number (1, 2, or 3)
- Criteria count: total acceptance criteria being re-verified across all phases
- Command list: deduplicated mandatory commands to re-run
- Baseline ref

Re-read the original `<run-root>/ROADMAP.md` from disk. Do not rely on earlier
reading from this session or from phase-level self-reports. This is the
definitive phase and deliverable list.

### Phase completeness check

For each phase in ROADMAP.md, verify that `<run-root>/STATE.md` shows status
`done` and that the corresponding phase spec (`phases/phase-N.md`) contains
`IMPLEMENTAUDIT_PHASE_DONE` in the transcript evidence. Any phase missing
`IMPLEMENTAUDIT_PHASE_DONE` is a gap.

### Mandatory command re-run

Re-run the deduplicated mandatory command set. Surface last ~10 lines + exit
code for each. Record each as: re-verified (ran fresh this round) or
trust-prior (accepted from prior-phase evidence without re-running).

If any command fails, hangs, times out, or is replaced by a rerun or substitute,
record an Andon before classifying the result as blocking or non-blocking.

### Deliverable check

For each deliverable listed in ROADMAP.md, run:

```bash
bash skills/scripts/repo-state.sh deliverable <Baseline ref> <path>
```

Record: exists, non-empty, changed-since-baseline. If the helper is unavailable,
record the weaker evidence type and remaining risk.

### AUDIT_VERIFY

Print `AUDIT_VERIFY` with: per-phase status (done / blocked / missing), per-
deliverable existence check, mandatory-command re-run results.

### Coverage math

Compute and print:

```
re_verified / (re_verified + trust_prior) = <fraction>
```

If `trust_prior / (re_verified + trust_prior) > 0.30`, print:

```
AUDIT_WARNING: trust-prior > 30% — consider re-running flagged commands
```

### AUDIT_GAPS and audit-fix rounds

If any gap is found (missing phase, missing deliverable, failing command, or
failing criterion):

1. Print `AUDIT_GAPS` with: each gap, severity (blocking / non-blocking),
   and proposed fix.
2. Write `<run-root>/phases/audit-fix-<round>.md` with a phase spec targeting
   only the blocking gaps. Forbidden: expanding scope, adding features, or
   changing non-failing criteria.
3. Execute the audit-fix spec inline.
4. Return to AUDIT_START for round N+1.

Maximum 3 rounds. If blocking gaps remain after round 3, print `AUDIT_HANDOFF`
instead of `AUDIT_COMPLETE`.

### AUDIT_COMPLETE and IMPLEMENTAUDIT_RUN_COMPLETE

Print `AUDIT_COMPLETE` only when:
- Every phase in ROADMAP.md has `IMPLEMENTAUDIT_PHASE_DONE` with status done or
  explicitly deferred with owner decision
- Every deliverable exists and is non-empty
- No blocking gaps remain
- Coverage math printed

Then print `IMPLEMENTAUDIT_RUN_COMPLETE`.

### AUDIT_HANDOFF

Print `AUDIT_HANDOFF` (instead of `AUDIT_COMPLETE`) when:
- Blocking gaps remain after 3 rounds, or
- An unresolvable FAILURE_HANDOFF prevents a phase from closing, or
- The owner requests handoff before completion

`AUDIT_HANDOFF` must not appear with `IMPLEMENTAUDIT_RUN_COMPLETE`.

### Ordering rules

- `AUDIT_COMPLETE` must precede `IMPLEMENTAUDIT_RUN_COMPLETE`.
- `AUDIT_COMPLETE` means verified terminal closure, not merely a completed
  audit operation.
- `IMPLEMENTAUDIT_RUN_COMPLETE` appears only when every in-scope ledger item
  is terminally closed.
- Do not print `IMPLEMENTAUDIT_RUN_COMPLETE` if `FAILURE_HANDOFF` or
  `AUDIT_HANDOFF` appeared in the transcript.
