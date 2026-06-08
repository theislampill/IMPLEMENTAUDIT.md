# IMPLEMENTAUDIT.md

An audit-governed implementation skill for turning findings, handoffs, checklists,
reviews, goals, and plans into bounded, verified repository changes — with evidence
for every claim.

Source file for the docs portal. Generated into _site/index.html by
scripts/build-docs-portal.py. Do not hand-edit the generated output; edit this file
and re-run the generator.

## Overview

**IMPLEMENTAUDIT.md** is a repo and a skill. The repo hosts the canonical definition;
the skill — invoked as `/implementaudit` — is a method for turning audit findings,
handoffs, checklists, reviews, goals, tasks, gaps, and implementation plans into
bounded, verified repository changes.

It is **not** a release bot, package publisher, provenance system, or generic
autonomous build loop. It is an *audit-governed implementation* runtime: every
mutation happens under an audit object, and no claim is stronger than its evidence.

:::info
**Core Invariant.** Every finding closes. No orphan items. No unsafe actions. No proof
claim without evidence.
:::

The `.md` in the name is branding and lineage, not a required root behavior file.
The actual skill definition lives in `skills/SKILL.md`.

## Quick Start

New to IMPLEMENTAUDIT? Here is the minimal path to your first governed implementation.

### 1. Understand the small loop

Every run follows the same spine:

    Input artifact → live repo inspection → owner/source patch → Smoke A/B → final audit

### 2. Try a simple invocation

With the skill installed, invoke it from your agent:

    /implementaudit < audit-findings.md
    /implementaudit implement these findings
    /goal using /implementaudit, close the findings in AUDIT.md

### 3. Understand the basic workflow

- **Read** the input — it must be a recognizable audit artifact.
- **Go to Gemba** — inspect the real files, not summaries.
- **Smoke A** — run baseline checks before any change.
- **Patch** — fix the owner/source, not the nearest symptom.
- **Smoke B** — verify post-change checks against the baseline.
- **Close** — every item reaches `done`, `changed`, `blocked`, `deferred`, or `unverified`.

### 4. Default authorization stance

:::warning
**No commit. No push. No tag. No release. No publication. No provenance.**
Each action requires separate explicit authorization.
:::

## Install

### Codex

Manual copy from a repo checkout:

    mkdir -p ~/.codex/skills/implementaudit
    cp -R skills/* ~/.codex/skills/implementaudit/

Or from a release asset with checksum verification:

    bash scripts/build-release-asset.sh
    bash scripts/install-codex-from-release.sh \
      --asset dist/IMPLEMENTAUDIT.skill \
      --checksum dist/CHECKSUMS.txt \
      --codex-home "$HOME/.codex" \
      --version 0.2.8

### Claude Code

Use the host's current plugin instructions with `.claude-plugin/plugin.json` as
package metadata. For public clone/plugin setup, an HTTPS repo URL is usually the
simplest path.

:::info
**No auto-update.** A locally installed skill does not update automatically when the
GitHub repo has a new release. Repeat the install step after each release.
:::

### v0.2.8.0 release

Release `v0.2.8.0` is live. Tag at commit `d2829a4`. The release asset
`IMPLEMENTAUDIT.skill` includes a `CHECKSUMS.txt` — a SHA-256 checksum manifest for
local integrity verification. No signatures, attestations, SBOMs, or provenance
chains are claimed. Pages docs are live.

## For New Users

You have just discovered IMPLEMENTAUDIT.md. This is the right place to start.

### card: First encounter?

Start with the Overview and Quick Start to understand what IMPLEMENTAUDIT is and how
to run your first audit-governed implementation.

- [→ Overview](#overview)
- [→ Quick Start](#quick-start)

### card: Ready to install?

Skip to the Install section for Codex and Claude Code setup instructions. No auto-update mechanism exists — repeat the install step on each release.

- [→ Install](#install)

### card: Confused by the terminology?

IMPLEMENTAUDIT uses precise vocabulary. The Terminology table explains every key term.

- [→ Terminology](#terminology)

## For Agents and Operators

You will be invoking `/implementaudit` in your AI coding tool. Here is what you need.

### card: Invocation reference

Four modes: direct governance, embedded governance, goal synthesis, and governed
casual-build intake. Know the difference before you invoke.

- [→ Invocation Modes](#invocation-modes)
- [→ Usage Examples](#usage-examples)

### card: Execution gates

Eight non-skippable gates. Each must pass before the next. If a gate fails — Andon.

- [→ Execution Spine](#execution-spine)
- [→ Operating Method](#operating-method)

### card: Optional tooling

Graphify and ActiveGraph are optional for ordinary user runs. Orientation and custody
evidence only — not proof.

- [→ Optional Tooling](#optional-tooling)

## For Auditors and Maintainers

You need the evidence trail. Here is where to look.

### card: Audit dogfood history

Trace every IMPLEMENTAUDIT run against this repo: what was proven, what was deferred,
what remained unverified.

- [→ Evidence and Audit Trail](#evidence-and-audit-trail)

### card: Diagram sources

Mermaid source files for the execution spine, invocation modes, and tooling
architecture flowcharts.

- [→ Repo Layout](#repo-layout)

### card: Canonical sources

`skills/SKILL.md` is the canonical method. `AGENTS.md` is the authoritative project
doc. `CHANGELOG.md` records milestone evidence.

- [→ Repo Layout](#repo-layout)
- [→ Safety and Boundaries](#safety-and-boundaries)

## Terminology

IMPLEMENTAUDIT uses a precise vocabulary. Understanding these terms is essential.

| Term | Meaning |
|---|---|
| `AUDIT.md` | An audit input or evidence-implementation artifact that drives a run: file, attachment, pasted audit, handoff, checklist, review, goal, task, gap, or plan. |
| `tdqyq-audit-object` | The audit-as-noun: the evidence-bearing record for the run — scope, owner/source, claims, changed files, checks, closure state. |
| `ydqyq-audit-action` | The audit-as-verb: inspects, classifies, verifies, authorizes or rejects mutation, or closes findings against the audit object. |
| Owner/source | The canonical file, schema, script, fixture, or doc that owns a claim or behavior. Patch this, not the nearest symptom. |
| Gemba | Go to the real place of work. Inspect actual files, not summaries. |
| Smoke A / Smoke B | Baseline pre-change verification (A) then post-change comparison (B). Regressions trigger the regression protocol. |
| Andon | A visible blocker or abnormality signal. Surface it immediately — do not hide failure. |
| Hansei | Structured reflection after gaps, regressions, false passes, or failures: gap, cause, countermeasure, follow-up. |
| 5 Whys | Trace symptoms to root cause. Symptom, condition, system gap, prevention gap, systemic countermeasure. |
| Kaizen | Durable process improvement folded back into the standard. |
| Greenfield | A new artifact with no established owner/source — must define acceptance, rollback, and evidence first. |
| Brownfield | Existing repo surface — inspect owner/source, tests, generated artifacts, and regression surface before change. |
| Graphify | Optional terrain/orientation aid for finding where to inspect. Not proof. Absence is not an error. |
| ActiveGraph | Optional custody/event evidence substrate for recording gate passages. Not correctness proof. Absence is not an error. |

## Invocation Modes

`/implementaudit` has four invocation shapes, depending on what the user supplies:

### Direct Governance

The user supplies a concrete audit, handoff, checklist, review, or bounded plan. The
run applies audit-closure hygiene directly.

    /implementaudit implement this handoff
    /implementaudit close the findings in this review
    /implementaudit work through this checklist

### Embedded Governance

The user already supplied a host goal/task/plan, especially inside `/goal`.
IMPLEMENTAUDIT wraps that target with its gates — it does **not** print a second
`/goal`.

    /goal using /implementaudit, close the findings in AUDIT.md

### Goal Synthesis

The user supplies an idea, gap, or incomplete target. IMPLEMENTAUDIT performs Gemba,
phase planning, and self-critique, then produces a bounded handoff.

    /implementaudit audit this repo state and give me the next best implementation goal

### Governed Casual-Build Intake

The user supplies natural-language repo-build intent. IMPLEMENTAUDIT synthesizes a
bounded audit object before routing to the appropriate work mode — greenfield,
brownfield, or mixed.

    /implementaudit make the docs portal generated by CI and prove it is fresh
    /implementaudit fix this repo bug safely and keep the diff reviewable

:::info
**Embedded governance:** In embedded governance mode, the outer `/goal` owns the
audit object. IMPLEMENTAUDIT acts inside it and must not emit a nested `/goal`.
:::

## Execution Spine

The execution spine is the non-skippable sequence of gates. Each gate must pass
before moving to the next, or work stops with an **Andon**.

| Gate | Purpose | Halt Condition |
|---|---|---|
| 0. Safety | Read repo instructions, safety defaults, authorization gates, and AGENTS.md conflict rules. | STOP if unsafe, unauthorized, or contradicts repo policy. |
| 1. Input | Confirm input is a valid audit artifact. | STOP if empty, malformed, or not an audit artifact. |
| 2. Pre-flight | Detect optional tooling, confirm write access, ownership, constraints. | STOP unless every required pre-flight item passes. |
| 3. Smoke A | Run baseline before mutation. Classify pre-existing failures. | Do not mutate until baseline is recorded. |
| 4. Implement | P0 to P1 to P2. Patch owner/source. Guard scope creep. | Andon if owner/source unclear or dependency blocks. |
| 5. Smoke B | Compare post-change checks against Smoke A. | Regression protocol if any passing check now fails. |
| 6. Trace | Preserve causal chain in ledger, commit body (if authorized), AGENTS.md. | Do not finalize until authorization boundaries are explicit. |
| 7. Self-check | Quality bar before final response. | Fix, revert, or mark unverified before final. |

:::danger
**Non-negotiable.** These are gates, not a table of contents. Each row must pass
before the next. If a gate fails, stop and Andon — do not pretend the run is
complete.
:::

## Operating Method

IMPLEMENTAUDIT combines core disciplines from Lean and quality management:

### PDCA

Plan the smallest safe change. Do it. Check the evidence. Act — standardize
if successful, revise if not.

### Gemba

Go to the real place of work. Inspect actual files, not summaries or memory.

### Smoke Before Claim

Every behavior claim must be tagged with its evidence type. Never upgrade
static evidence into live proof.

### Andon

Surface blockers, failures, unclear ownership, or unsafe conditions immediately.
Do not hide failure. Do not mark "mostly done."

### Hansei

Reflect after gaps, regressions, false passes, or failures. Name the gap,
cause, countermeasure, and follow-up.

### 5 Whys

Trace symptoms to root cause: why the symptom, why the condition, why the
system allowed it, why it was not caught earlier, what prevents recurrence.

### Plan Closure

Every item maps to exactly one terminal status: `done`, `changed`, `blocked`,
`deferred`, or `unverified`. No item may remain open.

## Usage Examples

### Basic invocations

    /implementaudit < audit.md
    /implementaudit implement these findings
    /implementaudit --onboard-tools
    /goal using /implementaudit, close the findings in AUDIT.md
    /implementaudit make the CI workflow generate and deploy the docs portal

Natural-language requests such as *implement these findings*, *act on this audit*,
*close these items*, or *work through this handoff* also invoke the method.

### Worked flow

    Finding: README describes behavior that no longer matches skills/SKILL.md.

    Owner/source: skills/SKILL.md defines behavior.
                  README.md is derived public documentation.

    Smoke A: Read skills/SKILL.md and README.md.
             Run git diff --check.

    Countermeasure: Patch README.md to match live source of truth.

    Smoke B: Run git diff --check -- README.md.
             Manually inspect evidence wording.

    Closure: Status changed. Commit only if authorized.

## Default Behavior

The default small-audit mode works on one artifact. It:

- Validates the input is a recognizable audit artifact
- Normalizes findings into a ledger
- Classifies items: **P0** (blocks goal or safety), **P1** (named in audit), **P2** (nice-to-have), **OWNER DECISION**, **DEFERRED**, **OUT OF SCOPE**
- Processes in P0 to P1 to P2 order
- Patches owner/source, not nearest symptom
- Requires evidence for every claim
- Closes every item terminally — zero open items at final response

## Routing

IMPLEMENTAUDIT classifies work before mutation:

| Route | What it means |
|---|---|
| Greenfield | New artifact with no established owner/source. Define scope, acceptance criteria, rollback, and evidence plan first. |
| Brownfield | Existing repo surface. Inspect owner/source, tests, generated artifacts, regression surface before change. |
| Mixed | New artifact inside an established repo. Brownfield outer inspection first, then greenfield intake for the new part. |
| Governed casual-build | Natural-language repo-build intent. IMPLEMENTAUDIT synthesizes a bounded audit object before routing to greenfield, brownfield, or mixed. |

## Repo Layout

Understanding the repo structure helps you find the right owner/source.

    /
    ├── AGENTS.md                  Authoritative project doc
    ├── README.md                  Public-facing overview + install
    ├── CHANGELOG.md               Milestone notes (Keep a Changelog)
    ├── CONTRIBUTING.md            Short onboarding
    ├── skills/                    Canonical skill source
    │   ├── SKILL.md               The /implementaudit method
    │   ├── references/            Progressive-disclosure reference docs
    │   ├── scripts/               Planner-executed bash helpers
    │   └── templates/             .IMPLEMENTAUDIT/ file templates
    ├── scripts/                   Repo validation and release tools
    ├── tests/                     Shell test suites
    ├── docs/                      Local docs (you are here)
    │   ├── portal/onboarding.md   Portal content source
    │   ├── diagrams/              Mermaid source for README flows
    │   └── audits/                Dogfood audit ledgers
    ├── fixtures/                  Test fixtures
    ├── .claude-plugin/            Plugin manifest
    └── .github/workflows/         CI validation

## Optional Tooling

IMPLEMENTAUDIT can optionally integrate with two external tools to strengthen the
audit trail. Both are optional — the skill is fully usable without either.

**Graphify** provides terrain and orientation evidence. It can help identify
owner/source candidates, dependency paths, and stale assumptions. It is not proof.
Live files remain source of truth. Graphify absence is not an error.

For ordinary user runs, Graphify is optional. For IMPLEMENTAUDIT self-maintenance
runs, Graphify is canonical when available and authorized — orientation evidence from
the skill's own repo supports faster Gemba. Graphify output is never a substitute
for live-file inspection.

**ActiveGraph** provides chain-of-custody evidence for audit gate passages. It is not
correctness proof. ActiveGraph absence is not an error.

For ordinary user runs, ActiveGraph is optional. For IMPLEMENTAUDIT self-maintenance
runs, ActiveGraph is canonical when available and authorized — custody events support
the Capability Ledger and audit history.

:::success
**Markdown fallback is first-class.** When Graphify and ActiveGraph are absent,
IMPLEMENTAUDIT uses ordinary Gemba, ordinary ledgers, and ordinary final reporting.
This is not a degraded mode.
:::

:::warning
**No install without authorization.** Tool installation, indexing, event-store setup,
and export are separate explicit gates — not implied by an audit run.
:::

## Safety and Boundaries

IMPLEMENTAUDIT has firm safety defaults. These actions require **explicit
authorization**:

- Commit
- Push
- Tag
- Publish
- Create or update releases
- Delete data
- Alter credentials or secrets
- Rewrite history
- Commit raw diagnostic outputs
- Hand-edit generated artifacts when a source generator exists
- Claim proof without evidence

Authorization is **per-action**:

- Local commit authorization does not imply push authorization
- Push authorization does not imply tag, release, or publication authorization
- Release authorization does not imply provenance authorization

:::danger
**AGENTS.md conflicts are OWNER DECISION.** If an audit finding contradicts
AGENTS.md, the agent must surface the conflict as a human decision — not silently
choose which instruction wins.
:::

## What It Does Not Do

`/implementaudit` is not:

- **A release bot.** It does not push, tag, or publish without explicit gates.
- **A provenance system.** `CHECKSUMS.txt` is a SHA-256 integrity manifest — not a signature, attestation, SBOM, or provenance chain.
- **A package publisher.** Release assets require separate authorization.
- **Generic autonomous-build software.** Every mutation happens under an audit contract.
- **A framework-specific tool.** It is repo-generic and does not assume language, CI, or release conventions.
- **A marketplace auto-updater.** No marketplace publication or update has occurred. Local copied skills do not update from GitHub releases automatically.

:::info
**The authoritative reference is always `skills/SKILL.md` and `AGENTS.md` in the
repo.** When in doubt, go to Gemba — read the source.
:::

## Evidence and Audit Trail

Audit ledgers and diagram sources live in repo-local docs for maintainers and
reviewers.

The v0.2.8.0 adaptation lane closed G1-G7 comparator-advantage gaps. G5 (per-phase
continuity writeback) is classified **STRENGTHENED** — the v0.2.6.0 PROTOCOL loop
base existed, and v0.2.8.0 added the `IMPLEMENTAUDIT_CONTINUITY_SAVED` marker with 6
required fields, a bounded writeback options table, ActiveGraph custody path, Graphify
terrain-update request, and a 34-check continuity test suite.

- `docs/audits/INDEX.md` — full dogfood history index
- `docs/audits/v0.2.8.0-adaptation.md` — v0.2.8.0 gap closure ledger
- `docs/audits/v0.2.8.0-docs-portal-ci-onboarding.md` — docs portal CI and onboarding audit
- `docs/diagrams/` — Mermaid source for execution spine and tooling diagrams

## Audit Status

Current release and deployment facts for v0.2.8.0:

- **Version:** v0.2.8.0
- **Plugin manifest:** 0.2.8
- **Release:** Live. Tag `v0.2.8.0` at commit `d2829a4`. Release asset `IMPLEMENTAUDIT.skill` with `CHECKSUMS.txt` (SHA-256 checksum manifest). No signatures, attestations, SBOMs, or provenance chains are claimed.
- **Pages docs:** Live and verified.
- **G5 status:** STRENGTHENED — v0.2.6.0 PROTOCOL loop base; v0.2.8.0 added `IMPLEMENTAUDIT_CONTINUITY_SAVED` marker, bounded writeback options, and 34-check continuity test suite.
- **Graphify:** Optional sidecar for user runs; canonical for self-maintenance runs when available and authorized. Orientation evidence only — not proof.
- **ActiveGraph:** Optional sidecar for user runs; canonical for self-maintenance runs when available and authorized. Custody evidence only — not correctness proof.
- **Marketplace:** No marketplace publication or update has occurred.
- **Comparator note:** No all-domain obsolescence claim is made. Each tool has its own scope and users.
