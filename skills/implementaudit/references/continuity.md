# Context-epoch continuity (#35)

Long runs cross automatic context compactions, new sessions, manual resumes,
and handoffs. The run root holds durable state; a compacted or reconstructed
summary is an OBSERVATION OF HISTORY, not current-state authority. This
reference governs re-entry: no repository mutation after a continuity
boundary until the reconciliation below has run, and no replay of a
satisfied one-shot instruction, ever.

## Continuity boundaries and epochs

A continuity boundary is any event after which working context may no longer
match durable live state. Each boundary starts a new CONTEXT EPOCH, recorded
as a row in STATE.md `## Context epochs and instruction applicability`.
Boundary provenance is exactly one of:

```text
host-reported-compaction
new-session
handoff-resume
manual-resume
inferred-context-gap
```

Never fabricate a compaction the host did not expose: when no host signal
exists but continuity is in doubt, the honest provenance is
`inferred-context-gap`. An uninterrupted turn crosses no boundary and MUST
NOT add epoch ceremony.

## Post-boundary reconciliation (required before mutation)

After any continuity boundary, and before the next repository mutation:

1. Establish the unique active run root and the current repository identity
   (repo root + HEAD; for non-Git subjects, the declared inventory).
   Ambiguous or multiple candidate run roots route to an audited handoff —
   never guess. No run root at all means truthful intake, not fabricated
   recovery.
2. Reread current `ROADMAP.md`, `STATE.md`, process/command state (including
   `background/<chain-id>` chains), and the relevant terminal evidence from
   disk.
3. Classify continuity-critical instructions by lifecycle kind and target
   (see the applicability record below).
4. Compare the reconstructed context against durable live state. Where they
   disagree, LIVE STATE WINS; the reconstructed summary never reopens
   terminal evidence.
5. Refuse replay of a satisfied or superseded one-shot instruction. The
   refusal cites the terminal evidence (`Target already satisfied at
   <evidence>; no duplicate action taken.`).
6. Restore the current next authorized action from STATE.md and continue
   from there — never restart the run because context was reconstructed.
7. When continuity cannot be established (identity mismatch, corrupted
   state, irreconcilable instruction set), hand off with the evidence rather
   than speculate.

The reconciliation is recorded by the new epoch row (provenance, repository
identity at establishment, reconciled: yes). No new transcript marker
exists for this: the epoch row plus the existing pause/resume markers are
the record.

## Instruction lifecycle and applicability record

Instruction kinds:

```text
one-shot-action
standing-constraint
standing-authorization
persistent-objective
query-or-information-request
```

Statuses: `active` / `satisfied` / `superseded` / `revoked` / `expired` /
`ambiguous`. Only a one-shot action normally becomes `satisfied`. Standing
constraints and authorizations survive boundaries until revoked, superseded,
expired, or their declared scope ends — reconciliation must not accidentally
consume them (a "do not push" constraint issued before a compaction still
binds after it; a scoped commit authorization stays scoped and active).

Each continuity-critical instruction gets one applicability row binding:
instruction id; source reference (event id / content hash — never raw
conversation text in a committed artifact); kind; issuing authority;
subject identity (and subject version when applicable); issued epoch;
status; status evidence; supersedes/superseded-by links; scope end or
expiry when applicable. Preconditions and the terminal predicate live in
the status-evidence cell (what would prove this satisfied/expired).

## Repeated current owner message

An identical NEW owner message is a fresh authority event, not automatically
a stale replay. If its target is already terminally satisfied, respond:
"Target already satisfied at <evidence>; no duplicate action taken. Current
open state is <state>." Reactivation requires an explicit reopen/re-audit
instruction, a changed target, or new evidence sufficient to invalidate the
terminal status — and it is recorded as a new instruction row, never by
rewriting the satisfied row's history.

## Continuity capsule

When a boundary is crossed, the re-entry summary ("capsule") binds to
CURRENT state: current repository identity, current epoch id, current next
authorized action, and the active (not satisfied/superseded) instruction
set. Every capsule field rederives from live source owners at write time;
a capsule inherited from an earlier epoch is itself reconstructed context
and re-verifies against live state before use.

## Single-writer epoch claim

Two concurrent resume attempts must not both mutate: at most one writer
establishes the new epoch (create-once epoch row / run-root claim
semantics). The loser observes the existing claim and routes to
handoff-or-wait, never to a second parallel epoch.

## Migration

Legacy run roots (no epoch section) remain valid and resumable; the section
becomes required only for NEW epochs established after the feature version.
The first resume of a legacy root may create the initial epoch row after
validating existing durable state. No full conversation text is ever copied
into the run root; references are ids/hashes under the existing
custody/privacy boundary.
