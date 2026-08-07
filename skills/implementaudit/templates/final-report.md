# Final Report Template

Use this template for a terminal response or tracked handoff when the run needs
a consolidated audit report. Do not invent stronger proof than the evidence
supports.

## Verdict

Choose one explicit verdict and state whether it is proven, proven with
deferrals, blocked, or unverified.

## Goal

State the user goal and the bounded audit object.

## Input Basis

List the audit, handoff, attachments, repo files, baseline ref, and owner
instructions used as input.

## Findings Ledger

| # | Finding | Priority | Owner/source | Action | Status | Evidence | Follow-up |
|---|---|---:|---|---|---|---|---|

## Changed Files

List changed files and classify tracked, untracked, generated, or local-only.

## Smoke A / Smoke B

| Check | Smoke A result | Smoke B result | Evidence type | Delta | Remaining risk |
|---|---|---|---|---|---|

## Andon / Hansei

Record any Andon, abnormality class, root cause, Hansei, countermeasure, and
rerun evidence. Say "None" only when no abnormality occurred.

## Commands Run

List exact commands, exit status, and whether failures were target, unrelated,
substituted-command, or blocked.

## Evidence Boundary

State what the run proves and what it does not prove: local source, package,
install-copy smoke, live host execution, public release, marketplace,
publication, license, issue creation, or provenance.

## Claim Rows (proof-level discipline)

Every capability, parity, or surpass claim this report makes or repeats
carries an explicit proof level (PL1-PL7 taxonomy, `docs/audits/RETENTION.md`
in the source repo) and its evidence basis. Per-command evidence properties
(`structural` / `behavioral` / `provenance`) are the low-level building
blocks: they classify commands, proof levels classify claims. Do not use
verdict-class wording (PROVEN / SURPASSED) below PL6 without stating what
the claim is not.

A claim using all, every, complete, no remaining, none remaining, N of N, or
N/N carries `coverage: full`, a concrete `capture`, and the census group
`population_definition`, `population_size`, `examined_count`, plus a mechanical
or explicit-list `enumeration_source`. Partial or truncated capture cannot
establish the denominator. Omit the census group for ordinary claims and
labelled samples; an honest M-of-N claim remains partial corpus coverage.

| Claim | Scope | Proof level | Evidence basis | Freshness | Upgrade condition |
|---|---|---|---|---|---|

For each new verified `api`, `user-visible`, or `publication` claim, add
`external-kind: observation|mutation`. A mutation claim links
`external-mutation-record: <id>` to one target-bound record with
`runner`, `target-kind`, `target-id`, `mutation-command`, `mutation-exit: 0`,
`mutation-evidence`, distinct `readback-command`, `readback-exit: 0`, bare JSON
`readback-file`, recomputed `readback-sha256`, one top-level `readback-field`,
equal scalar `expected-value` and `observed-value`, and a distinct
`readback-evidence`. The read-back, not the mutator's output, establishes the
external state.

When artifact names or out-of-repo inputs support a claim, include the same
record vocabulary used by the protocol: `artifact-identity` plus an exact
`collision-receipt` for a same-name distinct-hash set, and `external-evidence`
with `bytes`, `mtime`, `liveness`, `still-producing`, `use`, `closure-bytes`,
and `closure-mtime`. Legacy rows without these new prefixes remain valid.

For a terminal qualification, record the closure-time identity block:

```text
AUDIT_START_ANCHOR: <full-40-hex-sha>
AUDIT_VERIFY_ANCHOR: <full-40-hex-sha>
REANCHOR_DISPOSITION: unchanged|per-finding
REANCHOR_EVIDENCE: none|structured-rows
reanchor-finding: <claim-id> | disposition: reanchored | evidence-file: <relative-file> | evidence-sha256: <64-lowercase-hex>
residual: <claim-id> | consequential: yes | disposition: SUPERSEDED_BY_CONCURRENT_MUTATION | evidence-file: <relative-file> | evidence-sha256: <64-lowercase-hex>
equivalent_config_attempts: <N_total>/<N_passing>
stochasticity_budget: <positive-integer>|none
stochasticity_budget_anchor: <full-start-sha>
stochasticity_budget_path: <tracked-repo-relative-declaration-file>
terminal_qualification: QUALIFIED|PROVISIONAL
```

Anchor drift requires exactly one hash-bound evidence row for every claim:
either re-anchored or a consequential concurrent-mutation residual. A numeric
stochasticity budget is predeclared only when its exact declaration exists in
the named tracked file at `AUDIT_START_ANCHOR`. More than one
equivalent-configuration draw without that proof is `PROVISIONAL`; an ordinary
`1/1` terminal is `QUALIFIED`.

## Remaining Caveats

List deferrals, owner decisions, unverified lanes, and future invalidation
conditions.

## Authorization Boundary

State whether commit, push, tag, release, publication, issue creation, license
selection, real-home install, marketplace claim, or provenance was authorized
or performed.

## Suggested Commit Message When No Commit Authorized

```text
<subject>

Finding:
- <finding>

Countermeasure:
- <change>

Evidence:
- <checks>

Evidence anchor: claim:<Claim-ID>

Boundaries:
- No commit, push, tag, release, publication, issue creation, license choice,
  real-home install, marketplace claim, or provenance unless separately
  authorized.
```

## Terminal Marker Order

For skill-governed runtime sessions, `AUDIT_COMPLETE` must appear before
`IMPLEMENTAUDIT_RUN_COMPLETE`. Do not print completion markers with
`AUDIT_HANDOFF` or `ANDON_HANDOFF`.
