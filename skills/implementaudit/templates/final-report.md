# Final Report Template

Use for a terminal response or tracked handoff; never outrun evidence.

## Verdict

State one verdict: proven, proven with deferrals, blocked, or unverified.

## Goal

State the goal and bounded audit object.

## Input Basis

List inputs, repo files, baseline, and owner instructions.

## Findings Ledger

| # | Finding | Priority | Owner/source | Action | Status | Evidence | Follow-up |
|---|---|---:|---|---|---|---|---|

## Changed Files

Classify changed files: tracked, untracked, generated, or local-only.

## Smoke A / Smoke B

| Check | Smoke A result | Smoke B result | Evidence type | Delta | Remaining risk |
|---|---|---|---|---|---|

## Andon / Hansei

Record Andon class, cause, Hansei, countermeasure, and rerun; use "None" only
when no abnormality occurred.

## Commands Run

List commands, exits, and target/unrelated/substituted/blocked failures.

## Evidence Boundary

Bound proof across source, package, install, host, release, marketplace,
publication, licence, issue creation, and provenance.

## Claim Rows (proof-level discipline)

Give every capability/parity/surpass claim a PL1-PL7 proof level and evidence
basis (`docs/audits/RETENTION.md` in the source repo). Command properties are
`structural` / `behavioral` / `provenance`; verdict wording below PL6 states its
limit. Full/N-of-N claims add `coverage: full`, `capture`,
`population_definition`, `population_size`, `examined_count`, and mechanical or
explicit-list `enumeration_source`; partial capture cannot set the denominator.

| Claim | Scope | Proof level | Evidence basis | Freshness | Upgrade condition |
|---|---|---|---|---|---|

## Public Capability Projection (when activated)

When `references/audit-playbook.md` §Public capability projection activates,
reuse its census/discrimination contract and fill this table:

| Topic | Owner/source | README disposition | Docs disposition | Current-state transition | Evidence |
|---|---|---|---|---|---|

Private source-only changes need no row.

For new verified `api`, `user-visible`, or `publication` claims, use the exact
`external-kind`, `external-mutation-record`, `readback-sha256`, `readback-field`,
`expected-value`, `observed-value`, `artifact-identity`, `collision-receipt`, and
`external-evidence` (`closure-bytes`, `closure-mtime`) grammar in
`references/repo-state-comparison.md` and
`templates/PROTOCOL.md`; readback, not mutation output, establishes state.

For a terminal qualification, record the closure-time identity block:

```text
AUDIT_START_ANCHOR: <full-40-hex-sha>
AUDIT_VERIFY_ANCHOR: <full-40-hex-sha>
REANCHOR_DISPOSITION: unchanged|per-finding
REANCHOR_EVIDENCE: none|structured-rows
reanchor-finding: <claim-id> | disposition: reanchored | evidence-file: <relative-file> | evidence-sha256: <64-lowercase-hex>
residual: <claim-id> | consequential: yes | disposition: SUPERSEDED_BY_CONCURRENT_MUTATION | evidence-file: <relative-file> | evidence-sha256: <64-lowercase-hex>
equivalent_config_attempts: <N_total>/<N_passing>
stochasticity_budget: <N>|none
stochasticity_budget_anchor: <full-start-sha>
stochasticity_budget_path: <tracked-file>
terminal_qualification: QUALIFIED|PROVISIONAL
```

Use `templates/PROTOCOL.md` for reanchor/residual row grammar. Numeric budgets
must exist in the tracked start-anchor file; otherwise repeated equivalent draws
are `PROVISIONAL`; ordinary `1/1` is `QUALIFIED`.

## Remaining Caveats

List deferrals, owner decisions, unverified lanes, and invalidation conditions.

## Authorization Boundary

State whether commit, push, tag, release, publication, issue creation, licence,
real-home install, marketplace, or provenance was authorised or performed.

## Suggested Commit Message When No Commit Authorized

```text
<subject>
Class: B | M
Finding: <finding>
Countermeasure: <change>
Evidence: <checks>
Evidence anchor: claim:<Claim-ID>
Linkage: #<issue> | ledger-row:<id> | Andon:<id> | not-applicable
Boundaries: No commit, push, tag, release, publication, issue creation, license
choice, real-home install, marketplace claim, or provenance unless authorised.
```

## Terminal Marker Order

For skill-governed runtime sessions, `AUDIT_COMPLETE` must appear before
`IMPLEMENTAUDIT_RUN_COMPLETE`. Do not print completion markers with
`AUDIT_HANDOFF` or `ANDON_HANDOFF`.
