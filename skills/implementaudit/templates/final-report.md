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

| Claim | Scope | Proof level | Evidence basis | Freshness | Upgrade condition |
|---|---|---|---|---|---|

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

Boundaries:
- No commit, push, tag, release, publication, issue creation, license choice,
  real-home install, marketplace claim, or provenance unless separately
  authorized.
```

## Terminal Marker Order

For skill-governed runtime sessions, `AUDIT_COMPLETE` must appear before
`IMPLEMENTAUDIT_RUN_COMPLETE`. Do not print completion markers with
`AUDIT_HANDOFF` or `ANDON_HANDOFF`.
